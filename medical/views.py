from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsDoctor

from .models import MedicalRecord
from .serializers import CreateMedicalRecordSerializer, MedicalRecordSerializer
from curova_backend.pagination import paginate_queryset
from notifications.helpers import create_notification


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def medical_record_list(request):
    """List medical records for the current patient (or doctor's patients)."""
    if request.user.user_type == "patient":
        qs = MedicalRecord.objects.filter(patient=request.user.patient_profile)
    elif request.user.user_type == "doctor":
        qs = MedicalRecord.objects.filter(doctor=request.user.doctor_profile)
    else:
        qs = MedicalRecord.objects.none()

    qs = qs.select_related("doctor__user", "appointment").prefetch_related(
        "prescriptions"
    )

    return paginate_queryset(qs, request, MedicalRecordSerializer)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def medical_record_detail(request, pk):
    """Retrieve a single medical record."""
    try:
        record = (
            MedicalRecord.objects.select_related("doctor__user", "appointment")
            .prefetch_related("prescriptions")
            .get(pk=pk)
        )
    except MedicalRecord.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # Access control
    user = request.user
    has_access = (
        (user.user_type == "patient" and record.patient_id == user.pk)
        or (user.user_type == "doctor" and record.doctor_id == user.pk)
        or user.user_type == "admin"
    )
    if not has_access:
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    return Response(MedicalRecordSerializer(record).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def create_medical_record(request):
    """Create a new medical record (doctor only). Accepts nested prescriptions."""
    serializer = CreateMedicalRecordSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        record = serializer.save()

        # Notify the patient about the new medical record
        create_notification(
            recipient=record.patient.user,
            title="New Medical Record",
            message=f"Dr. {record.doctor.user.get_full_name()} has created a new medical record: {record.diagnosis[:80]}.",
            notification_type="prescription",
            related_object_type="medical_record",
            related_object_id=record.id,
        )

        # Return the full serialized record
        return Response(
            MedicalRecordSerializer(record).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
