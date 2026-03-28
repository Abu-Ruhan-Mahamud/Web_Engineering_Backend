# Curova — Development Progress Log

## 📋 Overview
This document tracks the development phases, completed features, and current status of the **Curova Healthcare Management System**.

**Tech Stack**: Django 6.0 + DRF (backend) · React 19 + Vite 7 (frontend) · PostgreSQL 16 · Token Auth

---

## 🏁 Phase 1: Project Initialization (✅ COMPLETED)

### Objectives
- Set up development environment, backend, frontend, and database.

### What Was Done
- PostgreSQL database `curova_db` created (user: `curova_user`)
- Django project initialized at `backend/` with DRF, CORS, Pillow, psycopg
- React + Vite project initialized at `frontend/` with React Router DOM, Axios
- Python venv at project root: `venv/`
- `.env` configured for DB credentials

### Key Files
| File | Purpose |
|------|---------|
| `backend/curova_backend/settings.py` | Django config (DB, CORS, REST) |
| `backend/manage.py` | Django management |
| `frontend/vite.config.js` | Vite dev server config |
| `frontend/src/main.jsx` | React app entry point |

---

## 🔐 Phase 2: User Authentication System (✅ COMPLETED)

### Objectives
- Custom user model with 3 roles, registration, login, token auth.

### Backend
- Custom `User` model with `user_type` field: `patient`, `doctor`, `admin`
- One-to-one `Patient` profile (DOB, gender, blood type, allergies, medical history, emergency contact)
- One-to-one `Doctor` profile (license, specialization, experience, available_days, working_hours, bio, fee)
- Token-based authentication via `rest_framework.authtoken`

#### API Endpoints (prefix: `/api/auth/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Patient self-registration |
| POST | `/api/auth/login/` | Login → returns token + user |
| POST | `/api/auth/logout/` | Logout → deletes token |
| GET | `/api/auth/me/` | Current user info |
| GET | `/api/auth/doctors/` | List all doctors |

### Frontend
- `Homepage.jsx` — landing page with navigation
- `Login.jsx` — email + password, stores token in localStorage
- `Registration.jsx` — patient self-registration form
- `AuthContext.jsx` — global auth state (login/logout/user)
- `api.js` — Axios instance with token interceptor
- `ProtectedRoute.jsx` — role-based route wrapper

### Files
- `backend/users/` — models, serializers, views, urls, permissions
- `frontend/src/pages/public/` — Homepage, Login, Registration
- `frontend/src/contexts/AuthContext.jsx`
- `frontend/src/services/api.js`
- `frontend/src/components/common/ProtectedRoute.jsx`

---

## 📅 Phase 3: Patient Features (✅ COMPLETED)

### Objectives
- Full patient dashboard, profile, appointments, medical records, documents.

### Backend — Patient Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | `/api/auth/profile/` | Patient profile (personal + medical info) |
| GET | `/api/auth/dashboard-stats/` | Stats: total/upcoming/completed appointments |
| GET/POST | `/api/appointments/` | List + create appointments |
| GET/PATCH | `/api/appointments/{id}/` | Detail + update status |
| GET | `/api/records/records/` | List medical records |
| GET | `/api/records/records/{id}/` | Record detail with prescriptions |
| GET/POST | `/api/documents/documents/` | List + upload documents |
| GET/DELETE | `/api/documents/documents/{id}/` | Document detail + delete |

### Frontend — 5 Patient Pages
| Page | File | Features |
|------|------|----------|
| Dashboard | `pages/patient/Dashboard.jsx` | Welcome, 4 stat cards, upcoming appointments, medications |
| Profile | `pages/patient/Profile.jsx` | 3 tabs (Personal, Medical, Security), editable fields |
| Appointments | `pages/patient/Appointments.jsx` | Appointment list + booking view with calendar |
| Medical Records | `pages/patient/MedicalRecords.jsx` | Expandable record cards with prescriptions |
| Documents | `pages/patient/Documents.jsx` | Document grid with upload modal, download |

### Layout System
- `DashboardLayout.jsx` — shared header (logo, nav, notifications, user dropdown) + `<Outlet />`
- `PatientLayout.jsx` — passes patient nav items to DashboardLayout

### Styling
Each page has a dedicated CSS file in `frontend/src/styles/`:
- `dashboard.css` (shared layout), `profile.css`, `appointments.css`, `medical-records.css`, `documents.css`
- `variables.css` — CSS custom properties for design system
- `global.css` — base resets

---

## 👨‍⚕️ Phase 4: Doctor Features (✅ COMPLETED)

### Objectives
- Doctor dashboard, schedule management, patient overview, and create medical records.

