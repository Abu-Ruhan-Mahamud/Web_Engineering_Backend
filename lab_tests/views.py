from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsDoctor, IsLabTech

from .models import LabTest, LabTestResult
from .serializers import (
    CreateLabTestSerializer,
    LabTestSerializer,
    UploadLabResultSerializer,
)
from curova_backend.pagination import paginate_queryset
from notifications.helpers import create_notification


# ─── Lab Test CRUD ────────────────────────────────────────────


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def lab_test_list(request):
    """
    GET: List lab tests visible to the current user.
      - Patient: own tests
      - Doctor: tests they ordered
      - Lab Tech: tests with status in (ordered, sample_collected, processing)
      - Admin: all
    POST: Doctor creates a new lab test order.
    """
    if request.method == "GET":
        user = request.user
        if user.user_type == "patient":
            qs = LabTest.objects.filter(patient=user.patient_profile)
        elif user.user_type == "doctor":
            qs = LabTest.objects.filter(doctor=user.doctor_profile)
        elif user.user_type == "lab_tech":
            qs = LabTest.objects.filter(
                status__in=[
                    LabTest.Status.ORDERED,
                    LabTest.Status.SAMPLE_COLLECTED,
                    LabTest.Status.PROCESSING,
                ]
            )
        elif user.user_type == "admin":
            qs = LabTest.objects.all()
        else:
            qs = LabTest.objects.none()

        # Optional status filter
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Optional patient filter (for doctors viewing specific patient)
        patient_filter = request.query_params.get("patient")
        if patient_filter:
            qs = qs.filter(patient_id=patient_filter)

        qs = qs.select_related("patient__user", "doctor__user", "reviewed_by__user")

        return paginate_queryset(qs, request, LabTestSerializer)

    # POST — doctor creates order
    if request.user.user_type != "doctor":
        return Response(
            {"detail": "Only doctors can order lab tests."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CreateLabTestSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        lab_test = serializer.save()

        # Notify patient about the new lab test order
        create_notification(
            recipient=lab_test.patient.user,
            title="Lab Test Ordered",
            message=f"Dr. {lab_test.doctor.user.get_full_name()} has ordered a {lab_test.test_name} ({lab_test.get_priority_display()}).",
            notification_type="lab_result",
            related_object_type="lab_test",
            related_object_id=lab_test.id,
        )

        return Response(
            LabTestSerializer(lab_test).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def lab_test_detail(request, pk):
    """Retrieve or update a single lab test."""
    try:
        lab_test = (
            LabTest.objects.select_related(
                "patient__user", "doctor__user", "reviewed_by__user"
            )
            .get(pk=pk)
        )
    except LabTest.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    # Access control
    has_access = (
        (user.user_type == "patient" and lab_test.patient_id == user.pk)
        or (user.user_type == "doctor" and lab_test.doctor_id == user.pk)
        or user.user_type == "lab_tech"
        or user.user_type == "admin"
    )
    if not has_access:
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    if request.method == "GET":
        return Response(LabTestSerializer(lab_test).data)

    # PATCH — lab tech updates status, doctor reviews
    if user.user_type == "lab_tech":
        new_status = request.data.get("status")
        allowed = [
            LabTest.Status.SAMPLE_COLLECTED,
            LabTest.Status.PROCESSING,
        ]
        if new_status and new_status in [s.value for s in allowed]:
            lab_test.status = new_status
            lab_test.save(update_fields=["status"])
            return Response(LabTestSerializer(lab_test).data)
        return Response(
            {"detail": "Lab techs can only update status to sample_collected or processing."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.user_type == "doctor":
        new_status = request.data.get("status")
        if new_status == LabTest.Status.REVIEWED:
            lab_test.status = LabTest.Status.REVIEWED
            lab_test.reviewed_at = timezone.now()
            lab_test.reviewed_by = user.doctor_profile
            lab_test.save(update_fields=["status", "reviewed_at", "reviewed_by"])

            # Notify patient that doctor reviewed their results
            create_notification(
                recipient=lab_test.patient.user,
                title="Lab Results Reviewed",
                message=f"Dr. {user.get_full_name()} has reviewed your {lab_test.test_name} results.",
                notification_type="lab_result",
                related_object_type="lab_test",
                related_object_id=lab_test.id,
            )

            return Response(LabTestSerializer(lab_test).data)
        return Response(
            {"detail": "Doctors can only set status to reviewed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"detail": "You cannot modify this lab test."},
        status=status.HTTP_403_FORBIDDEN,
    )


# ─── Lab Test Results ─────────────────────────────────────────


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def lab_test_result(request, pk):
    """
    GET: Retrieve the result for a lab test (patient, doctor, lab_tech, admin).
    POST: Lab tech uploads a result.
    """
    try:
        lab_test = LabTest.objects.select_related(
            "patient__user", "doctor__user"
        ).get(pk=pk)
    except LabTest.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    has_access = (
        (user.user_type == "patient" and lab_test.patient_id == user.pk)
        or (user.user_type == "doctor" and lab_test.doctor_id == user.pk)
        or user.user_type == "lab_tech"
        or user.user_type == "admin"
    )
    if not has_access:
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )

    if request.method == "GET":
        try:
            result = lab_test.result
        except LabTestResult.DoesNotExist:
            return Response(
                {"detail": "No result uploaded yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        from .serializers import LabTestResultSerializer

        return Response(LabTestResultSerializer(result).data)

    # POST — lab tech uploads result
    if user.user_type != "lab_tech":
        return Response(
            {"detail": "Only lab technicians can upload results."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if hasattr(lab_test, "result"):
        return Response(
            {"detail": "Result already uploaded. Use PATCH to update."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = UploadLabResultSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(lab_test=lab_test, uploaded_by=user)
        # Auto-advance status
        lab_test.status = LabTest.Status.RESULTS_AVAILABLE
        lab_test.completed_at = timezone.now()
        lab_test.save(update_fields=["status", "completed_at"])

        # Notify patient that results are ready
        create_notification(
            recipient=lab_test.patient.user,
            title="Lab Results Available",
            message=f"Results for your {lab_test.test_name} are now available. Please check your lab results page.",
            notification_type="lab_result",
            related_object_type="lab_test",
            related_object_id=lab_test.id,
        )
        # Notify the ordering doctor
        create_notification(
            recipient=lab_test.doctor.user,
            title="Lab Results Ready for Review",
            message=f"{lab_test.test_name} results for {lab_test.patient.user.get_full_name()} are ready for your review.",
            notification_type="lab_result",
            related_object_type="lab_test",
            related_object_id=lab_test.id,
        )

        return Response(
            LabTestSerializer(lab_test).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsLabTech])
def lab_test_result_update(request, pk):
    """Lab tech updates an existing result."""
    try:
        lab_test = LabTest.objects.get(pk=pk)
    except LabTest.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        result = lab_test.result
    except LabTestResult.DoesNotExist:
        return Response(
            {"detail": "No result to update."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = UploadLabResultSerializer(result, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(LabTestSerializer(lab_test).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
