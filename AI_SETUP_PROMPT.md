# Curova Project - Complete Setup Guide for AI Agent

**Date Created:** March 28, 2026  
**Project Name:** Curova (Healthcare Management Platform)  
**For:** Team member onboarding with AI agent assistance (Antigravity)

---

## 📋 Project Overview

**Curova** is a full-stack healthcare management platform with:
- **Backend:** Django REST Framework (Python) - medical records, appointments, prescriptions, medications, lab tests, notifications
- **Frontend:** React + Vite (JavaScript) - responsive UI for patients, doctors, lab technicians, and admins
- **Database:** PostgreSQL (or SQLite for development)
- **Authentication:** Token-based auth + Google OAuth integration
- **Design System:** CSS variables-based spacing, colors, typography

### Key Features
- **Patient Portal:** Dashboard, appointments, lab results, medical records, medications, document uploads, profile
- **Doctor Portal:** Schedule management, patient list, patient details, medical records, pending lab reports
- **Lab Tech Portal:** Lab test management, results entry
- **Admin Portal:** User management, appointment oversight, system statistics, CSV export
- **Notifications:** In-app notifications with smart routing based on user role
- **Google OAuth:** Sign-in/signup with Google accounts

---

## 🏗️ Architecture Overview

```
WebProject_Curova/
├── backend/                      # Django REST Framework backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                      # Environment configuration (must be created)
│   ├── curova_backend/           # Main Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── pagination.py
│   ├── appointments/             # Appointment management app
│   ├── documents/                # Medical documents app
│   ├── lab_tests/                # Lab test management app
│   ├── medical/                  # Medical records app
│   ├── medications/              # Medication management app
│   ├── messaging/                # Messaging system app (phase 5)
│   ├── notifications/            # Notification system app
│   └── users/                    # User management app (includes auth endpoints)
│
├── frontend/                     # React + Vite frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.local                # Environment config (must be created)
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── pages/                # Page components (organized by role)
│       ├── components/           # Reusable components
│       ├── contexts/             # React Context API
│       ├── services/             # API services
│       ├── hooks/                # Custom hooks
│       ├── styles/               # CSS stylesheets
│       └── assets/               # Static assets
│
├── README.md
├── SETUP.md
├── QUICK_START.md
├── TODO_TRACKER.md               # Task/issue tracking
└── project_docs/                 # Documentation & design files
```

---

## ⚙️ Prerequisites

Before starting, ensure your system has:

