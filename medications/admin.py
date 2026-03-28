from django.contrib import admin
from .models import Medication, MedicationReminder


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("name", "patient", "dosage", "frequency", "is_active")
    list_filter = ("is_active",)


@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ("medication", "reminder_time", "is_enabled")
