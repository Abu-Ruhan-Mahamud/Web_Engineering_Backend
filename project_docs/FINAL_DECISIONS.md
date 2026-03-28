# CUROVA — Final Decisions: Remaining Work

**Date:** February 9, 2026  
**Status:** Approved for implementation  
**Scope:** 8 tasks across backend and frontend

---

## Problem 1: No Notification System

**Current state:** The bell icon in the navigation bar is purely decorative. No notification model, endpoints, or logic exists. Users have no way to know when something important happens (appointment confirmed, lab results ready, prescription created) unless they manually check each page.

**Solution:**
- Create a new `notifications` Django app with a `Notification` model containing: recipient, title, message, notification_type (appointment, medication, lab_result, prescription, system), is_read flag, related object reference, and timestamps.
- REST endpoints: list notifications (paginated), mark single as read, mark all as read, get unread count.
- Wire the existing bell icon to show a live unread count badge and a dropdown with recent notifications.
- Full notifications page for history.

---

## Problem 2: No Medication Reminders UI

**Current state:** The `MedicationReminder` model exists in the database (medication FK, reminder_time, is_enabled) but has zero frontend UI. Patients cannot set, view, or manage reminders for their medications. This feature is explicitly listed in the project requirements.

**Solution:**
- Add a reminders section to the patient Medications page where patients can set one or more reminder times per medication and toggle them on/off.
- Reminders integrate with the notification system — when a reminder time passes, a notification is generated (in-app only, consistent with web app limitations).
- No redundancy: medication reminders are a *source* of notifications, not a parallel system. One notification model serves all notification types.

---

## Problem 3: Unrestricted Doctor Schedule Changes

**Current state:** Doctors can freely modify their schedule (remove available days, change working hours, change slot duration) via a simple PUT endpoint with zero validation. If a doctor removes "Wednesday" from their available days while having 5 confirmed Wednesday appointments, nothing happens to those appointments — they become orphaned with no one notified.

**Solution (Option B — Balanced Approach):**
1. **Backend validation:** Before applying schedule changes, query for future appointments that would become invalid under the new schedule (appointments on removed days, or outside new working hours).
2. **If conflicts exist:** Return the list of affected appointments to the frontend instead of applying the change.
3. **Frontend warning modal:** Show the doctor exactly which patients/appointments are affected. Doctor can confirm or cancel the change.
4. **On confirm:** Backend auto-cancels affected appointments and generates notifications to affected patients informing them their appointment was cancelled due to a schedule change, with a prompt to rebook.
5. **Additional fix:** Add today highlighting to the schedule management grid.

---

## Problem 4: Poor Patient Booking UX

**Current state:** Three UX gaps in the appointment booking flow:
- The calendar allows clicking on ANY future date, even if that day-of-week is not in the doctor's available days. The patient only learns the day is unavailable after the server rejects the booking.
- Time slots are generated purely from schedule math with no indication of which slots are already booked. The patient picks a slot, submits, and only then discovers it's taken via a server error.
- No slot boundary enforcement — a patient could theoretically book at 9:07 AM for a doctor with 30-minute slots.

**Solution:**
- **Calendar filtering:** Gray out / disable dates whose day-of-week is NOT in the selected doctor's `available_days`.
- **Booked slot display:** New backend endpoint `GET /api/appointments/booked-slots/?doctor_id=X&date=Y` returns already-booked time slots. Frontend shows these slots as disabled/taken.
- **Slot boundary enforcement:** Backend validation ensures appointment_time aligns to a slot boundary: `(appointment_time - working_hours_start) % slot_duration == 0`.

---

## Problem 5: Stale Past Appointments

**Current state:** Appointments that have passed their scheduled date but are still in "scheduled" or "confirmed" status remain unchanged forever. There is no automatic cleanup or status transition, leading to inaccurate dashboard stats and confusing appointment lists.

**Solution (Industry Standard Approach):**
- **Auto-cleanup on access:** When the appointment list API is called, run a lightweight check that updates stale appointments:
  - Past "scheduled" (never confirmed) → **"no_show"** (patient didn't confirm and didn't attend)
  - Past "confirmed" → **"completed"** (benefit of the doubt — confirmed appointments likely occurred; doctor may have forgotten to update status)
- **Visual distinction:** Past appointments show clear status badges in the UI so users understand what happened.
- **No cron dependency:** Cleanup triggers on API access, keeping the system simple without requiring background task infrastructure.

---

## Problem 6: Tedious Lab Tech Report Entry

**Current state:** Lab technicians must manually type every field for every test result — values, reference ranges, units, findings, impressions. This is slow, error-prone, and produces inconsistent formatting across reports.

**Solution (Frontend-Only, Test-Specific Templates):**
- Define template data as JSON constants in the frontend for common test types:
  - **Structured:** CBC (Hemoglobin, WBC, RBC, Platelets, Hematocrit, MCV, MCH, MCHC), Lipid Panel (Total Cholesterol, LDL, HDL, Triglycerides), Thyroid Panel (TSH, T3, T4), Basic Metabolic Panel (Glucose, BUN, Creatinine, Sodium, Potassium, Chloride, CO2), Urinalysis (pH, Specific Gravity, Protein, Glucose, WBC, RBC), ECG/Cardiac (Heart Rate, PR Interval, QRS Duration, QT Interval).
  - **Narrative:** Chest X-Ray, CT Scan, MRI, Ultrasound, Pathology, Microbiology — each with section-specific prompts (e.g., "Heart size: Normal/Enlarged", "Lung fields: Clear/Opacity noted").
- When a lab tech selects a test type, the form pre-fills with standard parameters, reference ranges, and units. The lab tech only enters actual measured values.
- Test-specific (not category-level) because different tests within the same category have different parameters (CBC ≠ Lipid Panel, both are "blood tests").
- Frontend-only approach — no backend changes needed. Templates are maintainable as simple JS constants.

---

## Implementation Order

| # | Task | Depends On | Effort |
|---|---|---|---|
| 1 | Notifications backend app | — | Medium |
| 2 | Notifications frontend (bell icon + dropdown) | Task 1 | Medium |
| 3 | Auto-notification generation on events | Task 1 | Medium |
| 4 | Medication reminders UI + notification integration | Tasks 1-3 | Medium |
| 5 | Doctor schedule conflict handling | Task 1 (for notifications) | Medium |
| 6 | Patient booking UX improvements | — | Medium |
| 7 | Past appointment auto-cleanup | — | Low |
| 8 | Lab tech report templates | — | Medium |

---

## Technical Notes

- **No email notifications** — web app limitation; in-app only.
- **No background workers** — no Celery/Redis; all logic runs on request/response cycle.
- **Notification model is the single source** — medication reminders, appointment alerts, and lab results all flow through one notification system.
- **Templates are frontend-only** — hardcoded JSON constants, no admin UI for template management.
- **Past appointment cleanup is lazy** — runs on API access, not on a cron schedule.
