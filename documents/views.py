from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import MedicalDocument
from .serializers import MedicalDocumentSerializer, UploadDocumentSerializer
from users.permissions import IsPatient
from curova_backend.pagination import paginate_queryset


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def document_list(request):
    """
    GET  — list documents for the current patient.
    POST — upload a new document (patient only).
    """
    if request.method == "GET":
        if request.user.user_type == "patient":
            qs = MedicalDocument.objects.filter(patient=request.user.patient_profile)
        elif request.user.user_type == "doctor":
            from appointments.models import Appointment

            patient_ids = (
                Appointment.objects.filter(doctor=request.user.doctor_profile)
                .values_list("patient_id", flat=True)
                .distinct()
            )
            qs = MedicalDocument.objects.filter(patient_id__in=patient_ids)
        else:
            qs = MedicalDocument.objects.none()

        doc_type = request.query_params.get("type")
        if doc_type:
            qs = qs.filter(document_type=doc_type)

        return paginate_queryset(
            qs, request, MedicalDocumentSerializer, context={"request": request}
        )

    # POST — patient uploads a document
    if request.user.user_type != "patient":
        return Response(
            {"detail": "Only patients can upload documents."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = UploadDocumentSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    doc = serializer.save()
    return Response(
        MedicalDocumentSerializer(doc, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def document_detail(request, pk):
    """GET or DELETE a specific document."""
    try:
        doc = MedicalDocument.objects.get(pk=pk)
    except MedicalDocument.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # Access control
    if request.user.user_type == "patient" and doc.patient_id != request.user.pk:
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )
    elif request.user.user_type == "doctor":
        # Doctor can only access documents of patients they have appointments with
        from appointments.models import Appointment

        if not Appointment.objects.filter(
            doctor=request.user.doctor_profile, patient=doc.patient
        ).exists():
            return Response(
                {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

    if request.method == "GET":
        return Response(
            MedicalDocumentSerializer(doc, context={"request": request}).data
        )

    # DELETE
    if request.user.user_type != "patient" or doc.patient_id != request.user.pk:
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )
    doc.file.delete(save=False)
    doc.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
