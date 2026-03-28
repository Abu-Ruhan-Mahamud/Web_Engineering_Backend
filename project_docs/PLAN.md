# CUROVA - Project Implementation Plan

## Vision
Build a production-quality healthcare web app with intuitive workflows that real users would enjoy. Match demo designs exactly while questioning any functionality that doesn't make practical sense.

## Key Constraints
- ✅ Cross-platform (Windows, Fedora 43, Linux Mint)
- ✅ Match demo HTML designs (colors, components, layouts)
- ✅ Build frontend + backend side by side per feature
- ✅ Lock database schema before starting features
- ✅ No git pushes until project complete

---

## Phase 1: Foundation Setup

### 1.1 Environment Setup
- [ ] Install Python 3.10+, Node.js 18+, PostgreSQL 14+
- [ ] Verify setup works on all team member systems (Windows, Fedora, Mint)
- [ ] Create project folders: `backend/`, `frontend/`

### 1.2 Database Schema Finalization
**CRITICAL: Do NOT start coding until this is locked**

- [ ] Review 9-table schema from project.md
- [ ] Question and fix any issues NOW (inheritance approach, relationships, constraints)
- [ ] Document final schema (save as `backend/SCHEMA.md` or similar)
- [ ] Create PostgreSQL database: `curova_db`
- [ ] Test schema manually with SQL or Django models

**Schema to lock:**
- users, patients, doctors, appointments, medical_records, prescriptions, medications, medication_reminders, medical_documents

### 1.3 Backend Bootstrap
- [ ] Initialize Django project: `django-admin startproject curova_backend backend`
- [ ] Install dependencies: `django`, `djangorestframework`, `psycopg2-binary`, `python-decouple`
- [ ] Configure PostgreSQL connection in `settings.py`
- [ ] Create Django apps: `users`, `appointments`, `medical`, `medications`, `documents`
- [ ] Define all 9 models based on locked schema
- [ ] Run migrations: `python manage.py makemigrations && python manage.py migrate`
- [ ] Test models in Django shell

### 1.4 Frontend Bootstrap
- [ ] Initialize React project: `npm create vite@latest frontend -- --template react`
- [ ] Install dependencies: `axios`, `react-router-dom`
- [ ] Set up folder structure: `components/`, `pages/`, `services/`, `contexts/`
- [ ] Copy demo HTML files to reference folder
- [ ] Extract colors/fonts from demos: Create `styles/variables.css`

---

## Phase 2: Authentication (Build Vertically)

### 2.1 Backend - Auth System
- [ ] Set up DRF TokenAuthentication
- [ ] Create User model (or extend AbstractUser with user_type field)
- [ ] Create Patient/Doctor models with 1:1 relationship to User
- [ ] Build serializers: `UserSerializer`, `PatientSerializer`, `DoctorSerializer`
- [ ] Build API views:
  - `POST /api/auth/register/` (patient/doctor registration)
  - `POST /api/auth/login/` (token generation)
  - `POST /api/auth/logout/` (token invalidation)
- [ ] Test with Postman/curl

### 2.2 Frontend - Auth Pages
- [ ] Create `pages/Homepage.jsx` (match `curova_homepage.html`)
- [ ] Create `pages/Login.jsx` (match `curova-login-page.html`)
- [ ] Create `pages/Registration.jsx` (match `curova_registration.html`)
- [ ] Create `services/api.js` (axios instance with token handling)
- [ ] Create `contexts/AuthContext.jsx` (user state management)
- [ ] Set up routing with `react-router-dom`

### 2.3 Integration Test
- [ ] Register patient from frontend → Verify in database
- [ ] Register doctor from frontend → Verify in database
- [ ] Login as patient → Store token → Redirect to patient dashboard
- [ ] Login as doctor → Store token → Redirect to doctor dashboard
- [ ] Logout → Clear token → Redirect to homepage

---

## Phase 3: Patient Features (Build Vertically)

