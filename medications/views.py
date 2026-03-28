from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsPatient
from .models import Medication
from .serializers import MedicationSerializer
from curova_backend.pagination import paginate_queryset


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPatient])
def medication_list(request):
    """List the current patient's medications. Supports ?active=true filter."""
    patient = request.user.patient_profile
    qs = Medication.objects.filter(patient=patient).select_related(
        "prescribed_by__user"
    )

    active_param = request.query_params.get("active")
    if active_param == "true":
        qs = qs.filter(is_active=True)
    elif active_param == "false":
        qs = qs.filter(is_active=False)

    return paginate_queryset(qs, request, MedicationSerializer)


# ─── Medication Reminders ─────────────────────────────────────


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsPatient])
def reminder_list(request, medication_id):
    """
    GET  — list reminders for a specific medication.
    POST — create a new reminder for a medication.
    """
    try:
        medication = Medication.objects.get(
            pk=medication_id, patient=request.user.patient_profile
        )
    except Medication.DoesNotExist:
        return Response(
            {"detail": "Medication not found."}, status=drf_status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        reminders = medication.reminders.all()
        return Response(MedicationReminderSerializer(reminders, many=True).data)

    # POST — create reminder
    serializer = MedicationReminderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(medication=medication)
        return Response(serializer.data, status=drf_status.HTTP_201_CREATED)
    return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsPatient])
def reminder_detail(request, medication_id, reminder_id):
    """
    PATCH  — update a reminder (toggle is_enabled, change time/label).
    DELETE — remove a reminder.
    """
    try:
        reminder = MedicationReminder.objects.select_related("medication").get(
            pk=reminder_id,
            medication_id=medication_id,
            medication__patient=request.user.patient_profile,
        )
    except MedicationReminder.DoesNotExist:
        return Response(
            {"detail": "Reminder not found."}, status=drf_status.HTTP_404_NOT_FOUND
        )

    if request.method == "DELETE":
        reminder.delete()
        return Response(status=drf_status.HTTP_204_NO_CONTENT)

    # PATCH
    serializer = MedicationReminderSerializer(
        reminder, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=drf_status.HTTP_400_BAD_REQUEST)
