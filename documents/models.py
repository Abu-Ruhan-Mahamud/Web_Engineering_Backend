import os
from django.db import models
from django.core.validators import FileExtensionValidator


def document_upload_path(instance, filename):
    """Upload to media/documents/<patient_id>/<filename>."""
    return os.path.join("documents", str(instance.patient_id), filename)


class MedicalDocument(models.Model):
    """Uploaded medical documents (PDFs, images)."""

    class DocumentType(models.TextChoices):
        PRESCRIPTION = "prescription", "Prescription"
        DISCHARGE_SUMMARY = "discharge_summary", "Discharge Summary"
        INSURANCE = "insurance", "Insurance"
        REFERRAL_LETTER = "referral_letter", "Referral Letter"
        VACCINATION_RECORD = "vaccination_record", "Vaccination Record"
        MEDICAL_HISTORY = "medical_history", "Medical History"
        OTHER = "other", "Other"

    patient = models.ForeignKey(
        "users.Patient",
        on_delete=models.PROTECT,
        related_name="documents",
    )
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])
        ],
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    uploaded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "medical_documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["document_type"], name="idx_doc_type"),
            models.Index(fields=["-created_at"], name="idx_doc_created"),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
