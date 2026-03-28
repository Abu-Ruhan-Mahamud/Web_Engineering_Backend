from django.contrib import admin
from .models import MedicalDocument


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "document_type", "file_size", "created_at")
    list_filter = ("document_type",)
