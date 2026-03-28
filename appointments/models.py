from django.db import models
from django.conf import settings


class Appointment(models.Model):
    """Appointment between a patient and a doctor."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"
        RESCHEDULED = "rescheduled", "Rescheduled"

    patient = models.ForeignKey(
        "users.Patient",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        "users.Doctor",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    reason = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-appointment_date", "-appointment_time"]
        indexes = [
            models.Index(fields=["status"], name="idx_appointment_status"),
            models.Index(fields=["appointment_date"], name="idx_appointment_date"),
            models.Index(fields=["appointment_date", "status"], name="idx_appt_date_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "appointment_date", "appointment_time"],
                name="unique_doctor_slot",
            ),
        ]

    def __str__(self):
        return (
            f"Appointment: {self.patient} with {self.doctor} "
            f"on {self.appointment_date} at {self.appointment_time}"
        )