### 3.1 Patient Dashboard
**Backend:**
- [ ] Create permission class: `IsPatient`
- [ ] Build API: `GET /api/patients/<id>/` (profile data)
- [ ] Build API: `GET /api/appointments/` (filter for logged-in patient)
- [ ] Build API: `GET /api/patients/<id>/medical-records/` (recent records)

**Frontend:**
- [ ] Create `pages/PatientDashboard.jsx` (match `patient_dashboard.html`)
- [ ] Fetch and display: upcoming appointments, recent records
- [ ] Protected route (require auth)

**Test:** Login as patient → See dashboard with correct data

### 3.2 Book Appointment
**Backend:**
- [ ] Build API: `GET /api/doctors/` (list with filter by specialization)
- [ ] Build API: `POST /api/appointments/` (create appointment, check double-booking)
- [ ] Validate: UNIQUE constraint on (doctor_id, appointment_date)

**Frontend:**
- [ ] Create `pages/BookAppointment.jsx` (match `patient_book_appointment.html`)
- [ ] Doctor list with search/filter
- [ ] Calendar view for available slots
- [ ] Booking form with validation

**Test:** Book appointment → Verify in DB → Should prevent double-booking

### 3.3 Medical Records View
**Backend:**
- [ ] Ensure `GET /api/patients/<id>/medical-records/` returns full history
- [ ] Include prescriptions in response

**Frontend:**
- [ ] Create `pages/MedicalRecords.jsx` (match `patient_medical_records.html`)
- [ ] Timeline view with filters

**Test:** View medical records → See past appointments, diagnoses, prescriptions

### 3.4 Document Upload
**Backend:**
- [ ] Build API: `POST /api/medical-documents/` (multipart/form-data)
- [ ] Validate file types (PDF/JPG/PNG), max 5MB
- [ ] Build API: `GET /api/patients/<id>/documents/`

**Frontend:**
- [ ] Create `pages/Documents.jsx` (match `patient_documents.html`)
- [ ] Drag-drop upload, document type selector
- [ ] Grid view with download links

**Test:** Upload document → Verify file saved → Download and view

### 3.5 Medications & Reminders
**Backend:**
- [ ] Build API: `GET /api/medications/` (current patient meds)
- [ ] Build API: `POST /api/medications/` (add medication)

**Frontend:**
- [ ] Create `pages/Medications.jsx` or section in dashboard
- [ ] Active/inactive tabs
- [ ] Add medication form, reminder setter

**Test:** Add medication → Set reminder → Verify in DB

### 3.6 Patient Profile
**Backend:**
- [ ] Build API: `PATCH /api/patients/<id>/` (update profile)

**Frontend:**
- [ ] Create `pages/Profile.jsx` (match `patient_profile.html`)
- [ ] Editable fields: phone, emergency contacts, allergies

**Test:** Update profile → Verify changes saved

---

## Phase 4: Doctor Features (Build Vertically)

### 4.1 Doctor Dashboard
**Backend:**
- [ ] Create permission class: `IsDoctor`
- [ ] Build API: `GET /api/appointments/` (filter for logged-in doctor)

**Frontend:**
- [ ] Create `pages/DoctorDashboard.jsx` (match `doctor_dashboard.html`)
- [ ] Today's appointments table
- [ ] Quick stats

**Test:** Login as doctor → See dashboard with appointments

### 4.2 Schedule Management
**Backend:**
- [ ] Ensure appointment API supports status updates
- [ ] Build API: `PATCH /api/appointments/<id>/` (doctor can update status)

**Frontend:**
- [ ] Create `pages/ScheduleManagement.jsx` (match `doctor_schedule_management.html`)
- [ ] Weekly calendar view
- [ ] Click appointment to update status

**Test:** Doctor views schedule → Updates appointment status → Verify in DB

### 4.3 Patient Details View
**Backend:**
- [ ] Create permission class: `IsOwnerOrDoctor`
- [ ] Build API: `GET /api/patients/<id>/` (doctor can view any patient)

**Frontend:**
- [ ] Create `pages/PatientDetails.jsx` (match `doctor_patient_detail.html`)
- [ ] Tabs: Medical History, Prescriptions, Documents, Appointments

