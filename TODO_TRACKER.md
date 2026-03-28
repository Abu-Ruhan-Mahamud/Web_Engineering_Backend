# Curova — TODO & Issue Tracker

> Living document. Updated as work progresses.  
> **Last updated**: 7 Feb 2026 — Phase 5 complete (Admin Features)

---

## 🔴 Critical — Must Fix Before Demo

| # | Area | File(s) | Description | Status |
|---|------|---------|-------------|--------|
| C-1 | Patient Dashboard | `pages/patient/Dashboard.jsx` | **Medications section never fetched.** `medications` state initialised as `[]` but `fetchDashboardData()` never calls any medications API. "Today's Medications" always shows empty. | ✅ Fixed (F-22) |
| C-2 | Appointments UI | `pages/patient/Appointments.jsx` | **Missing appointment statuses in filter tabs.** Only shows `scheduled, confirmed, completed, cancelled`. Backend also has `in_progress`, `no_show`, `rescheduled`. Missing statuses silently fall into default styling. | ✅ Fixed (F-23) |
| C-3 | Auth Context | `contexts/AuthContext.jsx` | **User object never syncs fully after profile update.** After `PUT /auth/profile/`, only `first_name`, `last_name`, `phone` are merged back into context. Profile fields like `allergies`, `blood_type` etc. are lost from context. | ✅ Fixed (F-24) |

---

## 🟡 Moderate — Should Fix Before Release

| # | Area | File(s) | Description | Status |
|---|------|---------|-------------|--------|
| M-1 | Profile | `pages/patient/Profile.jsx` | **"Delete Account" button has no handler.** Button renders in Danger Zone but clicking does nothing. Misleading. | 🔲 Open |
| M-2 | Profile | `pages/patient/Profile.jsx` | **Password change form is fake.** Form renders fully but submit shows "not yet implemented" toast. Users will fill out the form expecting it to work. | 🔲 Open |
| M-3 | Profile | `pages/patient/Profile.jsx` | **No profile picture upload.** Avatar area has `avatar-upload` class but no file input or upload handler. | 🔲 Open |
| M-4 | Auth | `contexts/AuthContext.jsx` | **No token validation on app startup.** App trusts `localStorage` token without verifying it against the server. If token expired server-side, user appears logged in but every API call fails 401. | ✅ Fixed (F-25) |
| M-5 | API Layer | `services/api.js` | **401 handler uses `window.location.href` (hard reload).** Breaks SPA experience, loses React state. Should use React Router navigation. | ✅ Fixed (F-26) |
| M-6 | Profile | `pages/patient/Profile.jsx` | **Uses `PUT` not `PATCH` for partial updates.** `PUT /auth/profile/` sends only 2 fields (allergies, chronic_conditions). Works now because backend uses `partial=True`, but semantically wrong. | 🔲 Open |

---

## 🟢 Minor / UX Polish

| # | Area | File(s) | Description | Status |
|---|------|---------|-------------|--------|
| U-1 | Login | `pages/public/Login.jsx` | **"Continue with Google" button non-functional.** No OAuth integration. Button does nothing on click. | 🔲 Open |
| U-2 | Login & Register | `Login.jsx`, `Register.jsx` | **"Remember Me" / "Keep me signed in" checkboxes do nothing.** State tracked but never used. Token always stored in localStorage. | 🔲 Open |
| U-3 | Home | `pages/public/Home.jsx` | **Multiple dead links & buttons.** "Consult Now" on doctor cards, "View All →" spans, footer links all non-functional (`href="#"`). | ✅ Fixed (F-19) |
| U-4 | Home | `pages/public/Home.jsx` | **Copyright year hard-coded `2025`.** Should be `{new Date().getFullYear()}`. | ✅ Fixed (F-20) |
| U-5 | Dashboard / Schedule | `doctor/Dashboard.jsx`, `doctor/ScheduleManagement.jsx` | **No error state shown to users.** API failures only logged to console. User sees empty view with no explanation. | 🔲 Open |
| U-6 | Layout | `components/layout/DashboardLayout.jsx` | **Notification bell is decorative.** Button renders in header but has no handler or notification system. | 🔲 Open |
| U-7 | Patient Dashboard | `pages/patient/Dashboard.jsx` | **"Quick Actions" buttons are placeholder.** "Message Doctor", "Upload Document" buttons may not navigate correctly. | 🔲 Open |

