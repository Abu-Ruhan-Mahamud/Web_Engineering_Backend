# Curova Healthcare Management System

A full-stack healthcare management web application for patient appointment booking, medical records management, and healthcare service coordination.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Test Accounts](#test-accounts)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [User Roles & Permissions](#user-roles--permissions)
- [Troubleshooting](#troubleshooting)
- [Development Guidelines](#development-guidelines)

---

## 📖 Project Overview

**Curova** is a healthcare management platform that enables:
- **Patients**: Book appointments, manage medical records, view documents, track medications
- **Doctors**: Manage schedule/availability, view patients, create medical records with prescriptions
- **Admins**: Verify doctors, manage users, oversee system operations

### Implemented Features
1. ✅ User Authentication & Role-Based Access Control (Patient, Doctor, Admin)
2. ✅ Patient Dashboard, Profile, Appointments, Medical Records, Documents
3. ✅ Doctor Dashboard, Schedule Management, Patients List & Detail, Create Medical Records
4. ✅ Appointment Booking & Management
5. ✅ Medical Records with nested Prescriptions
6. ✅ Document Uploads
7. 🔲 Messaging System (Planned — Phase 5)
8. 🔲 Admin Dashboard (Planned — Phase 6)

---

## 🛠 Technology Stack

### Backend
- **Framework**: Django 6.0.2 with Django REST Framework 3.16
- **Database**: PostgreSQL 16+
- **Authentication**: Token-based (DRF `rest_framework.authtoken`)
- **API**: RESTful, JSON responses

### Frontend
- **Framework**: React 19 with Vite 7.2
- **Routing**: React Router DOM v7.13
- **HTTP Client**: Axios 1.13
- **Styling**: Vanilla CSS with Poppins font, custom design system

### Design System Tokens

| Token | Value |
|-------|-------|
| Primary Blue | `#1e3a8a` |
| Primary Teal | `#17a2b8` |
| Teal Hover | `#138496` |
| Light Teal | `#74C3D0` |
| Page Background | `#f5f5f7` |
| Card Border Radius | `16px` |
| Gradient | `linear-gradient(135deg, #74C3D0 0%, #17a2b8 100%)` |
| Font | Poppins (Google Fonts) |

---

## 🏗 System Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  React Frontend │ ◄─────► │  Django Backend  │ ◄─────► │   PostgreSQL    │
│   (Port 5173)   │   REST  │   (Port 8000)    │         │   (Port 5432)   │
└─────────────────┘   API   └─────────────────┘         └─────────────────┘
```

### Database Tables
`users_user` · `users_patient` · `users_doctor` · `appointments_appointment` · `medical_medicalrecord` · `medical_prescription` · `medications_medication` · `documents_document`

---

## ✅ Prerequisites

| Tool | Minimum | Check |
|------|---------|-------|
| Python | 3.12+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | any | `git --version` |

---

## 🚀 Installation & Setup

### Phase 1: Database Setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE curova_db;
CREATE USER curova_user WITH PASSWORD 'curova_pass_2026';
ALTER ROLE curova_user SET client_encoding TO 'utf8';
ALTER ROLE curova_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE curova_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
\q
```

Verify: `psql -U curova_user -d curova_db -h 127.0.0.1` → `curova_db=>` prompt.

### Phase 2: Backend Setup

> **Important**: The virtual environment lives at the **project root** (`WebProject_Curova/venv/`), not inside `backend/`.

```bash
cd WebProject_Curova

# Create & activate venv (skip if venv/ exists)
python -m venv venv
source venv/bin/activate     # Linux/Mac
# OR: venv\Scripts\activate  # Windows

cd backend
pip install -r requirements.txt
```

Verify `backend/.env` exists (see QUICK_START.md for contents).

```bash
python manage.py migrate
python manage.py seed_data        # populates test users, appointments, records
python manage.py runserver        # http://127.0.0.1:8000/
```

### Phase 3: Frontend Setup

```bash
cd WebProject_Curova/frontend
npm install
npm run dev                       # http://localhost:5173/
```

---

## 🎯 Running the Application

### Start Backend (Terminal 1)
```bash
cd WebProject_Curova
source venv/bin/activate
cd backend && python manage.py runserver
```
- 🌐 Backend API: http://127.0.0.1:8000/api/
- 🔧 Admin Panel: http://127.0.0.1:8000/admin/

### Start Frontend (Terminal 2)
```bash
cd WebProject_Curova/frontend
npm run dev
```
- 🌐 Frontend: http://localhost:5173/

---

## 🧪 Test Accounts

The `seed_data` management command creates these accounts:

| Role | Email | Password |
|------|-------|----------|
| Patient | testpatient@curova.com | testpass123 |
| Doctor | testdoctor@curova.com | testpass123 |
| Admin | admin@curova.com | adminpass123 |

**Patient** → http://localhost:5173/patient/dashboard  
**Doctor** → http://localhost:5173/doctor/dashboard  
**Admin** → http://127.0.0.1:8000/admin/

---

## 📡 API Reference

**Base URL**: `http://127.0.0.1:8000/api/`  
**Auth Header**: `Authorization: Token <token>` (token returned by login endpoint)

### Authentication (`/api/auth/`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/register/` | Register patient | No |
| POST | `/auth/login/` | Login (returns token) | No |
| POST | `/auth/logout/` | Logout (deletes token) | Yes |
| GET | `/auth/me/` | Current user info | Yes |
| GET/PUT | `/auth/profile/` | Patient profile | Patient |
| GET | `/auth/dashboard-stats/` | Patient stats | Patient |
| GET | `/auth/doctors/` | List all doctors | Yes |

### Doctor (`/api/auth/doctor/`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/auth/doctor/dashboard-stats/` | Doctor dashboard stats | Doctor |
| GET | `/auth/doctor/profile/` | Doctor profile | Doctor |
| GET/PUT | `/auth/doctor/schedule/` | Schedule / availability | Doctor |
| GET | `/auth/doctor/patients/` | Doctor's patients | Doctor |
| GET | `/auth/doctor/patients/<id>/` | Patient detail | Doctor |

### Appointments (`/api/appointments/`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/appointments/` | List user's appointments | Yes |
| POST | `/appointments/` | Book appointment | Patient |
| GET | `/appointments/<id>/` | Appointment detail | Yes |
| PATCH | `/appointments/<id>/` | Update appointment | Yes |
| DELETE | `/appointments/<id>/` | Cancel appointment | Yes |

### Medical Records (`/api/records/`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/records/` | List user's records | Yes |
| GET | `/records/<id>/` | Record detail | Yes |
| POST | `/records/create/` | Create record + prescriptions | Doctor |

### Documents (`/api/documents/`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/documents/` | List user's documents | Yes |
| POST | `/documents/upload/` | Upload document | Yes |
| GET | `/documents/<id>/` | Document detail | Yes |
| DELETE | `/documents/<id>/` | Delete document | Yes |

---

## 📁 Project Structure

```
WebProject_Curova/
├── venv/                            # Python virtual environment (at project root)
├── backend/
│   ├── manage.py
│   ├── requirements.txt             # pip install -r requirements.txt
│   ├── .env                         # DB creds, CORS, SECRET_KEY
│   ├── curova_backend/              # Django settings, root urls, wsgi
│   ├── users/                       # Auth + patient/doctor profile APIs
│   │   ├── models.py               # User, Patient, Doctor
│   │   ├── views.py                # register, login, logout, me, profiles, doctor views
│   │   ├── serializers.py          # User, Patient, Doctor serializers
│   │   ├── urls.py                 # /api/auth/... (12 paths)
│   │   └── permissions.py          # IsPatient, IsDoctor, IsAdmin, IsOwnerOrDoctor
│   ├── appointments/                # Appointment CRUD
│   ├── medical/                     # Medical records + prescriptions
│   │   ├── models.py               # MedicalRecord, Prescription
│   │   ├── views.py                # list, detail, create
│   │   └── serializers.py          # Read + Create serializers
│   ├── documents/                   # Document uploads
│   └── medications/                 # Medication tracking
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Routes: public, patient/*, doctor/*
│   │   ├── main.jsx                 # Entry point
│   │   ├── pages/
│   │   │   ├── public/              # Home, Login, Register
│   │   │   ├── patient/             # Dashboard, Profile, Appointments,
│   │   │   │                        #   MedicalRecords, Documents
│   │   │   └── doctor/              # Dashboard, ScheduleManagement,
│   │   │                            #   Patients, PatientDetail, CreateRecord
│   │   ├── components/
│   │   │   ├── layout/              # DashboardLayout, PatientLayout,
│   │   │   │                        #   DoctorLayout, Navbar
│   │   │   └── common/              # ProtectedRoute
│   │   ├── services/api.js          # Axios instance (baseURL, token interceptor)
│   │   ├── contexts/AuthContext.jsx  # Auth state, login/logout/register
│   │   └── styles/                  # CSS per feature area
│   ├── package.json
│   └── vite.config.js
│
├── project_docs/                    # PLAN.md, demo HTML mockups
├── README.md                        # ← You are here
├── QUICK_START.md                   # 15-minute setup guide
└── DEVELOPMENT_LOG.md               # Phase-by-phase progress
```

---

## 👥 User Roles & Permissions

### 1. Patient Role
**Registration**: Self-registration via signup form
**Capabilities**:
- Book appointments with doctors
- View appointment history
- Manage medical records
- Upload/download documents
- Update profile information
- View prescribed medications

**Default Access**: Active upon registration

### 2. Doctor Role
**Registration**: Created and verified by Admin
**Capabilities**:
- View assigned appointments
- Update appointment status
- Add medical records for patients
- Prescribe medications
- Set availability schedule
- Manage consultation fees

**Default Access**: Inactive until admin verification

### 3. Admin Role
**Registration**: Created via Django superuser command
**Capabilities**:
- Verify and activate doctor accounts
- Manage all users (view, edit, deactivate)
- View system-wide statistics
- Manage appointments (all users)
- System configuration
- Full database access via Django admin

**Access**: Django admin panel + Custom admin dashboard

---

## 🔧 Troubleshooting

### Issue 1: Cannot connect to database
**Symptoms**: `psycopg2.OperationalError` or "connection refused"
**Solutions**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
# Or check via pg_ctl status

# Verify credentials in .env match database
psql -U curova_user -d curova_db -h 127.0.0.1

# Check PostgreSQL accepts connections
sudo nano /etc/postgresql/14/main/postgresql.conf
# Ensure: listen_addresses = '*' or 'localhost'
```

### Issue 2: Frontend cannot reach backend
**Symptoms**: "Network Error" or CORS errors
**Solutions**:
```bash
# 1. Verify backend is running on port 8000
curl http://127.0.0.1:8000/api/auth/doctors/

# 2. Check CORS settings in backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:5173

# 3. Check frontend API configuration
# frontend/src/services/api.js baseURL should be http://127.0.0.1:8000
```

### Issue 3: Migrations fail
**Symptoms**: `django.db.migrations.exceptions.InconsistentMigrationHistory`
**Solutions**:
```bash
# Reset migrations (CAUTION: Development only)
python manage.py migrate --fake users zero
python manage.py migrate --fake appointments zero
rm -rf */migrations/000*.py
python manage.py makemigrations
python manage.py migrate

# Or drop and recreate database:
psql -U postgres
DROP DATABASE curova_db;
CREATE DATABASE curova_db;
\q
python manage.py migrate
```

### Issue 4: Port already in use
**Symptoms**: "Address already in use"
**Solutions**:
```bash
# Find process using port 8000 (backend)
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
# Update frontend API baseURL accordingly
```

### Issue 5: Static files not loading
**Symptoms**: CSS/JS not loading in frontend
**Solutions**:
```bash
# Clear Vite cache
cd frontend
rm -rf node_modules/.vite
npm run dev

# Clear browser cache
# Chrome: Ctrl+Shift+Delete
```

---

## 💻 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 (Django best practices)
- **JavaScript**: ES6+ standards
- **React**: Functional components with hooks

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/appointment-reminders

# Make changes and commit
git add .
git commit -m "Add appointment reminder feature"

# Push and create pull request
git push origin feature/appointment-reminders
```

### Testing
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests (if configured)
cd frontend
npm run test
```

### API Endpoints Documentation

See the [API Reference](#api-reference) section above for the complete endpoint listing.

**Base URL**: `http://127.0.0.1:8000/api/`  
**Auth Header**: `Authorization: Token <token>`

### Environment Variables
**Never commit**:
- `.env` files
- Database credentials
- Secret keys
- API tokens

**Use**:
- `python-decouple` for backend
- Environment-specific config files

---

## 📞 Support & Resources

### Documentation
- **Django**: https://docs.djangoproject.com/
- **React**: https://react.dev/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Common Commands Cheatsheet
```bash
# Backend
python manage.py runserver           # Start server
python manage.py makemigrations      # Create migrations
python manage.py migrate             # Apply migrations
python manage.py createsuperuser     # Create admin
python manage.py shell               # Django shell

# Frontend
npm run dev                          # Start dev server
npm run build                        # Production build
npm run preview                      # Preview production build

# Database
psql -U curova_user -d curova_db -h 127.0.0.1  # Connect
\dt                                  # List tables
\d users                             # Describe table
\q                                   # Quit
```

---

## 📝 Notes

1. **Development Mode**: Current configuration is for development only
2. **Production**: Requires additional security configurations
3. **Backups**: Regularly backup PostgreSQL database
4. **Updates**: Keep dependencies updated for security patches

---

**Project Status**: ✅ Active Development (Phase 4 complete — Doctor Features)  
**Last Updated**: July 2025  
**See Also**: [QUICK_START.md](QUICK_START.md) · [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)
