"""
Seed realistic medication & notification data for testing toast popups.

Usage:
    python manage.py seed_notifications

What it does:
    1. Adds varied-frequency medications for patient@curova.com
    2. Clears stale medication reminder notifications
    3. Creates a handful of fresh notifications (different types)
       so the toast system fires on the very next poll cycle.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from users.models import User, Patient, Doctor
from medications.models import Medication
from notifications.models import Notification


class Command(BaseCommand):
    help = "Seed medication and notification data to test toast popups."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "Seeding notification & medication test data..."
        ))

        # ── Resolve users ──
        try:
            patient_user = User.objects.get(email="patient@curova.com")
            patient = patient_user.patient_profile
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                "patient@curova.com not found. Run 'python manage.py seed_data' first."
            ))
            return

        doctor = Doctor.objects.first()
        today = timezone.now().date()

        # ─── 1. Add varied-frequency medications ────────────────────
        new_meds = [
            {
                "name": "Metformin",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "notes": "Take with breakfast and dinner",
            },
            {
                "name": "Amoxicillin",
                "dosage": "250mg",
                "frequency": "Three times daily",
                "notes": "Complete full course — 7 days remaining",
            },
            {
                "name": "Vitamin D3",
                "dosage": "2000 IU",
                "frequency": "Once daily",
                "notes": "Take with a meal containing fat for better absorption",
            },
            {
                "name": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "Once daily",
                "notes": "Take at bedtime",
            },
            {
                "name": "Omeprazole",
                "dosage": "20mg",
                "frequency": "Twice daily",
                "notes": "Take 30 minutes before meals",
            },
        ]

        created_count = 0
        for m in new_meds:
            _, created = Medication.objects.get_or_create(
                patient=patient,
                name=m["name"],
                defaults={
                    "dosage": m["dosage"],
                    "frequency": m["frequency"],
                    "is_active": True,
                    "notes": m["notes"],
                    "prescribed_by": doctor,
                    "start_date": today - timedelta(days=14),
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  ✔ Medication: {m['name']} ({m['frequency']})"
                ))
            else:
                self.stdout.write(f"  ⏩ {m['name']} already exists, skipping.")

        # ─── 2. Clear ALL existing notifications for this patient ───
        deleted_count, _ = Notification.objects.filter(
            recipient=patient_user,
        ).delete()
        self.stdout.write(f"  🗑  Cleared {deleted_count} old notifications")

        # ─── 3. Create a batch of fresh mixed-type notifications ────
        #    These appear as "already in the system" when the page loads.
        now = timezone.now()
        seed_notifications = [
            {
                "title": "Appointment Confirmed",
                "message": "Your appointment with Dr. Sarah Ahmed on Feb 12 at 9:30 AM has been confirmed.",
                "notification_type": "appointment",
                "related_object_type": "appointment",
                "is_read": True,
                "created_at": now - timedelta(hours=3),
            },
            {
                "title": "Lab Results Ready",
                "message": "Your Complete Blood Count (CBC) results are now available. Tap to view.",
                "notification_type": "lab_result",
                "related_object_type": "lab_test",
                "is_read": True,
                "created_at": now - timedelta(hours=1),
            },
            {
                "title": "New Prescription Added",
                "message": "Dr. Sarah Ahmed prescribed Amoxicillin 250mg — Three times daily for 7 days.",
                "notification_type": "prescription",
                "related_object_type": "medication",
                "is_read": True,
                "created_at": now - timedelta(minutes=45),
            },
        ]

        for n in seed_notifications:
            created_at = n.pop("created_at")
            notif = Notification.objects.create(recipient=patient_user, **n)
            # Override auto_now_add via queryset update
            Notification.objects.filter(pk=notif.pk).update(created_at=created_at)

        self.stdout.write(f"  ✔ Created {len(seed_notifications)} background notifications (read)")

        # ─── 4. Create UNREAD notifications that will trigger toasts ─
        #    The toast system fires when unread_count increases on the
        #    next 30-second poll. We deliberately leave these UNREAD so
        #    the frontend's polling picks them up and pops toast popups.
        toast_notifications = [
            {
                "title": "Morning: Metformin",
                "message": "Time to take Metformin (500mg) — Twice daily",
                "notification_type": "medication",
                "related_object_type": "medication_reminder",
                "is_read": False,
            },
            {
                "title": "Morning: Amoxicillin",
                "message": "Time to take Amoxicillin (250mg) — Three times daily",
                "notification_type": "medication",
                "related_object_type": "medication_reminder",
                "is_read": False,
            },
            {
                "title": "Morning: Vitamin D3",
                "message": "Time to take Vitamin D3 (2000 IU) — Once daily",
                "notification_type": "medication",
                "related_object_type": "medication_reminder",
                "is_read": False,
            },
            {
                "title": "Upcoming Appointment",
                "message": "Reminder: You have an appointment with Dr. Sarah Ahmed tomorrow at 9:30 AM.",
                "notification_type": "appointment",
                "related_object_type": "appointment",
                "is_read": False,
            },
        ]

        for n in toast_notifications:
            Notification.objects.create(recipient=patient_user, **n)

        self.stdout.write(self.style.SUCCESS(
            f"  🔔 Created {len(toast_notifications)} UNREAD notifications (will trigger toasts!)"
        ))

        # ─── Summary ─────────────────────────────────────────────────
        total_meds = Medication.objects.filter(patient=patient, is_active=True).count()
        total_unread = Notification.objects.filter(
            recipient=patient_user, is_read=False
        ).count()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("═" * 55))
        self.stdout.write(self.style.SUCCESS("  Notification test data seeded!"))
        self.stdout.write(self.style.SUCCESS("═" * 55))
        self.stdout.write("")
        self.stdout.write(f"  Active medications : {total_meds}")
        self.stdout.write(f"  Unread notifications: {total_unread}")
        self.stdout.write("")
        self.stdout.write("  → Login as patient@curova.com / Patient@123")
        self.stdout.write("  → Toast popups should appear within 30 seconds")
        self.stdout.write("  → Additional reminders will auto-generate based on time of day:")
        self.stdout.write("       Morning (07:00)  — all medications")
        self.stdout.write("       Afternoon (13:00) — Amoxicillin (3× daily)")
        self.stdout.write("       Night (20:00)    — Metformin, Amoxicillin, Omeprazole")
        self.stdout.write("")
