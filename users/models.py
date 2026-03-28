from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based user types."""

    class UserType(models.TextChoices):
        PATIENT = "patient", "Patient"
        DOCTOR = "doctor", "Doctor"
        ADMIN = "admin", "Admin"
        LAB_TECH = "lab_tech", "Lab Technician"

    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.PATIENT,
    )
    phone = models.CharField(max_length=20, blank=True, default="")
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_type"], name="idx_user_type"),
            models.Index(fields=["is_active"], name="idx_user_active"),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"


class Patient(models.Model):
    """Patient profile — 1:1 extension of User."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        primary_key=True,
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        blank=True,
        default="",
    )
    blood_type = models.CharField(
        max_length=5,
        choices=[
            ("A+", "A+"),
            ("A-", "A-"),
            ("B+", "B+"),
            ("B-", "B-"),
            ("AB+", "AB+"),
            ("AB-", "AB-"),
            ("O+", "O+"),
            ("O-", "O-"),
        ],
        blank=True,
        default="",
    )
    address = models.TextField(blank=True, default="")
    emergency_contact_name = models.CharField(max_length=150, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default="")
    allergies = models.JSONField(default=list, blank=True)
    chronic_conditions = models.JSONField(default=list, blank=True)
    medical_history = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "patients"

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class Doctor(models.Model):
    """Doctor profile — 1:1 extension of User."""

    class Specialization(models.TextChoices):
        GENERAL = "general_practice", "General Practice"
        CARDIOLOGY = "cardiology", "Cardiology"
        DERMATOLOGY = "dermatology", "Dermatology"
        NEUROLOGY = "neurology", "Neurology"
        ORTHOPEDICS = "orthopedics", "Orthopedics"
        PEDIATRICS = "pediatrics", "Pediatrics"
        PSYCHIATRY = "psychiatry", "Psychiatry"
        SURGERY = "surgery", "Surgery"
        OPHTHALMOLOGY = "ophthalmology", "Ophthalmology"
        ENT = "ent", "ENT"
        GYNECOLOGY = "gynecology", "Gynecology"
        UROLOGY = "urology", "Urology"
        ONCOLOGY = "oncology", "Oncology"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        primary_key=True,
    )
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(
        max_length=30,
        choices=Specialization.choices,
        default=Specialization.GENERAL,
    )
    years_experience = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True, default="")
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    available_days = models.JSONField(
        default=list,
        blank=True,
        help_text='List of available days, e.g. ["monday","tuesday"]',
    )
    working_hours_start = models.TimeField(default="09:00")
    working_hours_end = models.TimeField(default="17:00")
    slot_duration = models.PositiveIntegerField(
        default=30,
        help_text="Appointment slot duration in minutes",
    )

    class Meta:
        db_table = "doctors"

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialization_display()})"