1. **Python 3.9+** - [Download](https://www.python.org/downloads/)
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Node.js 16+** & **npm** - [Download](https://nodejs.org/)
   ```bash
   node --version    # Should be 16 or higher
   npm --version
   ```

3. **PostgreSQL 12+** (or use SQLite for dev)
   - **Linux:** `sudo apt-get install postgresql postgresql-contrib`
   - **macOS:** `brew install postgresql`
   - **Windows:** [Download installer](https://www.postgresql.org/download/windows/)
   - **Or use SQLite** (no additional installation needed, comes with Python)

4. **Git** (for version control)

5. **Google OAuth Client ID** (optional, but recommended for full feature testing)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google+ API
   - Create OAuth 2.0 credentials (Web application)
   - Authorized URIs: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8000`
   - Authorized redirect URIs: `http://localhost:8000`
   - Copy the **Client ID**

---

## 🚀 Step-by-Step Setup

### **STEP 1: Extract and Navigate to Project**

```bash
# Extract the zip file
unzip WebProject_Curova.zip
cd WebProject_Curova
```

### **STEP 2: Backend Setup**

#### 2a. Create Python Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 2b. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected packages:** Django, djangorestframework, django-cors-headers, python-decouple, Pillow, psycopg2-binary, google-auth, google-auth-oauthlib, etc.

#### 2c. Create `.env` File

Create `/backend/.env` with the following content:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-custom-secret-key-change-this-in-production-12345678901234567890

# Database Configuration (use ONE of these)
# For PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/curova_db
# For SQLite (development):
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth (leave empty if not using OAuth)
GOOGLE_CLIENT_ID=your_google_client_id_here

# Email Configuration (optional, for production)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Important:** 
- Replace `your-custom-secret-key...` with a random string (at least 50 characters)
- For PostgreSQL, replace `username`, `password`, `localhost`, `5432`, `curova_db` with your actual database credentials
- For Google OAuth, paste the Client ID from Google Cloud Console
- SQLite is simpler for development (no external database needed)

#### 2d. Create Database

**Option A: SQLite (Simpler for Development)**
```bash
# Just run migrations - SQLite database will be created automatically
python manage.py migrate
```

**Option B: PostgreSQL (Production-Ready)**
```bash
# First, create the database in PostgreSQL
# On Linux/macOS:
psql -U postgres
# Then in psql prompt:
CREATE DATABASE curova_db;
CREATE USER curova_user WITH PASSWORD 'curova_password';
ALTER ROLE curova_user SET client_encoding TO 'utf8';
ALTER ROLE curova_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE curova_user SET default_transaction_deferrable TO 'off';
ALTER ROLE curova_user SET default_transaction_level TO 'read committed';
ALTER ROLE curova_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
\q

# Then update .env: DATABASE_URL=postgresql://curova_user:curova_password@localhost:5432/curova_db

# Run migrations
python manage.py migrate
```

#### 2e. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
# Follow prompts:
# Email: admin@curova.com
# Password: testpass123 (or your choice)
# First Name: Admin
# Last Name: User
```

#### 2f. Populate Database with Test Data

The project includes a custom management command to populate test data. This creates:
- 5 patients
- 1 doctor
- 1 lab technician
- 20 appointments (various statuses and times)
- 8 medical records
- 16 prescriptions
- 10 medications
- Lab test results

Run this command:
```bash
python manage.py populate_test_data
```

**If this command doesn't exist**, manually create test users:
```bash
# Create a patient user
python manage.py shell
```

Then in the Django shell:
```python
from django.contrib.auth.models import User
from users.models import Patient, Doctor

# Create patient
patient_user = User.objects.create_user(
    username='testpatient',
    email='testpatient@curova.com',
    password='testpass123',
    first_name='Test',
    last_name='Patient'
)
patient = Patient.objects.create(user=patient_user)

# Create doctor
doctor_user = User.objects.create_user(
    username='testdoctor',
    email='testdoctor@curova.com',
    password='testpass123',
    first_name='Test',
    last_name='Doctor'
)
doctor = Doctor.objects.create(
    user=doctor_user,
    specialization='Internal Medicine',
    license_number='LIC001',
    years_experience=10,
    consultation_fee=150.00
)

exit()
```

### **STEP 3: Frontend Setup**

```bash
cd ../frontend

# Install Node dependencies
npm install

# Verify installation
npm list react react-dom vite
```

**Expected packages:** React, React Router, axios, @react-oauth/google, Vite, etc.

#### 3a. Create `.env.local` File

Create `/frontend/.env.local`:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000/api

# Google OAuth (must match backend)
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

**Important:**
- **VITE_API_URL:** Backend must be running on `http://localhost:8000` with `/api` prefix
- **VITE_GOOGLE_CLIENT_ID:** Must match the backend `.env` file exactly

---

## 🗄️ Database Schema Overview

### Core Models

**User** (Django built-in)
- username, email, password, first_name, last_name, is_active, date_joined

**Patient** (extends User)
- user (OneToOne to User)
- date_of_birth, gender, blood_type, allergies, chronic_conditions
- emergency_contact_name, emergency_contact_phone
- address, city, country

**Doctor** (extends User)
- user (OneToOne to User)
- specialization, license_number, years_experience, consultation_fee
- bio, is_verified

**Appointment**
- patient (ForeignKey to Patient)
- doctor (ForeignKey to Doctor)
- appointment_date, appointment_time
- status (choices: scheduled, confirmed, completed, cancelled, in_progress, etc.)
- notes, created_at, updated_at

**MedicalRecord**
- patient (ForeignKey to Patient)
- doctor (ForeignKey to Doctor)
- appointment (ForeignKey to Appointment, optional)
- diagnosis, treatment_plan, clinical_notes
- recorded_date, updated_at

**Prescription**
- medical_record (ForeignKey to MedicalRecord)
- medication (ForeignKey to Medication)
- dosage, frequency, duration_days
- instructions, created_at

**Medication**
- name, description, dosage_form
- is_active, created_at

**LabTest**
- patient (ForeignKey to Patient)
- doctor (ForeignKey to Doctor)
- appointment (ForeignKey to Appointment)
- test_type, status (pending, in_progress, results_available, cancelled)
- priority (routine, urgent, stat)
- notes, results, created_at, updated_at

**Notification**
- user (ForeignKey to User)
- title, message, notification_type
- related_object_type (string: 'appointment', 'lab_test', 'prescription', etc.)
- related_object_id (integer)
- is_read, created_at

---

## 🔑 Authentication System

### Backend Auth Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register/` | POST | Register new user (patient or doctor) |
| `/auth/login/` | POST | Login with email/password |
| `/auth/google-login/` | POST | Login with Google OAuth token |
| `/auth/logout/` | POST | Logout and invalidate token |
| `/auth/me/` | GET | Get current logged-in user |
| `/auth/profile/` | GET/PUT | Get/update user profile |
| `/auth/change-password/` | POST | Change password |

### Frontend Auth Context (`contexts/AuthContext.jsx`)

The React app uses a centralized auth context that manages:
- Current user object
- Authentication token (stored in localStorage)
- `login(email, password)` function
- `googleLogin(token)` function
- `logout()` function
- `updateUser(data)` function
- `isAuthenticated` boolean

---

## 📱 Running the Application

### Terminal 1: Start Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver 0.0.0.0:8000
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
```

### Terminal 2: Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Access the Application

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Main React app |
| http://localhost:8000/admin | Django admin panel |
| http://localhost:8000/api | API root endpoint |

---

## 🧪 Testing Accounts

After running `populate_test_data`, use these accounts:

### Patients
| Email | Password | Name |
|-------|----------|------|
| testpatient@curova.com | testpass123 | Test Patient |
| pranto.csecu@gmail.com | testpass123 | Pranto Roy |
| janedoe@curova.com | testpass123 | Jane Doe |
| alice@curova.com | testpass123 | Alice Smith |

### Doctor
| Email | Password | Name |
|-------|----------|------|
| testdoctor@curova.com | testpass123 | Test Doctor |

### Admin
| Email | Password | Name |
|-------|----------|------|
| admin@curova.com | testpass123 | Admin User |

### Lab Tech
(Create manually via Django admin if needed)

---

## 🔍 Key Files to Know

### Backend Structure

| File | Purpose |
|------|---------|
| `settings.py` | Django configuration, installed apps, database, auth |
| `urls.py` | Backend route mapping |
| `users/views.py` | Auth endpoints (login, register, profile) |
| `users/serializers.py` | Data serialization for users |
| `appointments/views.py` | Appointment CRUD endpoints |
| `medical/views.py` | Medical records endpoints |
| `lab_tests/views.py` | Lab test endpoints |
| `notifications/views.py` | Notification endpoints |

### Frontend Structure

| File | Purpose |
|------|---------|
| `contexts/AuthContext.jsx` | Central auth state & functions |
| `services/api.js` | Axios instance & API calls |
| `pages/public/Login.jsx` | Login page with OAuth |
| `pages/public/Register.jsx` | Registration page |
| `pages/patient/Dashboard.jsx` | Patient main dashboard |
| `pages/doctor/Dashboard.jsx` | Doctor main dashboard |
| `components/layout/DoctorLayout.jsx` | Doctor navigation wrapper |
| `components/layout/PatientLayout.jsx` | Patient navigation wrapper |
| `styles/variables.css` | Design system (colors, spacing, typography) |

---

## 🔧 Common Setup Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution:** Ensure virtual environment is activated and pip install was successful
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Reinstall
```

### Issue: "CORS errors" - Frontend can't reach backend
**Solution:** Check `CORS_ALLOWED_ORIGINS` in backend `settings.py`. Should include `http://localhost:5173`
```python
# In settings.py around line 60
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### Issue: "Cannot find module" in frontend
**Solution:** Clear node_modules and reinstall
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Google login not configured" error
**Solution:** 
1. Ensure `.env` has `GOOGLE_CLIENT_ID` set
2. Restart Django server (it caches env vars)
3. Verify Client ID matches in both `.env` and `.env.local`

### Issue: Database migration errors
**Solution:** Reset database (development only!)
```bash
python manage.py migrate zero  # Rollback all migrations
python manage.py migrate       # Rerun all migrations
```

### Issue: "Port 8000 is already in use"
**Solution:** Kill existing process or use different port
```bash
# Find and kill process using port 8000
sudo lsof -i :8000
sudo kill -9 <PID>

# Or use different port
python manage.py runserver 0.0.0.0:8001
```

---

## 📊 Role-Based Routing

The app automatically routes users based on their `user_type` after login:

| Role | Dashboard | Navigation Items | Key Features |
|------|-----------|------------------|--------------|
| **Patient** | `/patient/dashboard` | Dashboard, Appointments, Lab Results, Medications, Messages, Profile | View appointments, upload documents, see prescriptions |
| **Doctor** | `/doctor/dashboard` | Dashboard, Schedule, Patients, Pending Reports | Manage appointments, view patient records, create prescriptions |
| **Lab Tech** | `/lab/dashboard` | Dashboard, Tests, Results | Enter lab test results |
| **Admin** | `/admin/dashboard` | Dashboard, Users, Appointments | Manage users, view system stats, export data |

---

## 🛠️ Development Tips

### Enable Django Debug Toolbar (Optional)
```bash
pip install django-debug-toolbar
# Add 'debug_toolbar' to INSTALLED_APPS in settings.py
# Add debug_toolbar urls in urls.py
```

### Access Django Shell
```bash
python manage.py shell
# Now you can directly interact with models:
from users.models import Patient
patients = Patient.objects.all()
print(patients)
```

### View Database Migrations
```bash
python manage.py showmigrations  # Show all migrations
python manage.py showmigrations appointments  # Show specific app migrations
```

### Create a New API Endpoint
1. Add model in `apps/models.py`
2. Create `apps/serializers.py`
3. Create `apps/views.py` (ViewSets)
4. Wire up `apps/urls.py`
5. Add app URL to backend `urls.py`

### Hot Reload in Frontend
Vite automatically hot-reloads when you save files (no restart needed, unlike older tools).

---

## 📝 Next Steps After Setup

1. **Test Login:** Go to `http://localhost:5173/login` and sign in with test account
2. **Explore Patient Dashboard:** Navigate to appointments, medical records, medications
3. **Switch to Doctor:** Sign in as doctor and check schedule management
4. **Test Notifications:** Create appointment and check notification system
5. **Admin Panel:** Go to `http://localhost:8000/admin` with admin credentials
6. **Check API:** Visit `http://localhost:8000/api` to explore endpoints

---

## 📞 Support & Documentation

If you encounter issues not covered here:

1. **Check logs:** Backend errors show in terminal running runserver
2. **Browser console:** Frontend errors show in F12 DevTools → Console tab
3. **Django errors:** Usually include helpful traceback
4. **Review files:**
   - `README.md` - Project overview
   - `QUICK_START.md` - Quick reference
   - `TODO_TRACKER.md` - Known issues and features
   - `project_docs/` - Design documents

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python virtual environment activated
- [ ] `pip install -r requirements.txt` completed
- [ ] `.env` file created with database config
- [ ] `python manage.py migrate` completed
- [ ] `python manage.py createsuperuser` completed
- [ ] Test data populated (or manually created)
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend dependencies installed (`npm install`)
- [ ] `.env.local` created with API URL
- [ ] Frontend running on `http://localhost:5173`
- [ ] Can login as patient/doctor/admin
- [ ] Dashboard loads without errors
- [ ] Can navigate between pages

---

**Once these steps are complete, the application is fully functional and ready for testing!**
