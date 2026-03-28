from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Unified notification model for all in-app notifications.
    Created automatically when key events occur (appointment changes,
    lab results ready, prescriptions created, medication reminders, etc.).
    """

    class NotificationType(models.TextChoices):
        APPOINTMENT = "appointment", "Appointment"
        MEDICATION = "medication", "Medication"
        LAB_RESULT = "lab_result", "Lab Result"
        PRESCRIPTION = "prescription", "Prescription"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    is_read = models.BooleanField(default=False)

    # Optional link to a related object (appointment, lab test, etc.)
    related_object_type = models.CharField(max_length=50, blank=True, default="")
    related_object_id = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.recipient.email}"