**Test:** Doctor clicks patient → See full patient info

### 4.4 Create Medical Record
**Backend:**
- [ ] Build API: `POST /api/medical-records/` (after appointment completion)
- [ ] Build API: `POST /api/prescriptions/` (linked to medical record)
- [ ] Option to auto-create medication from prescription

**Frontend:**
- [ ] Create `pages/CreateMedicalRecord.jsx` (match `doctor_create_record.html`)
- [ ] Form: diagnosis, symptoms, treatment notes
- [ ] Repeatable prescription section
- [ ] Submit button creates record + prescriptions

**Test:** Doctor creates record → Verify in DB → Patient can see it

---

## Phase 5: Admin Features (Build Vertically)

### 5.1 Admin Dashboard
**Backend:**
- [ ] Create permission class: `IsAdmin`
- [ ] Build API: `GET /api/admin/users/` (all users with filters)
- [ ] Build stats endpoints (user counts, appointment counts)

**Frontend:**
- [ ] Create `pages/AdminDashboard.jsx` (match `curova_dashboard.html`)
- [ ] System stats cards
- [ ] Recent activity log

**Test:** Login as admin → See dashboard with stats

### 5.2 User Management
**Backend:**
- [ ] Build API: `PATCH /api/admin/users/<id>/deactivate/` (set is_active=False)
- [ ] Build API: `POST /api/admin/users/` (create user)

**Frontend:**
- [ ] Create `pages/UserManagement.jsx` or section in dashboard
- [ ] User list table with filters
- [ ] Actions: Edit, Deactivate, Reset Password

**Test:** Admin deactivates user → User cannot login

### 5.3 Appointments Calendar
**Backend:**
- [ ] Build API: `GET /api/appointments/` (admin can see all)
- [ ] Export CSV functionality

**Frontend:**
- [ ] Create `pages/AppointmentsCalendar.jsx` (match `curova_appointments.html`)
- [ ] Monthly calendar view, color-coded by status
- [ ] Filters, export button

**Test:** Admin views all appointments → Export as CSV

---

## Phase 6: Polish & Deployment

### 6.1 Responsive Design
- [ ] Test all pages on mobile, tablet, desktop
- [ ] Fix responsive issues (hamburger menu, table scrolling)

### 6.2 Error Handling
- [ ] Backend: Proper error responses (400, 401, 403, 404, 409)
- [ ] Frontend: Display user-friendly error messages
- [ ] Loading states, spinners

### 6.3 Security Review
- [ ] Verify SQL injection protection (Django ORM)
- [ ] Verify unauthorized access blocked (permission classes on all views)
- [ ] Test file upload restrictions
- [ ] HTTPS in production

### 6.4 Deployment
- [ ] Create `Dockerfile` for Django
- [ ] Create `Dockerfile` for React
- [ ] Create `docker-compose.yml` (Django, PostgreSQL, Nginx)
- [ ] Deploy to cloud (AWS/Azure/GCP/Heroku)
- [ ] Configure environment variables
- [ ] Set up SSL certificate

### 6.5 Final Push
- [ ] Test entire app end-to-end on production
- [ ] Push all code to Git repos
- [ ] Write README with setup instructions

---

## Daily Workflow

1. **Lock feature scope** - Pick one feature from plan
2. **Backend first** - Build models, serializers, views, test API
3. **Frontend immediately after** - Build UI, integrate API, test flow
4. **Test end-to-end** - Verify feature works completely before moving on
5. **Cross-platform check** - Test on Windows/Linux systems
6. **Commit locally** - Keep backups (no git push yet)

---

## Critical Reminders

- 🔒 **Database schema locked before Phase 2**
- 🎨 **Match demo designs exactly** (colors, fonts, layouts)
- 🤔 **Question functionality** if it doesn't make sense
- 🔄 **Build vertically** not horizontally (no "all backend then all frontend")
- 💻 **Test cross-platform** regularly
- 📦 **No git pushes** until complete
