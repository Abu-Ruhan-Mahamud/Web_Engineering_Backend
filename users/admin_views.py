"""Admin-only API views for user management, system stats, and appointments."""

import csv
from datetime import timedelta

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer
from medications.models import Medication
from medical.models import MedicalRecord

from .admin_serializers import (
    AdminDoctorCreateSerializer,
    AdminUserDetailSerializer,
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
)
from .models import User
from .permissions import IsAdmin
from curova_backend.pagination import paginate_queryset


# ─── System Stats ────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_stats_view(request):
    """Return system-wide statistics for the admin dashboard."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # User counts by type
    user_qs = User.objects.all()
    total_users = user_qs.count()
    user_counts = dict(
        user_qs.values_list("user_type").annotate(c=Count("id")).values_list("user_type", "c")
    )

    # Appointment stats
    appt_qs = Appointment.objects.all()
    total_appointments = appt_qs.count()
    appt_by_status = dict(
        appt_qs.values_list("status").annotate(c=Count("id")).values_list("status", "c")
    )

    # Recent activity (last 30 days)
    recent_users = user_qs.filter(created_at__gte=thirty_days_ago).count()
    recent_appointments = appt_qs.filter(created_at__gte=thirty_days_ago).count()

    # Additional counts
    total_records = MedicalRecord.objects.count()
    active_medications = Medication.objects.filter(is_active=True).count()

    return Response(
        {
            "total_users": total_users,
            "users_by_type": {
                "patient": user_counts.get("patient", 0),
                "doctor": user_counts.get("doctor", 0),
                "admin": user_counts.get("admin", 0),
                "lab_tech": user_counts.get("lab_tech", 0),
            },
            "total_appointments": total_appointments,
            "appointments_by_status": {
                "scheduled": appt_by_status.get("scheduled", 0),
                "confirmed": appt_by_status.get("confirmed", 0),
                "in_progress": appt_by_status.get("in_progress", 0),
                "completed": appt_by_status.get("completed", 0),
                "cancelled": appt_by_status.get("cancelled", 0),
                "no_show": appt_by_status.get("no_show", 0),
                "rescheduled": appt_by_status.get("rescheduled", 0),
            },
            "total_medical_records": total_records,
            "active_medications": active_medications,
            "recent_users_30d": recent_users,
            "recent_appointments_30d": recent_appointments,
        }
    )


# ─── User Management ────────────────────────────────────────


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_list_view(request):
    """GET: list all users (with filters). POST: create a new doctor/admin."""
    if request.method == "GET":
        qs = User.objects.all()

        # Filters
        user_type = request.query_params.get("user_type")
        if user_type in ("patient", "doctor", "admin", "lab_tech"):
            qs = qs.filter(user_type=user_type)

        is_active = request.query_params.get("is_active")
        if is_active in ("true", "false"):
            qs = qs.filter(is_active=(is_active == "true"))

        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(username__icontains=search)
            )

        qs = qs.order_by("-created_at")
        return paginate_queryset(qs, request, AdminUserListSerializer)

    # POST — create doctor or admin
    serializer = AdminDoctorCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        AdminUserDetailSerializer(user).data, status=status.HTTP_201_CREATED
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_detail_view(request, user_id):
    """GET: full user detail. PATCH: update user fields."""
    try:
        user = User.objects.select_related("patient_profile", "doctor_profile").get(
            pk=user_id
        )
    except User.DoesNotExist:
        return Response(
            {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response(AdminUserDetailSerializer(user).data)

    # PATCH — prevent self-deactivation
    if user.pk == request.user.pk and "is_active" in request.data and not request.data["is_active"]:
        return Response(
            {"detail": "You cannot deactivate your own account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user.refresh_from_db()
    return Response(AdminUserDetailSerializer(user).data)


# ─── Appointments (Admin overview) ──────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_appointment_list_view(request):
    """Return all appointments for admin with optional filters."""
    qs = Appointment.objects.select_related(
        "patient__user", "doctor__user"
    ).all()

    # Filters
    appt_status = request.query_params.get("status")
    valid_statuses = [c[0] for c in Appointment.Status.choices]
    if appt_status in valid_statuses:
        qs = qs.filter(status=appt_status)

    doctor_id = request.query_params.get("doctor")
    if doctor_id:
        qs = qs.filter(doctor__user_id=doctor_id)

    patient_id = request.query_params.get("patient")
    if patient_id:
        qs = qs.filter(patient__user_id=patient_id)

    date_from = request.query_params.get("date_from")
    if date_from:
        qs = qs.filter(appointment_date__gte=date_from)

    date_to = request.query_params.get("date_to")
    if date_to:
        qs = qs.filter(appointment_date__lte=date_to)

    search = request.query_params.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(patient__user__first_name__icontains=search)
            | Q(patient__user__last_name__icontains=search)
            | Q(doctor__user__first_name__icontains=search)
            | Q(doctor__user__last_name__icontains=search)
        )

    qs = qs.order_by("-appointment_date", "-appointment_time")
    return paginate_queryset(qs, request, AppointmentSerializer)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_appointment_export_view(request):
    """Export all appointments as CSV."""
    qs = Appointment.objects.select_related(
        "patient__user", "doctor__user"
    ).order_by("-appointment_date", "-appointment_time")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="appointments_export.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Date",
            "Time",
            "Patient",
            "Patient Email",
            "Doctor",
            "Doctor Specialization",
            "Status",
            "Reason",
            "Notes",
            "Created",
        ]
    )

    for appt in qs:
        writer.writerow(
            [
                appt.id,
                appt.appointment_date,
                appt.appointment_time,
                appt.patient.user.get_full_name(),
                appt.patient.user.email,
                f"Dr. {appt.doctor.user.get_full_name()}",
                appt.doctor.get_specialization_display(),
                appt.get_status_display(),
                appt.reason,
                appt.notes,
                appt.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    return response