### Backend — Doctor Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/doctor/dashboard-stats/` | Stats: today's appointments, total patients, pending, weekly |
| GET/PUT | `/api/auth/doctor/profile/` | Doctor profile (user + specialization, bio, etc.) |
| GET/PUT | `/api/auth/doctor/schedule/` | Working hours, available days, slot duration |
| GET | `/api/auth/doctor/patients/` | List unique patients with last visit date |
| GET | `/api/auth/doctor/patients/{id}/` | Full patient detail (info, appointments, records, meds) |
| POST | `/api/records/create/` | Create medical record with nested prescriptions |

### Frontend — 4 Doctor Pages
| Page | File | Features |
|------|------|----------|
| Dashboard | `pages/doctor/Dashboard.jsx` | Welcome, 4 stat cards, today's schedule tabs, quick stats, recent patients |
| Schedule | `pages/doctor/ScheduleManagement.jsx` | Weekly config with toggles, week calendar grid, save schedule |
| Patients | `pages/doctor/Patients.jsx` | Searchable patient cards grid |
| Patient Detail | `pages/doctor/PatientDetail.jsx` | Gradient header, info sidebar, allergies, meds, tabbed history/appointments |
| Create Record | `pages/doctor/CreateRecord.jsx` | Multi-section form: complaint, vitals, diagnosis tags, treatment, repeatable prescriptions |

### Layout
- `DoctorLayout.jsx` — passes doctor nav items (Dashboard, Schedule, Patients) to DashboardLayout
- Routes nested under `/doctor/*` in `App.jsx`

### Styling
- `doctor-dashboard.css` — stats grid, schedule tabs, appointment list, sidebar
- `doctor-schedule.css` — toggle switches, week grid calendar, modal, legend
- `doctor-patients.css` — patient cards, detail view, timeline, tabs
- `doctor-records.css` — form sections, tag input, prescription blocks

---

## 👨‍💼 Phase 5: Admin Dashboard (📝 PLANNED)

### Planned Features
- Admin dashboard with system statistics
- Doctor verification workflow
- User management (search, filter, activate/deactivate)
- Bulk operations

---

## 💬 Phase 6: Messaging System (📝 PLANNED)

### Planned Features
- Patient-doctor messaging
- Real-time messaging (WebSocket consideration)
- Notification system

---

## 🧪 Phase 7: Testing & QA (📝 PLANNED)

### Planned Tasks
- Backend unit tests (Django TestCase)
- Frontend component tests
- API endpoint testing
- Security audit

---

## 🚀 Phase 8: Deployment (📝 PLANNED)

### Planned Tasks
- Production settings
- Static file config (whitenoise)
- HTTPS, domain setup
- Server deployment

---

## 📊 Current Status Summary

| Phase | Status |
|-------|--------|
| 1 — Project Setup | ✅ Complete |
| 2 — Authentication | ✅ Complete |
| 3 — Patient Features | ✅ Complete |
| 4 — Doctor Features | ✅ Complete |
| 5 — Admin Dashboard | 📝 Planned |
| 6 — Messaging | 📝 Planned |
| 7 — Testing & QA | 📝 Planned |
| 8 — Deployment | 📝 Planned |

---

## 🔐 Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | `testpatient@curova.com` | `testpass123` |
| Doctor | `testdoctor@curova.com` | `testpass123` |
| Admin | `admin@curova.com` | `adminpass123` |

---

## 🗂️ Project Structure

```
WebProject_Curova/
├── backend/
│   ├── curova_backend/     # Django settings, root urls
│   ├── users/              # Auth, profiles, permissions
│   ├── appointments/       # Booking system
│   ├── medical/            # Records + prescriptions
│   ├── medications/        # Medication model
│   ├── documents/          # File upload/download
│   ├── messaging/          # (future)
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/     # Layout, common components
│   │   ├── contexts/       # AuthContext
│   │   ├── pages/          # public/, patient/, doctor/, admin/
│   │   ├── services/       # api.js (Axios)
│   │   └── styles/         # CSS files
│   ├── package.json
│   └── vite.config.js
├── project_docs/           # Design demos, plan
├── venv/                   # Python virtual environment
├── README.md
├── QUICK_START.md
└── DEVELOPMENT_LOG.md      # ← This file
```

---

## 🎨 Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--color-deep-blue` | `#1e3a8a` | Logo, active nav, headings |
| `--color-teal` | `#17a2b8` | Primary accent — buttons, links, icons |
| `--color-teal-hover` | `#138496` | Hover states |
| `--color-light-teal` | `#74C3D0` | Gradient start |
| `--color-page-bg` | `#f5f5f7` | Page background |
| `--color-row-bg` | `#f9fafb` | Card interior backgrounds |
| Font | Poppins 300–700 | All text |
| Card radius | 16px | Cards, modals |
| Input radius | 8px | Form fields |

---

**Last Updated**: June 2025
**Status**: Active Development — Phase 4 Complete
