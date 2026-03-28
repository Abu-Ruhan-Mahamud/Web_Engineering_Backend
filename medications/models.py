from django.db import models


class Medication(models.Model):
    """Current medication tracking for a patient (mutable)."""

    patient = models.ForeignKey(
        "users.Patient",
        on_delete=models.PROTECT,
        related_name="medications",
    )
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, help_text='e.g. "Twice daily"')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    prescribed_by = models.ForeignKey(
        "users.Doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescribed_medications",
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medications"
        ordering = ["-is_active", "-created_at"]
        indexes = [
            models.Index(fields=["is_active"], name="idx_med_active"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=models.F("start_date")),
                name="medication_end_after_start",
            ),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({status}) - {self.patient}"


class MedicationReminder(models.Model):
    """Reminder settings for a medication."""

    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="reminders",
    )
    reminder_time = models.TimeField()
    label = models.CharField(max_length=100, blank=True, default="")
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medication_reminders"
        ordering = ["reminder_time"]

    def __str__(self):
        return f"Reminder: {self.medication.name} at {self.reminder_time}"
