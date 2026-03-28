from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from users.models import User, Patient, Doctor
from medications.models import Medication, MedicationReminder
from medical.models import MedicalRecord
from appointments.models import Appointment
from time import time

class Command(BaseCommand):
    help = "Populate database with demo patient profiles and medical data"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting demo data population...\n")
        
        # Create demo patients
        patients_data = [
            {
                "first_name": "Abu",
                "last_name": "Ruhan Mahamud",
                "email": "abu.ruhan@curova.com",
                "phone": "+880-1700-000001",
                "date_of_birth": date(1985, 5, 15),
                "gender": "male",
                "blood_type": "B+",
                "address": "123 Dhaka Street, Mirpur, Dhaka 1200",
                "emergency_contact_name": "Fatima Ruhan",
                "emergency_contact_phone": "+880-1700-000002",
                "allergies": ["Penicillin", "Shellfish"],
                "chronic_conditions": ["Hypertension", "Type 2 Diabetes"],
                "medications": [
                    {"name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "notes": "For blood pressure control"},
                    {"name": "Metformin", "dosage": "500mg", "frequency": "Twice daily", "notes": "For diabetes management"},
                ],
            },
            {
                "first_name": "Adnan",
                "last_name": "Uddin",
                "email": "adnan.uddin@curova.com",
                "phone": "+880-1700-000003",
                "date_of_birth": date(1992, 3, 22),
                "gender": "male",
                "blood_type": "O+",
                "address": "456 Gulshan Avenue, Gulshan, Dhaka 1212",
                "emergency_contact_name": "Rahia Uddin",
                "emergency_contact_phone": "+880-1700-000004",
                "allergies": ["Aspirin"],
                "chronic_conditions": ["Asthma"],
                "medications": [
                    {"name": "Albuterol Inhaler", "dosage": "100mcg", "frequency": "As needed", "notes": "For asthma relief"},
                    {"name": "Omeprazole", "dosage": "20mg", "frequency": "Once daily", "notes": "For GERD"},
                ],
            },
            {
                "first_name": "Arafat",
                "last_name": "Sheikh",
                "email": "arafat.sheikh@curova.com",
                "phone": "+880-1700-000005",
                "date_of_birth": date(1988, 8, 10),
                "gender": "male",
                "blood_type": "A-",
                "address": "789 Mohakhali, Dhaka 1212",
                "emergency_contact_name": "Nadia Sheikh",
                "emergency_contact_phone": "+880-1700-000006",
                "allergies": ["Sulfonamides"],
                "chronic_conditions": ["High cholesterol", "Fatty liver disease"],
                "medications": [
                    {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily at night", "notes": "Cholesterol management"},
                    {"name": "Vitamin B12", "dosage": "1000mcg", "frequency": "Once weekly", "notes": "Supplementation"},
                ],
            },
            {
                "first_name": "Sanzid",
                "last_name": "Islam",
                "email": "sanzid.islam@curova.com",
                "phone": "+880-1700-000007",
                "date_of_birth": date(1995, 11, 28),
                "gender": "male",
                "blood_type": "AB+",
                "address": "321 Banani, Dhaka 1213",
                "emergency_contact_name": "Aisha Islam",
                "emergency_contact_phone": "+880-1700-000008",
                "allergies": ["NSAIDs"],
                "chronic_conditions": ["Migraine disorder"],
                "medications": [
                    {"name": "Sumatriptan", "dosage": "50mg", "frequency": "As needed for migraine", "notes": "Takewithin 2 hours of onset"},
                    {"name": "Propranolol", "dosage": "40mg", "frequency": "Twice daily", "notes": "Migraine prevention"},
                ],
            },
            {
                "first_name": "Junain",
                "last_name": "Uddin",
                "email": "junain.uddin@curova.com",
                "phone": "+880-1700-000009",
                "date_of_birth": date(1980, 2, 14),
                "gender": "male",
                "blood_type": "B-",
                "address": "654 Dhanmondi, Dhaka 1205",
                "emergency_contact_name": "Zahra Uddin",
                "emergency_contact_phone": "+880-1700-000010",
                "allergies": ["Latex"],
                "chronic_conditions": ["Rheumatoid arthritis", "Osteoporosis"],
                "medications": [
                    {"name": "Methotrexate", "dosage": "15mg", "frequency": "Once weekly", "notes": "RA management"},
                    {"name": "Alendronate", "dosage": "70mg", "frequency": "Once weekly", "notes": "Bone density"},
                    {"name": "Calcium carbonate", "dosage": "1200mg", "frequency": "Daily", "notes": "Supplementation"},
                ],
            },
            {
                "first_name": "Abroy",
                "last_name": "Sobhan Chy",
                "email": "abroy.sobhan@curova.com",
                "phone": "+880-1700-000011",
                "date_of_birth": date(1990, 7, 3),
                "gender": "male",
                "blood_type": "O-",
                "address": "987 Baridhara, Dhaka 1212",
                "emergency_contact_name": "Zainab Sobhan",
                "emergency_contact_phone": "+880-1700-000012",
                "allergies": ["Codeine"],
                "chronic_conditions": ["Sleep apnea", "Obesity"],
                "medications": [
                    {"name": "CPAP therapy", "dosage": "8 hours nightly", "frequency": "Every night", "notes": "Sleep apnea treatment"},
                    {"name": "Metformin", "dosage": "850mg", "frequency": "Twice daily", "notes": "Weight and glucose management"},
                ],
            },
            {
                "first_name": "Meherab",
                "last_name": "Ahmed",
                "email": "meherab.ahmed@curova.com",
                "phone": "+880-1700-000013",
                "date_of_birth": date(1998, 4, 19),
                "gender": "male",
                "blood_type": "A+",
                "address": "147 Uttara, Dhaka 1230",
                "emergency_contact_name": "Halima Ahmed",
                "emergency_contact_phone": "+880-1700-000014",
                "allergies": ["Sulfa drugs"],
                "chronic_conditions": ["Seasonal allergies", "Mild eczema"],
                "medications": [
                    {"name": "Cetirizine", "dosage": "10mg", "frequency": "Once daily", "notes": "Allergy relief"},
                    {"name": "Hydrocortisone cream", "dosage": "1%", "frequency": "Twice daily as needed", "notes": "For eczema"},
                ],
            },
        ]

        created_count = 0
        updated_count = 0

        for patient_data in patients_data:
            meds = patient_data.pop("medications", [])
            allergies = patient_data.pop("allergies", [])
            chronic_conditions = patient_data.pop("chronic_conditions", [])

            # Create or get user
            user, created = User.objects.get_or_create(
                email=patient_data["email"],
                defaults={
                    "username": patient_data["email"].split("@")[0],
                    "first_name": patient_data["first_name"],
                    "last_name": patient_data["last_name"],
                    "user_type": User.UserType.PATIENT,
                    "phone": patient_data["phone"],
                    "is_active": True,
                },
            )

            # Set password (simple for demo: password123)
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(f"✅ Created user: {user.get_full_name()} ({user.email})")
                created_count += 1
            else:
                self.stdout.write(f"⏭️  User already exists: {user.get_full_name()}")
                updated_count += 1

            # Create or update patient profile
            patient, p_created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    "date_of_birth": patient_data["date_of_birth"],
                    "gender": patient_data["gender"],
                    "blood_type": patient_data["blood_type"],
                    "address": patient_data["address"],
                    "emergency_contact_name": patient_data["emergency_contact_name"],
                    "emergency_contact_phone": patient_data["emergency_contact_phone"],
                    "allergies": allergies,
                    "chronic_conditions": chronic_conditions,
                },
            )

            if not p_created:
                # Update if exists
                patient.date_of_birth = patient_data["date_of_birth"]
                patient.gender = patient_data["gender"]
                patient.blood_type = patient_data["blood_type"]
                patient.address = patient_data["address"]
                patient.emergency_contact_name = patient_data["emergency_contact_name"]
                patient.emergency_contact_phone = patient_data["emergency_contact_phone"]
                patient.allergies = allergies
                patient.chronic_conditions = chronic_conditions
                patient.save()

            # Create medications
            for med_data in meds:
                med, med_created = Medication.objects.get_or_create(
                    patient=patient,
                    name=med_data["name"],
                    defaults={
                        "dosage": med_data["dosage"],
                        "frequency": med_data["frequency"],
                        "notes": med_data["notes"],
                        "is_active": True,
                        "start_date": date.today() - timedelta(days=30),
                    },
                )
                if med_created:
                    self.stdout.write(f"  📋 Added medication: {med.name}")

        self.stdout.write(self.style.SUCCESS(
            f"\n✨ Demo data population complete!\n"
            f"   Created: {created_count} new users\n"
            f"   Updated: {updated_count} existing users\n"
            f"   Total patients: {len(patients_data)}\n"
            f"   Password for all: password123"
        ))
