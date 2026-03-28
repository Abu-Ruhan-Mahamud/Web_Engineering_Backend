"""
Auto-generate medication reminder notifications.

Called lazily on the unread-count poll (every 30 s).  For each active
medication whose frequency implies a time-of-day that has already passed
today, we create **one** notification per med-per-slot-per-day (idempotent).

Frequency → time-slot mapping
─────────────────────────────
  "Once daily" / default       → Morning  (07:00)
  "Twice daily"                → Morning  (07:00)  +  Night (20:00)
  "Three times daily"          → Morning  (07:00)  +  Afternoon (13:00) + Night (20:00)

We identify duplicates by checking for an existing notification where
  related_object_type = "medication_reminder"
  related_object_id   = medication.id
  title contains the slot label (Morning / Afternoon / Night)
  created_at is today
"""

from datetime import time as dt_time

from django.utils import timezone

from medications.models import Medication
from notifications.helpers import create_notification

# ── Slot definitions ──────────────────────────────────────────
MORNING = ("Morning", dt_time(7, 0))
AFTERNOON = ("Afternoon", dt_time(13, 0))
NIGHT = ("Night", dt_time(20, 0))

# Map lower-cased frequency keywords → list of slots
FREQUENCY_SLOTS = {
    "three times daily": [MORNING, AFTERNOON, NIGHT],
    "three times a day": [MORNING, AFTERNOON, NIGHT],
    "3 times daily": [MORNING, AFTERNOON, NIGHT],
    "twice daily": [MORNING, NIGHT],
    "twice a day": [MORNING, NIGHT],
    "2 times daily": [MORNING, NIGHT],
    # everything else falls through to the default: [MORNING]
}

DEFAULT_SLOTS = [MORNING]


def _slots_for_frequency(frequency: str):
    """Return the list of (label, time) slots for a given frequency string."""
    freq_lower = frequency.strip().lower()
    for key, slots in FREQUENCY_SLOTS.items():
        if key in freq_lower:
            return slots
    return DEFAULT_SLOTS


def check_medication_reminders(user):
    """
    For *patient* users only: create any due medication notifications for
    today that haven't been created yet.  Safe to call on every request —
    the duplicate guard makes it cheap.
    """
    if user.user_type != "patient":
        return

    now = timezone.localtime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    current_time = now.time()

    # Active medications for this patient
    meds = Medication.objects.filter(
        patient=user.patient_profile, is_active=True
    ).select_related("prescribed_by__user")

    if not meds.exists():
        return

    # All medication-reminder notifications already created today for this user
    from notifications.models import Notification

    existing = set(
        Notification.objects.filter(
            recipient=user,
            notification_type="medication",
            related_object_type="medication_reminder",
            created_at__gte=today_start,
        ).values_list("related_object_id", "title")
    )

    to_create = []

    for med in meds:
        slots = _slots_for_frequency(med.frequency)
        for label, slot_time in slots:
            # Only fire if the slot time has already passed today
            if current_time < slot_time:
                continue

            title = f"{label}: {med.name}"
            # Skip if already sent today (match on med id + title)
            if (med.id, title) in existing:
                continue

            to_create.append(
                Notification(
                    recipient=user,
                    title=title,
                    message=f"Time to take {med.name} ({med.dosage}) — {med.frequency}",
                    notification_type="medication",
                    related_object_type="medication_reminder",
                    related_object_id=med.id,
                )
            )

    if to_create:
        Notification.objects.bulk_create(to_create)
