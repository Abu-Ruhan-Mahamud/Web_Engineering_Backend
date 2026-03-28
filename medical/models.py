from django.db import models


class MedicalRecord(models.Model):
    """Medical record created by a doctor after an appointment."""

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        related_name="medical_record",
        null=True,
        blank=True,
    )
    patient = models.ForeignKey(
        "users.Patient",
        on_delete=models.PROTECT,
        related_name="medical_records",
    )
    doctor = models.ForeignKey(
        "users.Doctor",
        on_delete=models.PROTECT,
        related_name="medical_records",
    )
    chief_complaint = models.TextField(blank=True, default="")
    diagnosis = models.JSONField(
        default=list, blank=True, help_text="List of diagnoses"
    )
    symptoms = models.JSONField(default=list, blank=True, help_text="List of symptoms")
    examination_notes = models.TextField(blank=True, default="")
    treatment_plan = models.TextField(blank=True, default="")
    vitals = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"blood_pressure": "120/80", "heart_rate": 72, "temperature": 98.6}',
    )
    additional_notes = models.TextField(blank=True, default="")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="idx_medrec_created"),
        ]

    def __str__(self):
        return f"Record for {self.patient} on {self.created_at.date()}"


class Prescription(models.Model):
    """Immutable prescription linked to a medical record. Audit trail.

    NOTE: Prescriptions are intentionally separate from the Medication model
    (medications app).  Prescriptions capture what was prescribed at a specific
    visit and are immutable.  Medications track what a patient is *currently*
    taking and can be updated.  A future enhancement could auto-create a
    Medication entry when a new Prescription is saved.
    """

    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, help_text='e.g. "Twice daily"')
    duration = models.CharField(
        max_length=100, blank=True, default="", help_text='e.g. "7 days"'
    )
    instructions = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "prescriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"
