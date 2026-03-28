import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.conf import settings as django_settings
from django.utils import timezone

from .models import User, Patient, Doctor
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer,
    DoctorSelfUpdateSerializer,
    DoctorListSerializer,
)
from .permissions import IsPatient, IsDoctor

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new patient account."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token": token.key,
            "user": UserSerializer(user, context={'request': request}).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """Login and return auth token."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token": token.key,
            "user": UserSerializer(user, context={'request': request}).data,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_view(request):
    """Authenticate with a Google ID token.

    Accepts { "credential": "<Google ID token>" } from the frontend
    Google Identity Services flow.  Verifies the token against Google,
    finds-or-creates a patient User, and returns a DRF auth token.
    """
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    credential = request.data.get("credential", "")
    if not credential:
        return Response(
            {"detail": "Google credential token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    google_client_id = getattr(django_settings, "GOOGLE_CLIENT_ID", None)
    if not google_client_id:
        logger.error("GOOGLE_CLIENT_ID is not configured in settings.")
        return Response(
            {"detail": "Google login is not configured on this server."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Verify the token with Google
    try:
        idinfo = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            google_client_id,
        )
    except ValueError as exc:
        logger.warning("Google token verification failed: %s", exc)
        return Response(
            {"detail": "Invalid Google token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    email = idinfo.get("email", "").lower()
    if not email or not idinfo.get("email_verified"):
        return Response(
            {"detail": "Google account email is not verified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Find or create the user
    user = User.objects.filter(email=email).first()
    created = False

    if user is None:
        # Auto-register as a patient
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")
        username = email.split("@")[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=None,          # unusable password — social-only
            user_type="patient",
        )
        user.set_unusable_password()
        user.save()
        Patient.objects.create(user=user)
        created = True

    if not user.is_active:
        return Response(
            {"detail": "This account has been deactivated."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Optionally update profile picture from Google
    picture_url = idinfo.get("picture", "")

    token, _ = Token.objects.get_or_create(user=user)

    resp_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(
        {
            "token": token.key,
            "user": UserSerializer(user, context={'request': request}).data,
            "created": created,
        },
        status=resp_status,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout — delete the user's auth token."""
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    """
    Delete the current user's account (GDPR-compliant soft delete).
    
    Personal data is pseudonymized, medical records retained per healthcare standards:
    - Article 17(3) GDPR: Exception for legal claims and public health
    - HIPAA: Medical records retention is legal requirement
    - Real healthcare systems (Epic, NHS, Cerner): Never hard-delete medical records
    
    Approach:
    - Pseudonymize: Clear email, phone, profile picture, replace name with ID
    - Retain: All medical records, prescriptions, appointments (for continuity of care)
    - Deactivate: Disable login, delete auth token
    """
    user = request.user
    user_id = user.id
    
    # Step 1: Pseudonymize personal data (GDPR Article 89 compliant)
    user.first_name = f"Patient_{user_id}"
    user.last_name = ""
    user.email = f"deleted_user_{user_id}@deleted.local"
    user.phone = ""
    
    # Clear profile picture
    if user.profile_picture:
        try:
            user.profile_picture.delete(save=False)
        except Exception:
            pass
    
    # Step 2: Deactivate user account (prevent login)
    user.is_active = False
    user.save()
    
    # Step 3: Delete auth token (revoke access)
    try:
        user.auth_token.delete()
    except Exception:
        pass
    
    # Step 4: Create deletion audit record (optional — for transparency)
    try:
        from django.utils import timezone
        logger.info(
            f"User account deleted (pseudonymized): User ID {user_id}, "
            f"Time: {timezone.now().isoformat()}"
        )
    except Exception:
        pass
    
    return Response(
        {
            "detail": "Your account has been deactivated. "
            "Medical records are retained per healthcare regulations for continuity of care. "
            "Contact support if you need further assistance."
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Return or update the current authenticated user's info.

    GET  — return user data.
    PUT  — update editable fields (currently only phone and profile_picture).
    """
    if request.method == "PUT":
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(UserSerializer(request.user, context={'request': request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Change the current user's password."""
    current_password = request.data.get("current_password", "")
    new_password = request.data.get("new_password", "")
    confirm_password = request.data.get("confirm_password", "")

    if not all([current_password, new_password, confirm_password]):
        return Response(
            {"detail": "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not request.user.check_password(current_password):
        return Response(
            {"current_password": ["Current password is incorrect."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_password:
        return Response(
            {"confirm_password": ["New passwords do not match."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    try:
        validate_password(new_password, request.user)
    except ValidationError as e:
        return Response(
            {"new_password": list(e.messages)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    request.user.set_password(new_password)
    request.user.save()

    # Rotate token: delete old and issue new
    Token.objects.filter(user=request.user).delete()
    new_token = Token.objects.create(user=request.user)

    return Response({
        "detail": "Password changed successfully.",
        "token": new_token.key,
    })


# ── Patient Profile ────────────────────────────────────────────────


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsPatient])
def patient_profile_view(request):
    """GET or update the current patient's profile."""
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        return Response(
            {"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        user_data = UserSerializer(request.user, context={'request': request}).data
        profile_data = PatientProfileSerializer(patient).data
        return Response({**user_data, "profile": profile_data})

    # PUT — update user fields + patient profile fields
    user = request.user
    user_fields = ["first_name", "last_name", "phone", "profile_picture"]
    user_update_data = {}
    for field in user_fields:
        if field in request.data:
            user_update_data[field] = request.data[field]
    
    if user_update_data:
        user_serializer = UserSerializer(user, data=user_update_data, partial=True, context={'request': request})
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

    profile_serializer = PatientProfileSerializer(
        patient, data=request.data, partial=True
    )
    profile_serializer.is_valid(raise_exception=True)
    profile_serializer.save()

    user_data = UserSerializer(user, context={'request': request}).data
    profile_data = PatientProfileSerializer(patient).data
    return Response({**user_data, "profile": profile_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPatient])
def patient_dashboard_stats(request):
    """Return summary stats for the patient dashboard."""
    patient = request.user.patient_profile
    today = timezone.now().date()

    from appointments.models import Appointment
    from medical.models import MedicalRecord
    from medications.models import Medication

    total_appointments = Appointment.objects.filter(patient=patient).count()
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=today,
        status__in=["scheduled", "confirmed"],
    ).count()
    active_medications = Medication.objects.filter(
        patient=patient, is_active=True
    ).count()
    medical_records = MedicalRecord.objects.filter(patient=patient).count()

    return Response(
        {
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming_appointments,
            "active_medications": active_medications,
            "medical_records": medical_records,
        }
    )


# ── Doctor List (public for booking) ──────────────────────────────


@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_list_view(request):
    """List all active doctors, optionally filtered by specialization."""
    qs = Doctor.objects.filter(user__is_active=True).select_related("user")

    specialization = request.query_params.get("specialization")
    if specialization:
        qs = qs.filter(specialization=specialization)

    search = request.query_params.get("search")
    if search:
        from django.db.models import Q

        qs = qs.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(specialization__icontains=search)
        )

    serializer = DoctorListSerializer(qs, many=True)
    return Response(serializer.data)


# ── Doctor Dashboard & Profile ─────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_dashboard_stats(request):
    """Return summary stats for the doctor dashboard."""
    doctor = request.user.doctor_profile
    today = timezone.now().date()

    from appointments.models import Appointment

    total_patients = (
        Appointment.objects.filter(doctor=doctor)
        .values("patient")
        .distinct()
        .count()
    )
    todays_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today,
    ).exclude(status="cancelled").count()
    pending_reports = Appointment.objects.filter(
        doctor=doctor,
        status="completed",
    ).exclude(medical_record__isnull=False).count()
    weekly_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today - timezone.timedelta(days=today.weekday()),
        appointment_date__lte=today + timezone.timedelta(days=6 - today.weekday()),
    ).exclude(status="cancelled").count()

    return Response({
        "todays_appointments": todays_appointments,
        "total_patients": total_patients,
        "pending_reports": pending_reports,
        "weekly_appointments": weekly_appointments,
    })


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_profile_view(request):
    """GET or update the current doctor's profile."""
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return Response(
            {"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        user_data = UserSerializer(request.user, context={'request': request}).data
        profile_data = DoctorProfileSerializer(doctor).data
        return Response({**user_data, "profile": profile_data})

    # PUT — restricted to doctor-safe fields only.
    # Credential fields (license_number, specialization, years_experience)
    # and legal-name fields (first_name, last_name) are admin-managed.
    user = request.user
    if "phone" in request.data:
        user.phone = request.data["phone"]
        user.save()

    profile_serializer = DoctorSelfUpdateSerializer(
        doctor, data=request.data, partial=True
    )
    profile_serializer.is_valid(raise_exception=True)
    profile_serializer.save()

    user_data = UserSerializer(user, context={'request': request}).data
    profile_data = DoctorProfileSerializer(doctor).data
    return Response({**user_data, "profile": profile_data})


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_schedule_view(request):
    """GET or update the doctor's schedule/availability.

    PUT behaviour (conflict-aware):
    1. Compute which future non-cancelled appointments would become invalid
       under the proposed schedule (day removed, or outside new working hours).
    2. If conflicts exist AND `force` is not set, return 409 with the list.
    3. If `force=true` is sent, auto-cancel those appointments, notify patients,
       then save the new schedule.
    """
    doctor = request.user.doctor_profile

    if request.method == "GET":
        return Response({
            "available_days": doctor.available_days,
            "working_hours_start": str(doctor.working_hours_start),
            "working_hours_end": str(doctor.working_hours_end),
            "slot_duration": doctor.slot_duration,
        })

    # ── PUT — update schedule ──────────────────────────────────────

    from datetime import datetime as dt_cls
    from appointments.models import Appointment
    from notifications.helpers import create_notification

    new_days = request.data.get("available_days", doctor.available_days)
    new_start = request.data.get("working_hours_start", str(doctor.working_hours_start))
    new_end = request.data.get("working_hours_end", str(doctor.working_hours_end))
    new_slot = request.data.get("slot_duration", doctor.slot_duration)
    force = request.data.get("force", False)

    # Parse times for comparison
    def parse_time(t):
        """Accept '09:00', '09:00:00', or '9:00 AM' formats."""
        for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p"):
            try:
                return dt_cls.strptime(str(t).strip(), fmt).time()
            except ValueError:
                continue
        return doctor.working_hours_start  # fallback

    parsed_start = parse_time(new_start)
    parsed_end = parse_time(new_end)

    # Normalise day names to lowercase
    new_days_lower = [d.lower() for d in new_days]

    # Day-of-week mapping: Python weekday() → name
    DOW = {0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
           4: "friday", 5: "saturday", 6: "sunday"}

    # Find future active appointments that conflict
    today = timezone.localdate()
    future_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        status__in=["scheduled", "confirmed"],
    ).select_related("patient__user")

    conflicts = []
    for apt in future_appointments:
        day_name = DOW[apt.appointment_date.weekday()]
        day_removed = day_name not in new_days_lower
        outside_hours = apt.appointment_time < parsed_start or apt.appointment_time >= parsed_end

        if day_removed or outside_hours:
            reason = "day no longer available" if day_removed else "outside new working hours"
            conflicts.append({
                "id": apt.id,
                "patient_name": apt.patient.user.get_full_name(),
                "date": str(apt.appointment_date),
                "time": str(apt.appointment_time),
                "status": apt.status,
                "reason": reason,
            })

    # If conflicts exist and not forced, return them for confirmation
    if conflicts and not force:
        return Response({
            "has_conflicts": True,
            "conflicts": conflicts,
            "message": f"{len(conflicts)} upcoming appointment(s) would be affected by this schedule change.",
        }, status=status.HTTP_409_CONFLICT)

    # Force mode or no conflicts — apply changes
    if conflicts and force:
        conflict_ids = [c["id"] for c in conflicts]
        affected_apts = Appointment.objects.filter(id__in=conflict_ids).select_related("patient__user")

        for apt in affected_apts:
            apt.status = "cancelled"
            apt.notes = (apt.notes + "\n[Auto-cancelled: doctor schedule change]").strip()
            apt.save(update_fields=["status", "notes", "updated_at"])

            create_notification(
                recipient=apt.patient.user,
                title="Appointment Cancelled",
                message=(
                    f"Your appointment with Dr. {doctor.user.get_full_name()} "
                    f"on {apt.appointment_date.strftime('%b %d, %Y')} at "
                    f"{apt.appointment_time.strftime('%I:%M %p')} has been cancelled "
                    f"due to a schedule change. Please rebook at your convenience."
                ),
                notification_type="appointment",
                related_object_type="appointment",
                related_object_id=apt.id,
            )

    # Save the new schedule
    doctor.available_days = new_days_lower
    doctor.working_hours_start = parsed_start
    doctor.working_hours_end = parsed_end
    doctor.slot_duration = new_slot
    doctor.save()

    return Response({
        "available_days": doctor.available_days,
        "working_hours_start": str(doctor.working_hours_start),
        "working_hours_end": str(doctor.working_hours_end),
        "slot_duration": doctor.slot_duration,
        "cancelled_count": len(conflicts) if force else 0,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_patients_view(request):
    """List unique patients who have appointments with this doctor."""
    doctor = request.user.doctor_profile

    from appointments.models import Appointment

    patient_ids = (
        Appointment.objects.filter(doctor=doctor)
        .values_list("patient_id", flat=True)
        .distinct()
    )
    patients = Patient.objects.filter(user_id__in=patient_ids).select_related("user")

    data = []
    for p in patients:
        last_visit = (
            Appointment.objects.filter(doctor=doctor, patient=p, status="completed")
            .order_by("-appointment_date")
            .first()
        )
        data.append({
            "id": p.user_id,
            "first_name": p.user.first_name,
            "last_name": p.user.last_name,
            "email": p.user.email,
            "phone": p.user.phone,
            "gender": p.gender,
            "date_of_birth": p.date_of_birth,
            "blood_type": p.blood_type,
            "allergies": p.allergies,
            "chronic_conditions": p.chronic_conditions,
            "last_visit": last_visit.appointment_date if last_visit else None,
            "profile_picture": p.user.profile_picture.url if p.user.profile_picture else None,
        })
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_patient_detail_view(request, patient_id):
    """Full detail for a patient, including their records/medications/appointments with this doctor."""
    doctor = request.user.doctor_profile

    try:
        patient = Patient.objects.select_related("user").get(user_id=patient_id)
    except Patient.DoesNotExist:
        return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

    from appointments.models import Appointment
    from medical.models import MedicalRecord
    from medications.models import Medication
    from medical.serializers import MedicalRecordSerializer
    from appointments.serializers import AppointmentSerializer

    # Security: verify doctor has at least one appointment with this patient
    if not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
        return Response(
            {"detail": "You have no appointments with this patient."},
            status=status.HTTP_403_FORBIDDEN,
        )

    appointments_qs = Appointment.objects.filter(
        doctor=doctor, patient=patient
    ).order_by("-appointment_date")

    records_qs = (
        MedicalRecord.objects.filter(doctor=doctor, patient=patient)
        .select_related("doctor__user", "appointment")
        .prefetch_related("prescriptions")
        .order_by("-created_at")
    )

    medications_qs = Medication.objects.filter(patient=patient, is_active=True)

    patient_data = {
        "id": patient.user_id,
        "first_name": patient.user.first_name,
        "last_name": patient.user.last_name,
        "email": patient.user.email,
        "phone": patient.user.phone,
        "gender": patient.gender,
        "date_of_birth": patient.date_of_birth,
        "blood_type": patient.blood_type,
        "address": patient.address,
        "allergies": patient.allergies,
        "chronic_conditions": patient.chronic_conditions,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "profile_picture": patient.user.profile_picture.url if patient.user.profile_picture else None,
        "created_at": patient.user.created_at,
    }

    return Response({
        "patient": patient_data,
        "appointments": AppointmentSerializer(appointments_qs, many=True).data,
        "medical_records": MedicalRecordSerializer(records_qs, many=True).data,
        "medications": [
            {
                "id": m.pk,
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "is_active": m.is_active,
                "start_date": m.start_date,
            }
            for m in medications_qs
        ],
    })
