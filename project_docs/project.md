# CUROVA Healthcare Web Application - Build Prompt

## Project Goal
Build a complete full-stack healthcare management web application with patient appointment booking, medical records management, and three user roles (Patient, Doctor, Admin).
MAKE SURE TO REVIEW ALL DOCUMENTS AND DIRECTORIES AT:
/home/t14/CODEBASE/WebProject_Curova/project_docs
---

## ⚠️ IMPORTANT: Design Philosophy

**This document contains design decisions from academic project phases (D1/D2). DO NOT blindly follow these specifications.**

**Key Principles:**
- ✅ **Real-world dynamics first** - Build what makes sense for actual healthcare workflows
- ✅ **User intuitiveness first** - If something feels clunky or unintuitive, redesign it
- ✅ **Question everything** - These design choices may have issues, edge cases, or over-engineering
- ✅ **Practicality over documentation** - If a documented approach doesn't work well in practice, improve it

**Your mission:** Build an intuitive, production-quality healthcare app that real users would enjoy using, not just fulfill academic requirements.

---

## 🎨 Design Adherence

**CRITICAL: Match the demo designs as closely as possible.**

The `/home/t14/CODEBASE/WebProject_Curova/project_docs/frontend_design_demo/` folder contains HTML demos for all pages. These are your visual reference:

