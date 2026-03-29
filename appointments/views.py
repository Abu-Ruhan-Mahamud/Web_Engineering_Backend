from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Appointment
from .serializers import AppointmentSerializer, CreateAppointmentSerializer
from users.permissions import IsPatient, IsDoctor
from curova_backend.pagination import paginate_queryset
from notifications.helpers import create_notification


# ─── Auto-cleanup of stale past appointments ──────────────────

def _cleanup_stale_appointments():
    """Transition stale past appointments on API access (lazy cleanup).

    Rules:
    - Past "scheduled" (never confirmed) → "no_show"
    - Past "confirmed"                   → "completed"
    """
    today = timezone.now().date()

    # Past "scheduled" → "no_show"
    no_show_count = Appointment.objects.filter(
        appointment_date__lt=today,
        status="scheduled",
    ).update(status="no_show")

    # Past "confirmed" → "completed"
    completed_count = Appointment.objects.filter(
        appointment_date__lt=today,
        status="confirmed",
    ).update(status="completed")

    return no_show_count, completed_count


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booked_slots(request):
    """Return already-booked time slots for a doctor on a given date.
    GET /api/appointments/booked-slots/?doctor_id=X&date=YYYY-MM-DD
    """
    doctor_id = request.query_params.get("doctor_id")
    date_str = request.query_params.get("date")
    if not doctor_id or not date_str:
        return Response(
            {"detail": "doctor_id and date query params are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    booked = (
        Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date_str,
        )
        .exclude(status="cancelled")
        .values_list("appointment_time", flat=True)
    )
    # Return as list of "HH:MM" strings
    return Response(
        {"booked_slots": [t.strftime("%H:%M") for t in booked]}
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    """
    GET  — list appointments for the current user (patient or doctor).
    POST — book a new appointment (patient only).
    """
    if request.method == "GET":
        # Lazy cleanup: auto-transition stale past appointments
        _cleanup_stale_appointments()

        print(f"[DEBUG] appointment_list GET - User: {request.user}, Type: {request.user.user_type}")

        if request.user.user_type == "patient":
            qs = Appointment.objects.filter(patient=request.user.patient_profile)
            print(f"[DEBUG] Patient query - found {qs.count()} appointments")
        elif request.user.user_type == "doctor":
            try:
                doctor_profile = request.user.doctor_profile
                print(f"[DEBUG] Doctor profile found: {doctor_profile}")
                qs = Appointment.objects.filter(doctor=doctor_profile)
                print(f"[DEBUG] Doctor query - doctor_profile={doctor_profile.id}, found {qs.count()} appointments")
            except Exception as e:
                print(f"[DEBUG] ERROR getting doctor_profile: {e}")
                qs = Appointment.objects.none()
        else:
            print(f"[DEBUG] Unknown user type: {request.user.user_type}")
            qs = Appointment.objects.none()

        qs = qs.select_related(
            "doctor__user", "patient__user"
        )

        # Optional filters
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
            print(f"[DEBUG] Applied status filter: {status_filter}")

        upcoming = request.query_params.get("upcoming")
        if upcoming == "true":
            today = timezone.now().date()
            qs = qs.filter(
                appointment_date__gte=today,
                status__in=["scheduled", "confirmed"],
            ).order_by("appointment_date", "appointment_time")
            print(f"[DEBUG] Applied upcoming filter for date {today}")

        print(f"[DEBUG] Final queryset count: {qs.count()}")
        result = paginate_queryset(qs, request, AppointmentSerializer)
        print(f"[DEBUG] Paginated result type: {type(result)}, data keys: {result.data.keys() if hasattr(result, 'data') else 'N/A'}")
        return result

    # POST — patient books appointment
    if request.user.user_type != "patient":
        return Response(
            {"detail": "Only patients can book appointments."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CreateAppointmentSerializer(
        data=request.data,
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    appointment = serializer.save()

    # Notify the doctor about the new booking
    create_notification(
        recipient=appointment.doctor.user,
        title="New Appointment Booked",
        message=f"{appointment.patient.user.get_full_name()} booked an appointment on {appointment.appointment_date.strftime('%b %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')}.",
        notification_type="appointment",
        related_object_type="appointment",
        related_object_id=appointment.id,
    )

    return Response(
        AppointmentSerializer(appointment).data,
        status=status.HTTP_201_CREATED,
    )


# ─── Notification helpers ─────────────────────────────────────

_STATUS_LABELS = {
    "confirmed": "Confirmed",
    "cancelled": "Cancelled",
    "completed": "Completed",
    "in_progress": "In Progress",
    "no_show": "No Show",
    "rescheduled": "Rescheduled",
}


def _send_appointment_status_notification(appointment, old_status, new_status, acting_user):
    """Send a notification to the *other* party when an appointment status changes."""
    date_str = appointment.appointment_date.strftime("%b %d, %Y")
    time_str = appointment.appointment_time.strftime("%I:%M %p")
    label = _STATUS_LABELS.get(new_status, new_status)

    if acting_user.user_type == "patient":
        # Patient acted → notify doctor
        recipient = appointment.doctor.user
        title = f"Appointment {label}"
        message = f"{appointment.patient.user.get_full_name()} {label.lower()} their appointment on {date_str} at {time_str}."
    elif acting_user.user_type == "doctor":
        # Doctor acted → notify patient
        recipient = appointment.patient.user
        doctor_name = f"Dr. {appointment.doctor.user.get_full_name()}"
        title = f"Appointment {label}"
        message = f"{doctor_name} has {label.lower()} your appointment on {date_str} at {time_str}."
    else:
        # Admin acted → notify both
        doctor_name = f"Dr. {appointment.doctor.user.get_full_name()}"
        patient_name = appointment.patient.user.get_full_name()
        for recipient, msg in [
            (appointment.patient.user, f"Your appointment on {date_str} at {time_str} with {doctor_name} has been {label.lower()} by an administrator."),
            (appointment.doctor.user, f"The appointment on {date_str} at {time_str} with {patient_name} has been {label.lower()} by an administrator."),
        ]:
            create_notification(
                recipient=recipient,
                title=f"Appointment {label}",
                message=msg,
                notification_type="appointment",
                related_object_type="appointment",
                related_object_id=appointment.id,
            )
        return  # already sent both

    create_notification(
        recipient=recipient,
        title=title,
        message=message,
        notification_type="appointment",
        related_object_type="appointment",
        related_object_id=appointment.id,
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    """GET or update a single appointment."""
    try:
        appointment = Appointment.objects.select_related(
            "doctor__user", "patient__user"
        ).get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # Access control
    user = request.user
    is_owner = (user.user_type == "patient" and appointment.patient_id == user.pk) or (
        user.user_type == "doctor" and appointment.doctor_id == user.pk
    )
    if not is_owner and user.user_type != "admin":
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    if request.method == "GET":
        return Response(AppointmentSerializer(appointment).data)

    # PATCH — update status / notes
    allowed_fields = {"status", "notes"}
    update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

    # Role-based status transition enforcement
    if "status" in update_data:
        new_status = update_data["status"]
        current_status = appointment.status
        PATIENT_TRANSITIONS = {
            "scheduled": ["cancelled"],
            "confirmed": ["cancelled"],
        }
        DOCTOR_TRANSITIONS = {
            "scheduled": ["confirmed", "cancelled"],
            "confirmed": ["in_progress", "completed", "cancelled", "no_show"],
            "in_progress": ["completed"],
        }
        if user.user_type == "patient":
            allowed_statuses = PATIENT_TRANSITIONS.get(current_status, [])
            if new_status not in allowed_statuses:
                return Response(
                    {"detail": f"Patients cannot change status from '{current_status}' to '{new_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif user.user_type == "doctor":
            allowed_statuses = DOCTOR_TRANSITIONS.get(current_status, [])
            if new_status not in allowed_statuses:
                return Response(
                    {"detail": f"Invalid status transition from '{current_status}' to '{new_status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Admin can perform any status transition

    old_status = appointment.status
    serializer = AppointmentSerializer(appointment, data=update_data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    # Notify the other party about status changes
    new_status = update_data.get("status")
    if new_status and new_status != old_status:
        _send_appointment_status_notification(appointment, old_status, new_status, user)

    return Response(serializer.data)
