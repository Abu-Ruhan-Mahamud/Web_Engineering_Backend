# CUROVA Healthcare Web Application
## Complete Backend Engineering Guide

**Date:** March 28, 2026  
**Audience:** Backend engineering students with basic web knowledge but limited Django experience  
**Purpose:** Comprehensive guide to explain every architectural decision, code pattern, and design principle

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Philosophy](#architecture--philosophy)
3. [Tech Stack Breakdown](#tech-stack-breakdown)
4. [Database Schema](#database-schema)
5. [Authentication System](#authentication-system)
6. [Core Backend Applications](#core-backend-applications)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Key Design Patterns](#key-design-patterns)
9. [Common Operations Walkthrough](#common-operations-walkthrough)
10. [Deployment Architecture](#deployment-architecture)
11. [Testing & Debugging](#testing--debugging)
12. [Frontend Integration](#frontend-integration)

---

## Project Overview

### What is CUROVA?

CUROVA is a **healthcare management web application** that enables:
- **Patients** to book appointments with doctors, view medical records, track medications
- **Doctors** to manage their schedules, view patient histories, create medical records
- **Admins** to oversee all users and system statistics

### Why This Project Matters

Healthcare applications handle sensitive data, require role-based access control, and must handle complex workflows (scheduling, medical records, prescriptions). Building this teaches you enterprise software principles applicable to banking, government, e-commerce, and other regulated systems.

### Real-World Context

During 2-month development, you've deployed a complete full-stack application to production using:
- **Backend**: Django + Django REST Framework on Render
- **Frontend**: React + Vite on Vercel
- **Database**: PostgreSQL on Render (managed service)

This mirrors real startup deployments where backend and frontend are decoupled and can scale independently.

---

## Architecture & Philosophy

### Design Principles

#### 1. **Separation of Concerns**
Each Django "app" handles one domain:
- `users` → Authentication, user profiles, permissions
- `appointments` → Scheduling, booking logic
- `medical` → Doctor notes, prescriptions
- `medications` → Patient medication tracking
- `documents` → File uploads
- `lab_tests` → Lab test management
- `notifications` → In-app notifications
- `messaging` → (Placeholder for future chat)

**Why?** Easier to test, maintain, and extend. A developer working on appointments doesn't break medication logic.

#### 2. **REST API Guidelines**

The backend is 100% **RESTful** - all functionality exposed through HTTP endpoints following conventions:

```
GET    /api/appointments/          → List all appointments
POST   /api/appointments/          → Create appointment
GET    /api/appointments/5/        → Get appointment #5
PATCH  /api/appointments/5/        → Update appointment #5
DELETE /api/appointments/5/        → Delete appointment #5
```

**HTTP Status Codes Used:**
- `200 OK` - Request succeeded, returning data
- `201 CREATED` - Resource created successfully
- `400 BAD REQUEST` - Client sent invalid data
- `401 UNAUTHORIZED` - Authentication required
- `403 FORBIDDEN` - Authenticated but not authorized (permission denied)
- `404 NOT FOUND` - Resource doesn't exist
- `500 INTERNAL SERVER ERROR` - Server error

#### 3. **Token-Based Authentication**

Unlike traditional session cookies (which store state on server), this project uses **DRF Token Authentication**:

```
1. User logs in with email & password
2. Server generates unique 40-character token (stored in database)
3. Client sends Authorization: Token abc123def456... with every request
4. Server validates token, identifies user, checks permissions
```

**Advantage:** Stateless - frontend can be deployed anywhere, no server session state needed. Perfect for decoupled SPA + REST API architecture.

#### 4. **Role-Based Access Control**

User roles determine what they can see/do:

```python
class User(models.Model):
    user_type = CharField(choices=[
        "patient",    # Book appointments, view own records
        "doctor",     # Manage schedule, create records for patients
        "admin",      # View all users, system stats
        "lab_tech"    # Enter lab test results
    ])
```

**Permission Classes:**
```python
# In Django REST Framework
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_only_view(request):
    # Only authenticated doctors can access
    pass
```

### Data Flow Example: Patient Books Appointment

```
1. FRONTEND: User clicks "Book Appointment" on doctor profile
   ↓
2. FRONTEND: Sends POST /api/appointments/ {doctor_id: 5, date: "2026-03-30", time: "14:00"}
   with Authorization header
   ↓
3. BACKEND (appointments/views.py):
   - Verify user is authenticated (token check)
   - Verify user is a patient (IsPatient permission)
   - Validate doctor exists and date/time are valid
   - Check slot isn't already booked (unique constraint)
   ↓
4. BACKEND (appointments/models.py):
   - Create new Appointment record in database
   ↓
5. BACKEND (notifications/helpers.py):
   - Create notification for doctor ("Patient X booked appointment")
   - Create notification for patient ("Appointment confirmed")
   ↓
6. BACKEND: Return 201 CREATED response with appointment details
   ↓
7. FRONTEND: Receive response, show success message
   ↓
8. USER: Sees appointment in personal calendar
```

---

## Tech Stack Breakdown

### Backend Framework: Django

**What is Django?**

Django is a Python web framework that handles:
- **URL routing** - Maps URLs to Python functions
- **ORM** - Object-Relational Mapping converts Python code to SQL
- **Models** - Define database tables in Python
- **Migrations** - Version control for schemas
- **Admin panel** - Auto-generated CRUD interface
- **Security** - CSRF protection, SQL injection prevention

**Django REST Framework (DRF)**

DRF extends Django with REST capabilities:
- `@api_view` decorator to make views handle HTTP requests
- `Serializers` to convert Python objects to/from JSON
- `Viewsets` for automatic CRUD endpoints
- Permission classes for access control
- Automatic request/response validation

### Database: PostgreSQL

**Why PostgreSQL?**

```
✓ Supports complex data types (JSON, arrays, UUID)
✓ ACID compliance (transactions won't corrupt data)
✓ Scales well with proper indexing
✓ Free and open-source
```

**Database Connection String Format:**
```
postgresql://user:password@host:port/database
Example: postgresql://curova_user:secret@db.example.com:5432/curova_db
```

### Web Server: Gunicorn

**What is Gunicorn?**

Gunicorn is a **production WSGI server** - it understands both Python code and HTTP.

```
Request → Gunicorn (converts HTTP to Python) → Django app → Database
  ↓
Response ← Gunicorn (converts Python to HTTP) ← Django app ← Database
```

**Differences from development:**
- Development: `python manage.py runserver` (single-threaded, slow)
- Production: `gunicorn curova_backend.wsgi:application` (multi-process, handles 1000+ concurrent requests)

### Security Layers

#### CORS (Cross-Origin Resource Sharing)
By default, browsers block requests from different domains:
```
Frontend: https://curovafrontend.vercel.app
Backend:  https://curova-backend.onrender.com
```
These are different domains, so requests are blocked unless backend explicitly allows with:
```python
CORS_ALLOWED_ORIGINS = [
    "https://curovafrontend.vercel.app",
    "https://*.vercel.app",  # All Vercel preview URLs
]
```

#### Throttling
```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",    # Unauthenticated users: 30 requests/minute
        "user": "120/minute",   # Authenticated users: 120 requests/minute
    }
}
```
Prevents brute-force attacks and API abuse.

---

## Database Schema

### Schema Diagram (Text)

```
┌─────────────────────────────────────────────────────────┐
│                      USERS                              │
│  (Core authentication & profiles base table)            │
│─────────────────────────────────────────────────────────│
│ • id (PK)                                               │
│ • email (UNIQUE)          → Login username              │
│ • username                → For @mentions               │
│ • password (HASHED)       → PBKDF2 algorithm            │
│ • first_name, last_name                                 │
│ • user_type (CHOICE)      → patient/doctor/admin/lab    │
│ • phone, profile_picture                                │
│ • is_active               → Can be deactivated          │
│ • created_at, updated_at  → Timestamps                  │
└─────────────────────────────────────────────────────────┘
                        ▲
           ┌────────────┼────────────┐
           │            │            │
    (1:1)  │      (1:1) │      (1:1) │
           │            │            │
    ┌──────▼──────┐ ┌──▼──────────┐ ┌──▼────────────┐
    │   PATIENTS  │ │   DOCTORS   │ │  (LAB_TECH)   │
    ├─────────────┤ ├─────────────┤ └───────────────┘
    │ user_id(FK) │ │ user_id(FK) │
    │ DOB         │ │ license#(U) │
    │ gender      │ │ specialz    │
    │ blood_type  │ │ experience  │
    │ allergies[] │ │ working_hrs │
    │ conditions[]│ │ slot_duration
    │ history{}   │ │ fee         │
    └─────────────┘ └─────────────┘


┌──────────────────────────────────────────────────────┐
│              APPOINTMENTS (M:N join table)           │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • patient_id (FK→Patient)  → Who booked             │
│ • doctor_id (FK→Doctor)    → With whom             │
│ • appointment_date         → YYYY-MM-DD            │
│ • appointment_time         → HH:MM:SS              │
│ • status (CHOICE)          → See table below       │
│ • reason, notes            → Medical reason        │
│ • created_at, updated_at                            │
│                                                     │
│ CONSTRAINT: UNIQUE(doctor_id, date, time)          │
│ → Prevents double-booking same slot                 │
└──────────────────────────────────────────────────────┘
                      │
                  (1:1)│
                      ▼
┌──────────────────────────────────────────────────────┐
│            MEDICAL_RECORDS                            │
│  (Doctor's notes after appointment)                   │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • appointment_id (FK→Appointment, 1:1, nullable)     │
│ • patient_id (FK→Patient)                            │
│ • doctor_id (FK→Doctor)                              │
│ • chief_complaint, diagnosis[], symptoms[]           │
│ • examination_notes, treatment_plan                  │
│ • vitals{}  →  {BP: "120/80", HR: 72, Temp: 98.6}   │
│ • follow_up_date                                     │
│ • created_at, updated_at                             │
└──────────────────────────────────────────────────────┘
        │
        │ (1:N)
        ▼
┌──────────────────────────────────────────────────────┐
│              PRESCRIPTIONS (immutable)                │
│  (What was prescribed at this visit)                 │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • medical_record_id (FK→MedicalRecord)               │
│ • medication_name                                    │
│ • dosage         → "500mg"                           │
│ • frequency      → "Twice daily"                     │
│ • duration       → "7 days"                          │
│ • instructions   → Special notes for patient         │
│ • created_at     → When prescribed (immutable)       │
└──────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────┐
│            MEDICATIONS (Current tracking)             │
│  (What patient is currently taking)                   │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • patient_id (FK→Patient)                            │
│ • name, dosage, frequency                            │
│ • is_active      → True=currently taking             │
│ • start_date     → When started                      │
│ • created_at, updated_at  → When tracked             │
└──────────────────────────────────────────────────────┘
        │
        │ (1:N) Reminders for each medication
        ▼
┌──────────────────────────────────────────────────────┐
│         MEDICATION_REMINDERS                          │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • medication_id (FK→Medication)                      │
│ • reminder_time  → "09:00" (HH:MM format)            │
│ • is_enabled     → User can toggle on/off            │
└──────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────┐
│         MEDICAL_DOCUMENTS                             │
│  (Patient-uploaded files: scans, reports)             │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • patient_id (FK→Patient)                            │
│ • document_type  → "xray"/"scan"/"report"/etc        │
│ • file_path      → /media/documents/patient_5/...    │
│ • description    → "2024 chest X-ray"                │
│ • created_at, updated_at                             │
└──────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────┐
│             LAB_TESTS                                 │
│  (Test orders from doctor, results from lab tech)     │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • patient_id (FK→Patient)                            │
│ • doctor_id (FK→Doctor)  → Who ordered it            │
│ • test_type      → "CBC"/"Lipid Panel"/etc           │
│ • status         → "ordered"/"completed"             │
│ • created_at                                         │
└──────────────────────────────────────────────────────┘
        │
        │ (1:1) Test results
        ▼
┌──────────────────────────────────────────────────────┐
│          LAB_TEST_RESULTS                             │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • lab_test_id (FK→LabTest)                           │
│ • results{}      → Actual measured values             │
│ • findings       → What abnormalities noted           │
│ • impression     → Overall clinical interpretation    │
│ • uploaded_by_id (FK→User) → Lab tech who entered    │
│ • uploaded_at                                        │
└──────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────┐
│            NOTIFICATIONS                              │
│  (In-app alerts for all events)                       │
│─────────────────────────────────────────────────────│
│ • id (PK)                                            │
│ • recipient_id (FK→User) → Who receives notification │
│ • title, message                                     │
│ • notification_type → "appointment"/"lab"/"med"/etc  │
│ • is_read          → User can mark as read           │
│ • related_object_type/id → Links to appointment #5   │
│ • created_at                                         │
└──────────────────────────────────────────────────────┘
```

### Why This Schema?

#### User Table as Base

All users (patient, doctor, admin) inherit from Django's `AbstractUser` with added healthcare fields. This is called **Inheritance** rather than separate tables because:

```python
# Bad approach (separate tables):
CREATE TABLE patient_users (id, email, password, DOB, gender, ...);
CREATE TABLE doctor_users (id, email, password, license, specialty, ...);
# Problem: Duplicate email handling, authentication logic in both

# Good approach (inheritance):
CREATE TABLE users (id, email, password, user_type, ...);
CREATE TABLE patients (user_id FK→users, DOB, gender, ...);
CREATE TABLE doctors (user_id FK→users, license, specialty, ...);
# Benefit: One place for auth, users table is single source of truth
```

#### Separate Prescriptions & Medications Tables

```python
# PRESCRIPTIONS table:
# - Doctor prescribes Aspirin 500mg twice daily for 7 days
# - This prescription stays FOREVER (audit trail, immutable)
# - If doctor makes mistake, can't edit, only add a correction note

# MEDICATIONS table:
# - Patient adds "Aspirin 500mg" to current meds
# - Can mark as inactive, edit frequency, update start date
# - Reflects what patient is ACTUALLY taking NOW
```

**Why separate?**
- Prescriptions = Historical audit trail (compliance/legal)
- Medications = Current state for patient tracking
- One prescription could spawn multiple medication entries if taken for different conditions

#### Unique Constraint on Appointments

```python
CONSTRAINT: UNIQUE(doctor_id, appointment_date, appointment_time)
```

This prevents the database from accepting two appointments at the same slot:
```
Doctor 5, Jan 15, 2:00 PM → ALLOWED (first booking)
Doctor 5, Jan 15, 2:00 PM → REJECTED (slot already taken)
```

The database enforces this at the lowest level - even if application code has bugs, database rejects invalid data.

---

## Authentication System

### How Login Works (Step-by-Step)

#### Step 1: User Submits Credentials

```javascript
// Frontend (React)
const response = await axios.post("/api/auth/login/", {
    email: "doctor@curova.com",
    password: "securepass123"
});
```

#### Step 2: Backend Validates

```python
# Backend (users/views.py)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # Check format
    
    user = serializer.validated_data["user"]  # Find user & check password
    token, _ = Token.objects.get_or_create(user=user)  # Generate/get token
    
    return Response({
        "token": token.key,
        "user": UserSerializer(user).data,
    })
```

**What `is_valid(raise_exception=True)` does:**

```python
# In users/serializers.py (LoginSerializer)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if not user.check_password(data['password']):  # Compare hashed password
                raise ValidationError("Invalid password")
        except User.DoesNotExist:
            raise ValidationError("User not found")
        
        data['user'] = user
        return data
```

#### Step 3: Token Generation & Storage

```python
# Server side: Generates 40-char unique string
Token(user=user).save()
# Result: Token.objects.create(user=user5) 
#         → "a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2"

# Database:
# | token_key | user_id | created_at |
# | a3b4...   | 5       | 2026-03-28 |
```

#### Step 4: Response to Frontend

```json
{
  "token": "a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2",
  "user": {
    "id": 5,
    "email": "doctor@curova.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "doctor"
  }
}
```

#### Step 5: Frontend Stores Token

```javascript
// React
localStorage.setItem("token", "a3b4c5d6...");  // Save for later
```

### Authenticated Requests

#### How Each API Call Uses Token

```javascript
// Frontend sends token WITH EVERY REQUEST
const token = localStorage.getItem("token");
axios.defaults.headers.common["Authorization"] = `Token ${token}`;

// Every subsequent request includes:
// Authorization: Token a3b4c5d6...
```

```python
# Backend validates token for each request
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Enforces token check
def me_view(request):
    # At this point, request.user is already populated
    # by TokenAuthentication middleware
    return Response(UserSerializer(request.user).data)
```

### Token Lifecycle

```
1. User logs in
   ↓
2. Token created: {key: "abc123...", user_id: 5, created: 2026-03-28}
   ↓
3. Token stored in localStorage
   ↓
4. On every API call, token sent in header
   ↓
5. Server validates: "Is this token in database? Is it tied to an active user?"
   ↓
6. Yes → Grant access to request.user = User(id=5)
   No → Return 401 Unauthorized
   ↓
7. User logs out → Token deleted from database
   ↓
8. Next API call with old token → Server can't find it → 401 Unauthorized → Frontend redirects to login
```

### Permission Classes

```python
# In users/permissions.py

class IsPatient(BasePermission):
    """Allow access only to patients."""
    def has_permission(self, request, view):
        # request.user is already identified by token
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == "patient"
        )

# Usage in views
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPatient])
def patient_only_endpoint(request):
    # If user is not authenticated → 401
    # If authenticated but not patient (e.g., doctor) → 403 Forbidden
    pass
```

### Google OAuth (Sign-in with Google)

```
Frontend gets Google credential → POST /api/auth/google-login/ 
                                  ↓
Backend verifies with Google servers (not fake tokens!)
                                  ↓
If valid: Find/create user with that email
                                  ↓
Generate token same as regular login
```

**Key security feature:** We don't trust the frontend. Backend **always verifies** with Google that the token is real.

---

## Core Backend Applications

### 1. USERS App (Authentication & Profiles)

#### Models
- `User` - Base auth model (can be patient/doctor/admin)
- `Patient` - 1:1 extension with DOB, allergies, conditions
- `Doctor` - 1:1 extension with license, specialty, schedule

#### Key Files
- `models.py` - User, Patient, Doctor definitions
- `views.py` - Login, register, profile endpoints
- `serializers.py` - Convert User objects to JSON
- `permissions.py` - IsPatient, IsDoctor, IsAdmin classes
- `urls.py` - Route definitions

#### Important Views (Endpoints)

```python
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """POST /api/auth/register/
    Anyone can register. Creates User + Patient.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()  # Saves User to DB
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": ...})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """POST /api/auth/logout/
    Deletes the user's token (invalidates all sessions).
    """
    request.user.auth_token.delete()
    return Response({"detail": "Logged out successfully."})

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsPatient])
def patient_profile_view(request):
    """GET /api/auth/profile/ → Returns patient profile
    PUT /api/auth/profile/ → Updates profile (DOB, allergies, etc.)
    """
    patient = request.user.patient_profile
    if request.method == "GET":
        serializer = PatientProfileSerializer(patient)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = PatientProfileSerializer(patient, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_profile_view(request):
    """GET /api/auth/doctor/profile/
    PUT /api/auth/doctor/profile/
    """
    doctor = request.user.doctor_profile
    # Similar logic to patient_profile_view
    ...

@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_list_view(request):
    """GET /api/auth/doctors/?specialization=cardiology
    
    Public endpoint - anyone can see available doctors to book with.
    Optionally filter by specialization.
    """
    doctors = Doctor.objects.filter(user__is_active=True)
    
    specialization = request.query_params.get("specialization")
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    # Paginate for perf (returns 20 at a time)
    page = paginate_queryset(doctors, request)
    serializer = DoctorListSerializer(page, many=True)
    return get_paginated_response(serializer.data)
```

---

### 2. APPOINTMENTS App (Booking & Scheduling)

#### Models
- `Appointment` - Links patient + doctor + date/time + status

#### Status Flow

```
SCHEDULED → Patient books but hasn't confirmed
   ↓
CONFIRMED → Patient/doctor confirmed, appointment is set
   ↓
IN_PROGRESS → Appointment time has arrived, they're meeting
   ↓
COMPLETED → Appointment finished (doctor can create medical record)
   ↓

OR → CANCELLED → Either party cancelled
OR → NO_SHOW → Appointment time passed but nobody showed up
OR → RESCHEDULED → Moved to different date
```

#### Key Views

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booked_slots(request):
    """GET /api/appointments/booked-slots/?doctor_id=5&date=2026-04-15
    
    Returns times ALREADY BOOKED for that doctor on that date.
    Frontend uses this to gray out unavailable slots.
    
    Example response:
    {
      "booked_times": ["09:00", "09:30", "14:00"]
    }
    """
    doctor_id = request.query_params.get("doctor_id")
    date = request.query_params.get("date")
    
    booked = Appointment.objects.filter(
        doctor_id=doctor_id,
        appointment_date=date,
        status__in=["scheduled", "confirmed", "in_progress"]
    ).values_list('appointment_time', flat=True)
    
    return Response({"booked_times": list(booked)})

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    """GET /api/appointments/
    Returns appointments relevant to user:
    - If patient: their own appointments
    - If doctor: their appointments with patients
    
    POST /api/appointments/
    Patient creates new appointment booking.
    """
    if request.method == "GET":
        if hasattr(request.user, 'patient_profile'):
            # Patient: show their appointments
            appts = Appointment.objects.filter(patient=request.user.patient_profile)
        elif hasattr(request.user, 'doctor_profile'):
            # Doctor: show their appointments
            appts = Appointment.objects.filter(doctor=request.user.doctor_profile)
        else:
            return Response([])  # Admin sees nothing by default
        
        page = paginate_queryset(appts, request)
        serializer = AppointmentSerializer(page, many=True)
        return get_paginated_response(serializer.data)
    
    elif request.method == "POST":
        # Verify user is patient
        if not hasattr(request.user, 'patient_profile'):
            return Response({"error": "Only patients can book"}, status=403)
        
        serializer = CreateAppointmentSerializer(
            data=request.data,
            context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        
        # Create notifications
        patient = request.user.patient_profile
        doctor = appointment.doctor
        Notification.objects.create(
            recipient=doctor.user,
            title=f"New appointment from {patient.user.first_name}",
            message=f"Patient {patient.user.email} booked for {appointment.appointment_date}",
            notification_type="appointment",
            related_object_type="Appointment",
            related_object_id=appointment.id
        )
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=201
        )

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    """GET /api/appointments/5/
    Returns specific appointment details.
    
    PATCH /api/appointments/5/
    Update status or other details.
    Only allowed for patient or doctor in that appointment.
    """
    appointment = get_object_or_404(Appointment, id=pk)
    
    # Check permission
    is_patient_in_appt = (
        hasattr(request.user, 'patient_profile') and
        appointment.patient == request.user.patient_profile
    )
    is_doctor_in_appt = (
        hasattr(request.user, 'doctor_profile') and
        appointment.doctor == request.user.doctor_profile
    )
    
    if not (is_patient_in_appt or is_doctor_in_appt):
        return Response({"error": "Forbidden"}, status=403)
    
    if request.method == "GET":
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    
    elif request.method == "PATCH":
        serializer = AppointmentSerializer(
            appointment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # If status changed, notify other party
        if "status" in request.data:
            if is_patient_in_appt:
                notify_user = appointment.doctor.user
            else:
                notify_user = appointment.patient.user
            
            Notification.objects.create(
                recipient=notify_user,
                title=f"Appointment {request.data['status']}",
                notification_type="appointment",
            )
        
        return Response(AppointmentSerializer(appointment).data)
```

#### Validation Logic

```python
# In appointments/serializers.py
class CreateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
    
    def validate(self, data):
        doctor = data['doctor']
        date = data['appointment_date']
        time = data['appointment_time']
        
        # Validation 1: Date must be in future
        if date < timezone.now().date():
            raise ValidationError("Can't book in the past")
        
        # Validation 2: Doctor must be available that day
        day_name = date.strftime('%A').lower()  # "Monday" → "monday"
        if day_name not in doctor.available_days:
            raise ValidationError(f"Doctor not available on {day_name}s")
        
        # Validation 3: Time must be within working hours
        if not (doctor.working_hours_start <= time <= doctor.working_hours_end):
            raise ValidationError("Time outside doctor's working hours")
        
        # Validation 4: Time must align to slot boundary
        # Example: slot_duration=30, working from 9:00
        # 9:00 ✓, 9:30 ✓, 9:15 ✗ (not on 30min boundary)
        start_seconds = doctor.working_hours_start.hour * 3600 + doctor.working_hours_start.minute * 60
        time_seconds = time.hour * 3600 + time.minute * 60
        offset = (time_seconds - start_seconds) % (doctor.slot_duration * 60)
        if offset != 0:
            raise ValidationError("Time must be on slot boundary")
        
        # Validation 5: Slot not already booked
        exists = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            status__in=["scheduled", "confirmed"]
        ).exists()
        if exists:
            raise ValidationError("Slot already booked")
        
        return data
```

---

### 3. MEDICAL App (Patient Records)

#### Models
- `MedicalRecord` - Doctor notes after appointment
- `Prescription` - What was prescribed (immutable)

#### Key Views

```python
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def medical_record_list(request):
    """GET /api/records/
    POST /api/records/
    """
    if request.method == "GET":
        if hasattr(request.user, 'patient_profile'):
            # Patient sees their records
            records = MedicalRecord.objects.filter(
                patient=request.user.patient_profile
            )
        elif hasattr(request.user, 'doctor_profile'):
            # Doctor sees records they created
            records = MedicalRecord.objects.filter(
                doctor=request.user.doctor_profile
            )
        else:
            return Response([])
        
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":
        # Only doctors can create
        if not hasattr(request.user, 'doctor_profile'):
            return Response({"error": "Only doctors"}, status=403)
        
        serializer = MedicalRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save(doctor=request.user.doctor_profile)
        
        # Notify patient
        Notification.objects.create(
            recipient=record.patient.user,
            title="New medical record",
            message="Doctor created a record from your recent appointment",
            notification_type="system"
        )
        
        return Response(
            MedicalRecordSerializer(record).data,
            status=201
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def create_medical_record(request):
    """Simplified endpoint for doctors to create records after appointment."""
    serializer = CreateMedicalRecordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    record = MedicalRecord.objects.create(
        patient=serializer.validated_data['patient'],
        doctor=request.user.doctor_profile,
        appointment=serializer.validated_data.get('appointment'),
        chief_complaint=serializer.validated_data.get('chief_complaint', ''),
        diagnosis=serializer.validated_data.get('diagnosis', []),
        symptoms=serializer.validated_data.get('symptoms', []),
        examination_notes=serializer.validated_data.get('examination_notes', ''),
        treatment_plan=serializer.validated_data.get('treatment_plan', ''),
    )
    
    # Create prescriptions if provided
    prescriptions_data = serializer.validated_data.get('prescriptions', [])
    for rx_data in prescriptions_data:
        Prescription.objects.create(medical_record=record, **rx_data)
    
    return Response(
        MedicalRecordSerializer(record).data,
        status=201
    )
```

---

### 4. NOTIFICATIONS App

#### Use Cases

```
1. Appointment booked
   → Notify doctor: "Patient John booked with you on April 15"
   
2. Appointment confirmed
   → Notify patient: "Your appointment confirmed with Dr. Smith"
   
3. Lab results ready
   → Notify patient: "Your blood test results are in"
   
4. Prescription created
   → Notify patient: "Dr. Smith prescribed Aspirin"
   
5. Medication reminder
   → Notify patient: "Time to take your blood pressure medication"
```

#### Key Views

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """GET /api/notifications/
    Returns paginated notifications for logged-in user.
    """
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Optional filters
    is_read = request.query_params.get('is_read')
    if is_read is not None:
        notifications = notifications.filter(is_read=is_read == 'true')
    
    notification_type = request.query_params.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    page = paginate_queryset(notifications, request)
    serializer = NotificationSerializer(page, many=True)
    return get_paginated_response(serializer.data)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def notification_read(request, pk):
    """PATCH /api/notifications/5/read/
    Mark specific notification as read.
    """
    notification = get_object_or_404(Notification, id=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return Response(NotificationSerializer(notification).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """POST /api/notifications/mark-all-read/
    Marks all notifications for user as read.
    """
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return Response({"marked_read": count})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """GET /api/notifications/unread-count/
    Returns count of unread notifications.
    Used by frontend to show badge on bell icon.
    """
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response({"unread_count": count})
```

#### Creating Notifications (Helper)

```python
# In notifications/helpers.py
def create_notification(recipient, title, message, notification_type="system", obj=None):
    """
    Helper to consistently create notifications throughout the app.
    
    Usage:
    create_notification(
        recipient=patient.user,
        title="Appointment confirmed",
        message="Your appointment with Dr. Smith is confirmed",
        notification_type="appointment",
        obj=appointment
    )
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_type=obj.__class__.__name__ if obj else "",
        related_object_id=obj.id if obj else None
    )
```

---

## API Endpoints Reference

### Auth Endpoints

```
POST   /api/auth/register/          → Create account
       Input:  {email, password, first_name, last_name}
       Output: {token, user{...}}
       
POST   /api/auth/login/             → Get token
       Input:  {email, password}
       Output: {token, user{...}}
       
POST   /api/auth/google-login/      → Auth with Google
       Input:  {credential: "<Google JWT>"}
       Output: {token, user{...}}
       
POST   /api/auth/logout/            → Invalidate token
       Auth:   Required
       Output: {detail: "success"}
       
GET    /api/auth/me/                → Current user info
       Auth:   Required
       Output: {id, email, user_type, ...}
       
PUT    /api/auth/change-password/   → Change password
       Auth:   Required
       Input:  {old_password, new_password}
       Output: {detail, token: "<new token>"}
```

### Appointment Endpoints

```
GET    /api/appointments/           → List my appointments
       Auth:   Required (patient/doctor)
       Query:  ?status=confirmed&date_from=2026-04-01
       Output: {count, next, previous, results: [{...}]}
       
POST   /api/appointments/           → Book appointment
       Auth:   Required (patient only)
       Input:  {doctor_id, appointment_date, appointment_time, reason}
       Output: {...appointment object...}
       
GET    /api/appointments/5/         → Get specific appointment
       Auth:   Required
       Output: {...appointment object...}
       
PATCH  /api/appointments/5/         → Update appointment status
       Auth:   Required
       Input:  {status: "confirmed"}
       Output: {...appointment object...}
       
GET    /api/appointments/booked-slots/
       Query:  ?doctor_id=5&date=2026-04-15
       Output: {booked_times: ["09:00", "09:30"]}
```

### Medical Records Endpoints

```
GET    /api/records/                → My medical records
       Auth:   Required
       Output: [{...record...}, ...]
       
POST   /api/records/                → Create record (doctor)
       Auth:   Required (doctor)
       Input:  {patient_id, diagnosis[], symptoms[], ...}
       Output: {...record...}
       
GET    /api/records/5/              → Get specific record
       Auth:   Required
       Output: {...record...}
       
PATCH  /api/records/5/              → Update record
       Auth:   Required (doctor only)
       Input:  {treatment_plan, ...}
       Output: {...record...}
```

### Medications Endpoints

```
GET    /api/medications/            → List patient medications
       Auth:   Required (patient)
       Output: [{...med...}, ...]
       
POST   /api/medications/            → Add medication
       Auth:   Required (patient)
       Input:  {name, dosage, frequency}
       Output: {...medication...}
       
PATCH  /api/medications/5/          → Update medication
       Auth:   Required (patient)
       Input:  {is_active: false}
       Output: {...medication...}
```

### Lab Tests Endpoints

```
GET    /api/lab-tests/              → List lab tests
       Auth:   Required
       Output: [{...test...}, ...]
       
POST   /api/lab-tests/              → Order test (doctor)
       Auth:   Required (doctor)
       Input:  {patient_id, test_type}
       Output: {...test...}
       
GET    /api/lab-tests/5/            → Get test details
       Auth:   Required
       Output: {...test...}
       
POST   /api/lab-tests/5/result/     → Upload results (lab tech)
       Auth:   Required (lab_tech)
       Input:  {results{}, findings, impression}
       Output: {...test with results...}
```

### Notifications Endpoints

```
GET    /api/notifications/          → List notifications
       Auth:   Required
       Query:  ?is_read=false&type=appointment
       Output: {count, next, previous, results: [{...}]}
       
PATCH  /api/notifications/5/read/   → Mark as read
       Auth:   Required
       Output: {...notification...}
       
POST   /api/notifications/mark-all-read/
       Auth:   Required
       Output: {marked_read: 15}
       
GET    /api/notifications/unread-count/
       Auth:   Required
       Output: {unread_count: 3}
       
DELETE /api/notifications/5/        → Delete notification
       Auth:   Required
       Output: (no content)
```

---

## Key Design Patterns

### 1. Serializers (Data Transformation)

**Problem:** Database returns Python objects, frontend needs JSON.

```python
# Database
doctor = Doctor.objects.get(id=5)
print(doctor)  # <Doctor: Dr. John Doe (Cardiology)>

# Frontend expects JSON
# {"id": 5, "name": "John Doe", "specialization": "Cardiology", ...}

# Solution: Serializer
class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'user__first_name', 'user__last_name', 'specialization']

serializer = DoctorSerializer(doctor)
serializer.data  # {"id": 5, "first_name": "John", "last_name": "Doe", ...}
json.dumps(serializer.data)  # JSON string for HTTP response
```

**Validation Serializers:**
```python
class LoginSerializer(serializers.Serializer):
    """Validates incoming login data."""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        # Check user exists and password is correct
        # Raise ValidationError if not
        return data
```

### 2. Permission Classes (Authorization)

```python
# Rather than writing this in every view:
if request.user.user_type != "doctor":
    return Response({"error": "Forbidden"}, status=403)

# Use a reusable permission class:
class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == "doctor"

# Apply to any view:
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_only_view(request):
    # Automatically checks permission before executing
    pass
```

### 3. Pagination (Large Data Sets)

```python
# Problem: If we return all 10,000 notifications at once, network/memory explode

# Solution: Return 20 at a time
GET /api/notifications/?page=1
{
  "count": 10000,
  "next": "http://.../api/notifications/?page=2",
  "previous": null,
  "results": [{...}, {...}, ..., {...}]  // 20 items
}

GET /api/notifications/?page=2
{
  "count": 10000,
  "next": "http://.../api/notifications/?page=3",
  "previous": "http://.../api/notifications/?page=1",
  "results": [{...}, {...}, ..., {...}]  // Items 21-40
}
```

### 4. Status & State Management

```python
# Rather than boolean flags

# BAD:
class Appointment:
    is_booked = True
    is_confirmed = False
    is_completed = False
    is_cancelled = False
# What if is_booked=False and is_confirmed=True? Contradiction!

# GOOD:
class Appointment:
    status = CharField(choices=['scheduled', 'confirmed', 'completed', 'cancelled'])
# Only ONE status at a time, impossible to be in inconsistent state
```

### 5. Immutable Records (Audit Trails)

```python
# Prescriptions are IMMUTABLE
class Prescription(models.Model):
    # No update/delete allowed after creation
    # Future: Add constraint at DB level

# Why?
# Insurance: "Proof you prescribed this specific medication on this date"
# Legal: "We have an audit trail of every prescription"
# Prevents accidental data corruption

# If doctor realizes they made a mistake:
# 1. Create NEW amended prescription
# 2. Keep old one as historical record
# 3. Both exist in database forever
```

---

## Common Operations Walkthrough

### Operation 1: Patient Books Appointment

```
Step 1: Frontend loads doctor's profile
GET /api/auth/doctors/5/
→ Returns doctor details, schedule, working hours, slot duration

Step 2: User selects date on calendar
Frontend calls:
GET /api/appointments/booked-slots/?doctor_id=5&date=2026-04-15
→ Returns ["09:00", "10:00"] (already booked times)
→ Frontend grays out those times in UI

Step 3: User clicks available time and submits
Frontend POSTs:
POST /api/appointments/
{
  "doctor": 5,
  "appointment_date": "2026-04-15",
  "appointment_time": "14:00",
  "reason": "Chest pain"
}
With Authorization: Token abc123...

Step 4: Backend validates
- Is user authenticated? (check token)
- Is user a patient? (check user_type)
- Is doctor available on Monday? (check available_days)
- Is 14:00 within 09:00-17:00? (check working_hours)
- Is 14:00 on 30-min boundary? (check slot_duration)
- Is slot not already booked? (check unique constraint)

Step 5: Backend creates appointment
INSERT INTO appointments 
(patient_id, doctor_id, appointment_date, appointment_time, status, reason, created_at)
VALUES (10, 5, 2026-04-15, 14:00, 'scheduled', 'Chest pain', NOW())

Step 6: Backend creates notifications
INSERT INTO notifications (recipient_id, title, message, notification_type, related_object_type, related_object_id)
VALUES (5, 'New appointment from John Doe', '...', 'appointment', 'Appointment', 417)  // doctor

INSERT INTO notifications (recipient_id, title, message, notification_type, related_object_type, related_object_id)
VALUES (10, 'Appointment booked', '...', 'appointment', 'Appointment', 417)  // patient

Step 7: Backend returns appointment details
Status: 201 CREATED
{
  "id": 417,
  "patient": {...},
  "doctor": {...},
  "appointment_date": "2026-04-15",
  "appointment_time": "14:00:00",
  "status": "scheduled",
  "reason": "Chest pain",
  "created_at": "2026-03-28T14:30:00Z"
}

Step 8: Frontend receives response
- Shows success toast
- Updates appointments list
- Redirects to appointments page or shows details modal
```

### Operation 2: Doctor Creates Medical Record After Appointment

```
Step 1: Doctor finishes appointment with patient John, navigates to create record

Step 2: Doctor clicks "Create Medical Record"
Frontend shows form for:
- Chief complaint: "Patient complained of chest pain"
- Diagnosis: ["Anxiety", "Acid reflux"]
- Symptoms: ["chest pain", "shortness of breath"]
- Examination notes: "ECG normal, vitals stable"
- Treatment plan: "Prescribed antacid, referred to cardiology"
- Vitals: {BP: "120/80", HR: 72, Temp: 98.6}
- Prescriptions: [
    {medication_name: "Omeprazole", dosage: "20mg", frequency: "Twice daily", duration: "14 days"},
    {medication_name: "Sertraline", dosage: "50mg", frequency: "Once daily"}
  ]

Step 3: Doctor submits form
Frontend POSTs:
POST /api/records/
{
  "patient": 10,
  "appointment": 417,
  "chief_complaint": "...",
  "diagnosis": ["Anxiety", "Acid reflux"],
  "symptoms": ["chest pain", "SOB"],
  "examination_notes": "...",
  "treatment_plan": "...",
  "vitals": {...},
  "prescriptions": [...]
}
With Authorization: Token def456... (doctor's token)

Step 4: Backend validates
- Is user authenticated? (check token)
- Is user a doctor? (check user_type)
- Does patient exist? (check Patient)
- Does appointment exist? (check Appointment)

Step 5: Backend creates record
INSERT INTO medical_records 
(patient_id, doctor_id, appointment_id, chief_complaint, diagnosis, ...)
VALUES (10, 5, 417, '...', '["Anxiety", "Acid reflux"]', ...)

record_id = 892

Step 6: Backend creates prescriptions
FOR EACH prescription:
  INSERT INTO prescriptions (medical_record_id, medication_name, dosage, frequency, ...)
  VALUES (892, 'Omeprazole', '20mg', 'Twice daily', ...)
  → prescription_id = 1540

  INSERT INTO prescriptions ...
  → prescription_id = 1541

Step 7: Backend creates notification to patient
INSERT INTO notifications (recipient_id, title, message, notification_type)
VALUES (10, 'Medical record created', 'Dr. Smith created your medical record', 'system')

Step 8: Backend returns created record with prescriptions
Status: 201 CREATED
{
  "id": 892,
  "patient": 10,
  "doctor": 5,
  "appointment": 417,
  "chief_complaint": "...",
  "diagnosis": ["Anxiety", "Acid reflux"],
  "prescriptions": [
    {"id": 1540, "medication_name": "Omeprazole", "dosage": "20mg", ...},
    {"id": 1541, "medication_name": "Sertraline", "dosage": "50mg", ...}
  ],
  "created_at": "2026-03-28T15:45:00Z"
}

Step 9: Frontend receives response
- Shows success message
- Can display created record with prescriptions
- Frontend might auto-create Medication entries for patient to track
```

---

## Deployment Architecture

### Development vs Production

#### Development (Local Machine)
```
python manage.py runserver
↓
Django starts single-threaded server on http://localhost:8000
↓
Perfect for debugging, but can only handle 1 request at a time
```

#### Production (Render)
```
gunicorn curova_backend.wsgi:application
↓
Gunicorn starts multi-process server on 0.0.0.0:10000
↓
Can handle 100+ concurrent requests (via multiple worker processes)
↓
Production database: PostgreSQL (managed)
↓
Automatic logs, monitoring, auto-restart on crash
```

### Environment Variables

```python
# In settings.py
SECRET_KEY = config("SECRET_KEY")  # Secret signing key
DEBUG = config("DEBUG", default=False, cast=bool)  # Debug mode
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")  # Allowed domains
DATABASE_URL = config("DATABASE_URL")  # PostgreSQL connection string
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")  # Google OAuth
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(",")  # Frontend domains
```

**Why environment variables?**
- Never hardcode secrets in code (especially not in git!)
- Different servers have different secrets
- Easy to rotate secrets without changing code

### Migrations

```
Local development:
  python manage.py makemigrations  → Creates migration files (define changes)
  python manage.py migrate         → Applies migrations to local database

Production deployment:
  wsgi.py auto-runs migrations on startup (see lines added for Render)
  ↓
  Database schema auto-updates when new code is deployed
  ↓
  Zero downtime (Django migrations are designed for this)
```

### Auto Docker Deployment

```
1. You push code to GitHub
   git push origin main
   
2. Render webhook receives notification
   
3. Render:
   a. Pulls latest code from GitHub
   b. Installs dependencies: pip install -r requirements.txt
   c. Runs migrations: python manage.py migrate
   d. Starts server: gunicorn curova_backend.wsgi:application
   
4. Your API is live at https://curova-backend.onrender.com
```

---

## Testing & Debugging

### Common Error Messages

#### 400 Bad Request
```
Frontend: Invalid request data format
Example error:
{
  "email": ["This field may not be blank."],
  "password": ["Ensure this field has at least 8 characters."]
}

Debugging:
- Check JSON syntax
- Verify required fields are present
- Validate data types (email vs string, number vs string)
```

#### 401 Unauthorized
```
Problem: Missing or invalid authentication token

Debugging:
- Is token in Authorization header? (Authorization: Token abc123...)
- Has user logged in?
- Did user delete account?
- Did token expire/get invalidated?

Solution:
- Redirect user to login
- Refresh token if expired
```

#### 403 Forbidden
```
Problem: Authenticated but insufficient permissions

Example:
- Doctor trying to access patient-only endpoints
- Lab tech trying to create medical records

Debugging:
- Check user_type or permission class requirements
- Verify user role is correct in database
```

#### 404 Not Found
```
Problem: Resource doesn't exist or URL is wrong

Debugging:
- Check URL spelling and parameters
- Verify resource ID exists: GET /api/doctors/999/ (if doctor #999 doesn't exist)
- Check if resource was deleted

Solution:
- Check database for resource
- Use correct endpoint URL
```

#### 500 Internal Server Error
```
Problem: Backend code crashed

Debugging:
- Check Render logs for Python traceback
- Common causes:
  * Missing database field
  * Typo in code
  * Database connection down
  * Required environment variable not set
```

### Debugging Tools

#### Django Shell
```bash
python manage.py shell

>>> from users.models import User
>>> User.objects.all()  # List all users
<QuerySet [<User: john@email.com>, <User: jane@email.com>]>

>>> user = User.objects.get(email="john@email.com")
>>> user.user_type  # Check user type
'patient'

>>> from appointments.models import Appointment
>>> Appointment.objects.filter(doctor_id=5, status='scheduled')
# Check specific appointments
```

#### Django Admin Panel
```
http://localhost:8000/admin/
(or production: https://curova-backend.onrender.com/admin/)

Login with admin credentials
- View/edit all database records
- Create test data
- Check model relationships
```

#### Logs (Render)
```
Render Dashboard → Your Service → Logs
Shows all HTTP requests and Python errors in real-time
Invaluable for debugging production issues
```

---

## Frontend Integration

### API Interaction Pattern

```javascript
// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Auto-add token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Example usage in React component
import api from './services/api';

function AppointmentBooking() {
  const handleBooking = async (doctorId, date, time) => {
    try {
      const response = await api.post('/appointments/', {
        doctor: doctorId,
        appointment_date: date,
        appointment_time: time,
        reason: 'Regular checkup'
      });
      console.log('Booked!', response.data);
    } catch (error) {
      console.error('Error:', error.response?.data);
    }
  };
}
```

### Handling Auth

```javascript
// Login flow
async function login(email, password) {
  const response = await api.post('/auth/login/', {email, password});
  localStorage.setItem('token', response.data.token);
  localStorage.setItem('user', JSON.stringify(response.data.user));
  return response.data;
}

// Logout flow
async function logout() {
  await api.post('/auth/logout/');  // Invalidates token on server
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  // Redirect to login page
}

// Check auth on app load
useEffect(() => {
  const token = localStorage.getItem('token');
  if (!token) {
    redirectToLogin();
  } else {
    // Validate token still valid
    api.get('/auth/me/').catch(() => redirectToLogin());
  }
}, []);
```

### Error Handling

```javascript
async function handleAPICall() {
  try {
    const response = await api.get('/appointments/');
    setAppointments(response.data.results);
  } catch (error) {
    if (error.response?.status === 401) {
      // Token invalid, redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      setError('You dont have permission to access this');
    } else if (error.response?.status === 404) {
      setError('Resource not found');
    } else {
      setError('Something went wrong');
    }
  }
}
```

---

## Summary: Backend Responsibility

As the backend engineer, YOU'RE responsible for:

1. **Data Integrity**
   - Database schema design
   - Validation (email format, age > 0, etc.)
   - Foreign key relationships
   - Unique constraints

2. **Security**
   - Password hashing
   - Token authentication
   - Permission classes
   - CORS configuration
   - Input validation (SQL injection prevention)

3. **Business Logic**
   - Can patient book with available doctor?
   - Can doctor edit appointment that's already completed?
   - Are credentials in database correct?
   - Handle edge cases

4. **API Contract**
   - Clear endpoint definitions
   - Consistent response formats
   - Proper HTTP status codes
   - Good error messages

5. **Data Persistence**
   - Database migrations
   - Backups
   - Schema versioning via git

6. **Performance**
   - Indexing for fast queries
   - Pagination for large datasets
   - Query optimization

---

## Quick Reference: File Structure

```
backend/
├── curova_backend/              # Settings & core
│   ├── settings.py              # Database, apps, middleware config
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py                  # Production server entry point
│   └── pagination.py            # Shared pagination utility
│
├── users/                        # Auth & profiles
│   ├── models.py                # User, Patient, Doctor
│   ├── views.py                 # Login, register, profile endpoints
│   ├── serializers.py           # User JSON conversion
│   ├── permissions.py           # IsPatient, IsDoctor classes
│   ├── urls.py                  # Auth routes
│   ├── admin_views.py           # Admin-only endpoints
│   └── admin_urls.py            # Admin routes
│
├── appointments/                # Booking system
│   ├── models.py                # Appointment model
│   ├── views.py                 # List, create, detail endpoints
│   ├── serializers.py           # Validation & JSON conversion
│   └── urls.py                  # Appointment routes
│
├── medical/                      # Medical records
│   ├── models.py                # MedicalRecord, Prescription
│   ├── views.py                 # Create, retrieve endpoints
│   ├── serializers.py           # Serialization
│   └── urls.py                  # Medical routes
│
├── medications/                  # Medication tracking
│   ├── models.py                # Medication, MedicationReminder
│   ├── views.py                 # List, update endpoints
│   └── urls.py                  # Med routes
│
├── lab_tests/                    # Lab testing
│   ├── models.py                # LabTest, LabTestResult
│   ├── views.py                 # Order, results endpoints
│   └── urls.py                  # Lab routes
│
├── documents/                    # File uploads
│   ├── models.py                # MedicalDocument
│   ├── views.py                 # Upload, delete endpoints
│   └── urls.py                  # Document routes
│
├── notifications/               # In-app alerts
│   ├── models.py                # Notification model
│   ├── views.py                 # List, mark read endpoints
│   ├── helpers.py               # Utility functions
│   └── urls.py                  # Notification routes
│
├── requirements.txt             # Dependencies (Django, DRF, etc.)
├── manage.py                    # Django CLI tool
└── migrations/                  # Database version history
    └── All app migrations
```

---

This guide should provide you with complete understanding to:
- Explain any API endpoint and why it exists
- Trace data flow through database
- Understand authentication mechanism
- Modify endpoints if asked
- Debug common issues
- Design new features within existing architecture

Good luck with your presentation!
