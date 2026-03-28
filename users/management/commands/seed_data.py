"""
Management command to seed the database with demo data.

Usage:
    python manage.py seed_data

Creates:
    - 1 Admin user
    - 1 Doctor with full schedule
    - 2 Patient accounts
    - 1 Lab Technician
    - Sample appointments, lab orders, medications, and medical records
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework.authtoken.models import Token
from datetime import date, time, timedelta
import json

from users.models import User, Patient, Doctor


class Command(BaseCommand):
    help = "Seed the database with demo users and sample data for development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete ALL existing data before seeding (destructive!).",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing existing data..."))
            User.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding database..."))

        # ─── 1. Admin ───
        admin = self._create_user(
            email="admin@curova.com",
            password="Admin@123",
            first_name="System",
            last_name="Admin",
            user_type="admin",
        )

        # ─── 2. Doctor ───
        doc_user = self._create_user(
            email="doctor@curova.com",
            password="Doctor@123",
            first_name="Sarah",
            last_name="Ahmed",
            user_type="doctor",
        )
        if doc_user and not Doctor.objects.filter(user=doc_user).exists():
            Doctor.objects.create(
                user=doc_user,
                license_number="DOC-2024-001",
                specialization="cardiology",
                years_experience=12,
                bio="Experienced cardiologist specializing in preventive cardiology and heart failure management.",
                consultation_fee=150.00,
                available_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
                working_hours_start=time(9, 0),
                working_hours_end=time(17, 0),
                slot_duration=30,
            )
            self.stdout.write(f"  → Doctor profile created for {doc_user.email}")

        # ─── 3. Patients ───
        patient1 = self._create_user(
            email="patient@curova.com",
            password="Patient@123",
            first_name="John",
            last_name="Doe",
            user_type="patient",
        )
        if patient1 and not Patient.objects.filter(user=patient1).exists():
            Patient.objects.create(
                user=patient1,
                date_of_birth=date(1990, 5, 15),
                gender="male",
                blood_type="O+",
                address="123 Health Street, Medical City",
                emergency_contact_name="Jane Doe",
                emergency_contact_phone="+1234567890",
                allergies=["Penicillin", "Peanuts"],
                chronic_conditions=["Hypertension"],
            )
            self.stdout.write(f"  → Patient profile created for {patient1.email}")

        patient2 = self._create_user(
            email="patient2@curova.com",
            password="Patient@123",
            first_name="Alice",
            last_name="Smith",
            user_type="patient",
        )
        if patient2 and not Patient.objects.filter(user=patient2).exists():
            Patient.objects.create(
                user=patient2,
                date_of_birth=date(1985, 8, 22),
                gender="female",
                blood_type="A+",
                address="456 Wellness Avenue, Care Town",
            )
            self.stdout.write(f"  → Patient profile created for {patient2.email}")

        # ─── 4. Lab Technician ───
        lab_tech = self._create_user(
            email="labtech@curova.com",
            password="LabTech@123",
            first_name="Sarah",
            last_name="Johnson",
            user_type="lab_tech",
        )

        # ─── 5. Sample Data ───
        self._create_sample_data(doc_user, patient1, patient2)

        # ─── Summary ───
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("═" * 55))
        self.stdout.write(self.style.SUCCESS("  Database seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("═" * 55))
        self.stdout.write("")
        self.stdout.write("  Login Credentials:")
        self.stdout.write("  ─────────────────────────────────────────")
        self.stdout.write(f"  Admin:       admin@curova.com     / Admin@123")
        self.stdout.write(f"  Doctor:      doctor@curova.com    / Doctor@123")
        self.stdout.write(f"  Patient 1:   patient@curova.com   / Patient@123")
        self.stdout.write(f"  Patient 2:   patient2@curova.com  / Patient@123")
        self.stdout.write(f"  Lab Tech:    labtech@curova.com   / LabTech@123")
        self.stdout.write("")

    def _create_user(self, email, password, first_name, last_name, user_type):
        """Create a user if they don't already exist. Returns the user."""
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"  ⏩ User {email} already exists, skipping.")
            return User.objects.get(email=email)

        username = email.split("@")[0]
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
        )
        Token.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(f"  ✔ Created {user_type}: {email}"))
        return user

    def _create_sample_data(self, doctor_user, patient1_user, patient2_user):
        """Create sample appointments, lab orders, etc."""
        from appointments.models import Appointment
        from lab_tests.models import LabTest
        from medications.models import Medication

        doctor = Doctor.objects.filter(user=doctor_user).first()
        patient1 = Patient.objects.filter(user=patient1_user).first()
        patient2 = Patient.objects.filter(user=patient2_user).first()
        if not doctor or not patient1:
            return

        today = timezone.now().date()

        # ── Appointments ──
        if Appointment.objects.count() == 0:
            appointments_data = [
                # Past completed
                {"patient": patient1, "doctor": doctor, "date": today - timedelta(days=14),
                 "time": time(10, 0), "status": "completed", "reason": "Annual cardiac checkup"},
                {"patient": patient1, "doctor": doctor, "date": today - timedelta(days=7),
                 "time": time(14, 0), "status": "completed", "reason": "Follow-up on blood work"},
                # Upcoming
                {"patient": patient1, "doctor": doctor, "date": today + timedelta(days=2),
                 "time": time(9, 30), "status": "confirmed", "reason": "Blood pressure monitoring"},
                {"patient": patient1, "doctor": doctor, "date": today + timedelta(days=7),
                 "time": time(11, 0), "status": "scheduled", "reason": "Routine cardiac follow-up"},
            ]
            if patient2:
                appointments_data.append(
                    {"patient": patient2, "doctor": doctor, "date": today + timedelta(days=3),
                     "time": time(10, 30), "status": "scheduled", "reason": "Initial consultation"}
                )
            for a in appointments_data:
                Appointment.objects.create(
                    patient=a["patient"], doctor=a["doctor"],
                    appointment_date=a["date"], appointment_time=a["time"],
                    status=a["status"], reason=a["reason"],
                )
            self.stdout.write(f"  → Created {len(appointments_data)} sample appointments")

        # ── Lab Tests ──
        if LabTest.objects.count() == 0:
            lab_data = [
                {"patient": patient1, "doctor": doctor, "name": "Complete Blood Count (CBC)",
                 "category": "blood", "priority": "routine", "status": "processing",
                 "notes": "Routine annual screening"},
                {"patient": patient1, "doctor": doctor, "name": "Lipid Panel",
                 "category": "blood", "priority": "routine", "status": "ordered",
                 "notes": "Check cholesterol levels"},
                {"patient": patient1, "doctor": doctor, "name": "Chest X-Ray",
                 "category": "imaging", "priority": "routine", "status": "ordered",
                 "notes": "Pre-operative clearance"},
            ]
            for lab in lab_data:
                LabTest.objects.create(
                    patient=lab["patient"], doctor=lab["doctor"],
                    test_name=lab["name"], test_category=lab["category"],
                    priority=lab["priority"], status=lab["status"],
                    clinical_notes=lab["notes"],
                )
            self.stdout.write(f"  → Created {len(lab_data)} sample lab orders")

        # ── Medications ──
        if Medication.objects.count() == 0:
            meds_data = [
                {"patient": patient1, "doctor": doctor, "name": "Lisinopril",
                 "dosage": "10mg", "frequency": "Once daily", "is_active": True,
                 "notes": "Take in the morning with water"},
                {"patient": patient1, "doctor": doctor, "name": "Aspirin",
                 "dosage": "81mg", "frequency": "Once daily", "is_active": True,
                 "notes": "Take with food"},
            ]
            for m in meds_data:
                Medication.objects.create(
                    patient=m["patient"], prescribed_by=m["doctor"],
                    name=m["name"], dosage=m["dosage"],
                    frequency=m["frequency"], is_active=m["is_active"],
                    notes=m["notes"],
                    start_date=today - timedelta(days=30),
                )
            self.stdout.write(f"  → Created {len(meds_data)} sample medications")