---

## 🏗 Incomplete Features — Planned for Later Phases

| Phase | Feature | Description | Status |
|-------|---------|-------------|--------|
| 5 | Messaging System | Real-time chat between patients & doctors. Backend models exist (`messaging/`), frontend page exists as demo HTML only. | 🔲 Not started |
| 5 | Notification System | Push/in-app notifications for appointment reminders, new messages, record updates. | 🔲 Not started |
| 6 | Admin Dashboard | Admin panel for user management, doctor verification, system stats. Backend admin models exist, no custom frontend. | ✅ Done (Phase 5) |
| 6 | Doctor Verification Flow | Admin approves/rejects doctor registrations. Model field `is_verified` not on Doctor model yet. | 🔲 Not started |
| 7 | Password Change Endpoint | Backend endpoint for authenticated password change. Frontend form exists (Profile.jsx) but submits nothing. | 🔲 Not started |
| 7 | Account Deletion | Backend endpoint + frontend flow for account deletion. Button exists (Profile.jsx) but no handler. | 🔲 Not started |
| 7 | OAuth / Social Login | Google OAuth integration. Button exists in Login.jsx but non-functional. | 🔲 Not started |
| 7 | Profile Picture Upload | File upload for user avatars. Container styled but no input/handler. | 🔲 Not started |
| 8 | Appointment Reminders | Email/SMS reminders before appointments. | 🔲 Not started |
| 8 | Doctor Reviews & Ratings | Patient can review doctors after completed appointments. | 🔲 Not started |
| 8 | PDF Export | Export medical records / prescriptions as PDF. | 🔲 Not started |
| 8 | Search & Filter | Global search across patients, records, appointments. Advanced filters. | 🔲 Not started |

---

## ✅ Fixed This Session (7 Feb 2026)