- ✅ **Color palette is FIXED** - Use the exact colors from the demos (#17a2b8, #1e3a8a, #74C3D0, etc.). Tastefully decorate around these.
- ✅ **Component styling must match** - Buttons, cards, forms, modals should look like the demos
- ✅ **Page layouts should mirror demos** - Follow the general structure and visual hierarchy
- ✅ **Typography must match** - Poppins font, sizing, weights from demos

**Don't reinvent the wheel visually** - The design work is already done. Your focus should be on making it functional, responsive, and connected to a working backend.

**Reference files:**
- `project_docs/frontend_design_demo/*.html` - All 16 page designs
- `pages_documentation.md` - Detailed specs for each page

---

## 🔧 Development Strategy

**CRITICAL: Build frontend and backend side by side, NOT separately.**

**Cross-platform compatibility:**
- ⚠️ **Project must run on Windows, Linux (Fedora 43, Linux Mint), and any other platform**
- Use platform-independent paths, commands, and configurations
- Test on different team member systems before finalizing

**Git workflow:**
- Repository exists but **will NOT be used during development**
- Push everything once the project is complete
- Keep local backups of your work

**Step 1: Lock in the database schema FIRST**
- ⚠️ **Finalize and save your database design before coding** - Changes later are painful
- Review the 9-table schema, fix any issues you spot NOW
- Document your final schema (SQL or Django models) and commit it
- Run migrations and don't change core structure unless absolutely necessary

**Step 2: Develop iteratively per feature**
- Build one complete feature at a time: Database → API → UI → Integration
- Example flow: User auth → Patients can register (model + API + UI + test) → Doctors can register → Login works end-to-end
- **Don't build entire backend, then entire frontend** - You'll face integration nightmares

**Why this matters:**
- ❌ Separate development = discovering API/UI mismatches too late
- ✅ Side-by-side development = catch issues immediately, adjust both ends together
- ❌ Changing database mid-project = rewriting migrations, serializers, API contracts, frontend models
- ✅ Locked database = stable foundation, focus on features not schema debates

---

## Tech Stack
- **Frontend:** React.js with Vite
- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Auth:** Token-based authentication (DRF TokenAuthentication)
- **Styling:** Custom CSS with Poppins font, teal/blue theme (#17a2b8, #1e3a8a, #74C3D0)

## User Roles & Permissions
- **Patient:** Book appointments, view own medical records, upload documents, track medications
- **Doctor:** View assigned patients, manage schedule, create medical records, write prescriptions
- **Admin:** Manage all users, view system statistics, deactivate accounts

## Database Schema (9 Tables)

**Core entities with ISA inheritance pattern:**
- `users` (base table: id, email, password, user_type, first_name, last_name)
- `patients` (1:1 with users: date_of_birth, phone, allergies[], medical_history JSONB)
- `doctors` (1:1 with users: license_number, specialization, years_experience)
- `appointments` (N:1 patient, N:1 doctor: appointment_date, status, reason, notes)
- `medical_records` (1:1 with appointments: diagnosis, symptoms, treatment_notes)
- `prescriptions` (N:1 medical_record: medication_name, dosage, frequency - immutable)
- `medications` (N:1 patient: name, dosage, is_active - current tracking)
- `medication_reminders` (N:1 medication: reminder_time, is_enabled)
- `medical_documents` (N:1 patient: file_path, document_type, description)

**Key constraints:**
- `UNIQUE(doctor_id, appointment_date)` prevents double-booking
- Passwords hashed with Django PBKDF2
- Foreign keys with CASCADE deletes

## API Endpoints (RESTful)

**Auth (no auth required):**
- `POST /api/auth/register/` - Register user
- `POST /api/auth/login/` - Get token
- `POST /api/auth/logout/` - Invalidate token

**Patients:**
- `GET/PATCH /api/patients/<id>/` - Profile
- `GET /api/patients/<id>/medical-records/` - Medical history
- `GET /api/patients/<id>/prescriptions/` - All prescriptions
- `GET /api/patients/<id>/documents/` - All documents

**Doctors:**
- `GET /api/doctors/` - List (filter by specialization)
- `GET /api/doctors/<id>/` - Profile

**Appointments:**
- `GET /api/appointments/` - List (filter by status, date)
- `POST /api/appointments/` - Book (patients only)
- `PATCH /api/appointments/<id>/` - Update status

**Medical Records:**
- `POST /api/medical-records/` - Create (doctors only)

**Prescriptions:**
- `POST /api/prescriptions/` - Create (doctors only)

**Medications:**
- `GET /api/medications/` - Current meds (patient)
- `POST /api/medications/` - Add med

**Documents:**
- `POST /api/medical-documents/` - Upload (multipart/form-data)

**Admin:**
- `GET /api/admin/users/` - All users
- `PATCH /api/admin/users/<id>/deactivate/` - Deactivate user

**Permission classes:** IsPatient, IsDoctor, IsAdmin, IsOwnerOrDoctor

## UI Pages (16 Total)

**Public (3):** Homepage, Login, Registration

**Patient (6):** Dashboard, Book Appointment, Medical Records, Profile, Documents, Medications

**Doctor (4):** Dashboard, Schedule Management, Patient Details, Create Medical Record

**Admin (3):** Dashboard, User Management, Appointments Calendar

**Design:** Teal/blue color scheme, Poppins font, responsive (mobile-first), card-based layouts

## Core Features to Implement

### Authentication & Authorization
- User registration with email (patient/doctor/admin).
- Login with token generation
- Permission classes enforcing RBAC
- Password hashing (Django PBKDF2)

### Patient Features
- Book appointments (select doctor, date/time)
- View own medical history timeline
- Upload medical documents (PDF, images)
- Track current medications
- Set medication reminders

### Doctor Features
- View daily/weekly schedule
- Access patient medical records
- Create medical records after appointments
- Write prescriptions
- Update appointment status

### Admin Features
- List all users (filter by type)
- Create/deactivate accounts
- View system statistics
- Export appointment data

### Security
- SQL injection prevention (Django ORM parameterized queries)
- Unauthorized access prevention (permission checks at view level)
- HTTPS encryption
- Input validation (Django serializers)
- File upload restrictions (PDF/JPG/PNG only, 5MB max)

## Implementation Notes

**Database design decisions:**
- ISA inheritance (User → Patient/Doctor) avoids NULL fields
- Separate Prescription (immutable audit) vs Medication (mutable tracking)
- PostgreSQL arrays for allergies, JSONB for flexible medical_history
- `UNIQUE(doctor_id, appointment_date)` prevents double-booking at DB level

**API patterns:**
- RESTful endpoints (GET/POST/PATCH/DELETE)
- Nested routes for related resources (`/patients/<id>/medical-records/`)
- Query params for filtering (`?status=scheduled&date=2026-02-05`)
- Token in Authorization header: `Authorization: Token <token>`

---

**References:**
- Frontend demo files: `/home/t14/CODEBASE/WebProject_Curova/project_docs/frontend_design_demo/`
- Detailed specs in D1, D2 documents (requirements, design decisions)*********
- Git repos: Web_Engineering_Backend, Web_Engineering_Frontend
