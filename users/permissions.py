from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """Allow access only to patients."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "patient"
        )


class IsDoctor(BasePermission):
    """Allow access only to doctors."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "doctor"
        )


class IsAdmin(BasePermission):
    """Allow access only to admins."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.user_type == "admin" or request.user.is_staff)
        )


class IsLabTech(BasePermission):
    """Allow access only to lab technicians."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "lab_tech"
        )


class IsOwnerOrDoctor(BasePermission):
    """
    Allow if user is the patient themselves or a doctor.
    Expects the view to have a get_patient_user_id() method
    or the object to have a user/patient field.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True

        if request.user.user_type == "doctor":
            # Doctor must have an appointment relationship with the patient
            from appointments.models import Appointment

            patient_id = None
            if hasattr(obj, "patient_id"):
                patient_id = obj.patient_id
            elif hasattr(obj, "user_id"):
                patient_id = obj.user_id
            elif hasattr(obj, "patient") and hasattr(obj.patient, "pk"):
                patient_id = obj.patient.pk

            if patient_id is None:
                return False
            return Appointment.objects.filter(
                doctor=request.user.doctor_profile,
                patient_id=patient_id,
            ).exists()

        # Check if patient owns this resource
        if hasattr(obj, "user_id"):
            return obj.user_id == request.user.id
        if hasattr(obj, "patient_id"):
            return obj.patient_id == request.user.id
        if hasattr(obj, "patient") and hasattr(obj.patient, "user_id"):
            return obj.patient.user_id == request.user.id
        return False