| # | Area | Description |
|---|------|-------------|
| F-1 | Doctor Dashboard | Fixed `a.date` → `a.appointment_date` (today's appointment filter) |
| F-2 | Doctor Dashboard | Fixed `apt.time_slot` → `apt.appointment_time` (time display) |
| F-3 | Doctor Dashboard | Fixed `pt.name` → `pt.first_name + pt.last_name` (patient list) |
| F-4 | Schedule Management | Fixed `apt.date` → `apt.appointment_date`, `apt.time_slot` → `apt.appointment_time` (calendar cells) |
| F-5 | Patients List | Fixed `p.name` → `first_name + last_name` (search filter & display) |
| F-6 | Patient Detail | Fixed `profile.gender` → `patient.gender` (header meta) |
| F-7 | Patient Detail | Fixed `profile.date_of_birth` → `patient.date_of_birth` |
| F-8 | Patient Detail | Fixed `profile.blood_group` → `patient.blood_type` |
| F-9 | Patient Detail | Fixed `profile.emergency_contact` → `patient.emergency_contact_name + phone` |
| F-10 | Patient Detail | Fixed `profile.allergies` → `patient.allergies` |
| F-11 | Patient Detail | Fixed `med.medication_name` → `med.name` (medications list) |
| F-12 | Patient Detail | Fixed `apt.date` / `apt.time_slot` → `apt.appointment_date` / `apt.appointment_time` |
| F-13 | Database | Populated rich test data: 20 appointments, 8 records, 16 prescriptions, 10 medications, 5 patient profiles |
| F-14 | Doctor Profile | Updated: bio, fee ($150), 12yr experience, schedule Mon–Fri 9–5 |
| F-15 | Doctor Profile Page | Created `pages/doctor/Profile.jsx` + route in `App.jsx`. Profile dropdown link now works instead of redirecting to homepage. Three tabs: Personal Info, Professional Info, Schedule. |
| F-16 | **Security** — Doctor Profile | **Fixed credential manipulation vulnerability.** Doctors could self-edit `license_number`, `specialization`, `years_experience` via PUT. Created `DoctorSelfUpdateSerializer` (bio + consultation_fee only). Backend now silently ignores credential fields. Frontend shows credentials as read-only cards with admin notice. Name fields also locked (admin-managed). Verified via direct API test. |
| F-17 | Admin Routes | **Admin had no layout wrapper.** Admin dashboard was a bare `<Route>` with no header, nav, or logout. Created `AdminLayout.jsx` and nested admin routes under it (same pattern as patient/doctor). |
| F-18 | Admin Profile | **`/admin/profile` route missing** (same bug as doctor profile). Created placeholder `AdminProfile.jsx` + route. Profile dropdown no longer redirects to homepage. |
| F-19 | Homepage — Dead Links | **Fixed all dead UI on homepage.** "Consult Now" buttons now link to `/patient/appointments` or `/login`. "View All →" spans replaced with `<Link>`. 9 footer `href="#"` links replaced with `<Link>` to `/` or section anchors. |
| F-20 | Homepage — Copyright | Fixed hardcoded `© 2025` → `{new Date().getFullYear()}`. |
| F-21 | Patient Profile | Security tab "Cancel" button had no handler. Now clears password form fields. |
| F-22 | **C-1** — Medications API | Built medications backend API (`serializers.py`, `views.py`, `urls.py`). Wired patient `Dashboard.jsx` to call `GET /medications/?active=true`. Medications section now populated on patient dashboard. |
| F-23 | **C-2** — Appointment Statuses | Added `in_progress`, `no_show`, `rescheduled` to `STATUS_FILTERS` in `Appointments.jsx`. Added CSS classes for new statuses in `dashboard.css`. |
| F-24 | **C-3** — Auth Context Sync | `updateUser()` now merges data via spread (`{ ...prev, ...newData }`) instead of replacing. Preserves unmodified fields. |
| F-25 | **M-4** — Token Validation | `AuthContext` now validates token against `GET /auth/me/` on startup. Invalid/expired tokens are cleared automatically. |
| F-26 | **M-5** — 401 SPA Handler | Replaced `window.location.href = '/login'` with `CustomEvent('auth:logout')` dispatch. AuthContext listens and clears state without hard reload. |
| F-27 | **Phase 5** — Admin Backend | Created admin API: `GET /admin/stats/` (system-wide stats), `GET/POST /admin/users/` (list + create doctor/admin), `GET/PATCH /admin/users/:id/` (detail + toggle active), `GET /admin/appointments/` (all appointments with filters), `GET /admin/appointments/export/` (CSV export). Files: `admin_serializers.py`, `admin_views.py`, `admin_urls.py`. |
| F-28 | **Phase 5** — Admin Frontend | Built 3 admin pages: **Dashboard** (stats cards, appointment status bars, recent users, recent appointments table), **User Management** (filterable table, search, create doctor/admin modal, activate/deactivate), **Appointments** (status chips, date range filters, search, CSV export). Updated AdminLayout nav (Dashboard, Users, Appointments). Created `admin.css`. |
| F-29 | Admin User | Created admin account: `admin@curova.com` / `testpass123`. |

---

## 📊 Current Data State

| Entity | Count | Notes |
|--------|-------|-------|
| Users | 7 | 5 patients + 1 doctor + 1 admin |
| Appointments | 20 | 6 today, 4 past this week, 4 next week, 6 older |
| Medical Records | 8 | Across 4 patients, linked to completed appointments |
| Prescriptions | 16 | 2 per record average, diverse medications |
| Medications | 10 | 8 active + 2 inactive |
| Documents | 1 | Single test upload |

### Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | testpatient@curova.com | testpass123 |
| Patient | pranto.csecu@gmail.com | testpass123 |
| Patient | janedoe@curova.com | testpass123 |
| Patient | alice@curova.com | testpass123 |
| Patient | newuser@curova.com | TestPass123! |
| Doctor | testdoctor@curova.com | testpass123 |
| Admin | admin@curova.com | testpass123 |

---

## 📝 Notes

- The `pending_reports` stat in doctor dashboard always returns `0` — the backend view counts appointments with `status='completed'` that have no linked `MedicalRecord`, but our seed data links records to completed appointments. This is **correct behavior**, not a bug.
- `documents/` app model is `MedicalDocument`, not `Document`. All imports/references should use `MedicalDocument`.
- Patient model uses `primary_key=True` on the `user` OneToOneField, so Patient PK == User ID. Same for Doctor.
- The `messaging/` Django app exists but has no views/serializers/URLs wired up yet (Phase 5 scope).
