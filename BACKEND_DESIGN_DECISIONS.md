# CUROVA Backend — Design Decisions & Rationale

**Purpose:** Understand and explain the "why" behind architectural choices. For viva presentation.

---

## Table of Contents

1. [Why Django + Django REST Framework?](#why-django--django-rest-framework)
2. [Why Token-Based Authentication?](#why-token-based-authentication)
3. [Why Role-Based Access Control?](#why-role-based-access-control)
4. [Why PostgreSQL?](#why-postgresql)
5. [Why Separate User, Patient, Doctor Models?](#why-separate-user-patient-doctor-models)
6. [Why Immutable Prescriptions?](#why-immutable-prescriptions)
7. [Why Notifications App?](#why-notifications-app)
8. [Why Pagination?](#why-pagination)
9. [Why Unique Constraint on Appointments?](#why-unique-constraint-on-appointments)
10. [Why Serializers?](#why-serializers)
11. [Why Separate Frontend & Backend?](#why-separate-frontend--backend)
12. [Comparison: Our Choices vs. Alternatives](#comparison-our-choices-vs-alternatives)

---

## Why Django + Django REST Framework?

### The Choice
Backend: **Django web framework** + **Django REST Framework (DRF)**  
Alternatives considered: Flask, FastAPI, Node.js Express, Spring Boot

### Why We Chose It

#### 1. **Built-in ORM (Object-Relational Mapping)**
```python
# Django ORM - write Python, not SQL
user = User.objects.get(email="john@curova.com")
appointments = Appointment.objects.filter(doctor=user.doctor_profile, status='scheduled')

# Behind scenes, Django generates and executes SQL
# No SQL injection possible - parameterized queries
```

**Alternative (Flask):**
```python
# With Flask, you'd write raw SQL or use SQLAlchemy
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

Django's ORM is:
- Safer (automatic parameterization)
- Faster to develop (less boilerplate)
- Database-agnostic (switch from PostgreSQL to MySQL without code changes)

#### 2. **Admin Panel (Automatic CRUD UI)**
```
Default: http://localhost:8000/admin/
- Auto-generated interface to view/edit all data
- User management, authentication, permissions
- No additional code needed
```

**Value during development:**
- Testing data without writing scripts
- Debugging production data
- Client demos without custom UI

#### 3. **Built-in Security Features**
- CSRF protection (token validation on form submissions)
- SQL injection prevention (parameterized queries)
- Password hashing (PBKDF2 by default)
- XSS protection (template auto-escaping)

**Cost if building from scratch:** Weeks of security audits

#### 4. **Authentication & Permissions**
Django REST Framework provides:
- Token authentication (perfect for SPA + API)
- Permission classes (reusable, testable)
- Throttling (rate limiting)
- CORS handling via packages

**Alternative (Roll your own):**
- Generate tokens from scratch
- Implement permission logic in every view
- Handle rate limiting manually
- Test thoroughly for vulnerabilities

#### 5. **Migrations (Schema Versioning)**
```bash
python manage.py makemigrations  # Detect changes
python manage.py migrate          # Apply to database
# Result: Database schema tracked in git like code
```

**Why this matters:**
- Deploy without downtime
- Rollback database changes if needed
- New developer can sync entire schema from git
- Production database stays synchronized with code

---

## Why Token-Based Authentication?

### The Choice
**Token-based authentication** (DRF TokenAuthentication)

### The Flow
```
1. User submits email + password
   ↓
2. Server validates, generates Token(key="abc123...", user_id=5)
3. Token stored in database
   ↓
4. Client stores token in localStorage
   ↓
5. Client sends Authorization: Token abc123... with every request
   ↓
6. Server looks up token in database, identifies user
```

### Why This Over Sessions?

#### **Sessions (Traditional web apps)**
```python
# Traditional flow (for server-rendered HTML)
1. Login → Server creates session object, stores in server memory
2. Server returns session_id cookie to client
3. Client automatically sends cookie with every request
4. Server looks up session object from memory

# Problem for our architecture:
- Sessions stored in server memory (Redis/Memcached needed for scale)
- Frontend and backend must be on same domain (cookies cross-domain limited)
- Multiple backend servers need shared session storage
```

#### **Tokens (Perfect for decoupled SPA + API)**
```python
# Our setup:
- Frontend: https://curovafrontend.vercel.app
- Backend: https://curova-backend.onrender.com
# Different domains → Cookies won't work without complex setup

# Tokens solve this:
- Token is just a string, no cookies needed
- Sent via HTTP header (not subject to cookie restrictions)
- No server memory required (lookup is database query)
- Scales horizontally (multiple backend servers share same database)
```

### Practical Example

**Session-based problem:**
```
User logs in on server A
  → Session created in server A's memory
  
User's next request goes to server B (load balancer)
  → Session doesn't exist on server B
  → Treated as not logged in
  → Have to use sticky sessions (bad for scaling)
```

**Token-based solution:**
```
User logs in on server A
  → Token "abc123..." stored in shared database
  
User's next request goes to server B
  → Looks up token in shared database
  → Found → User validated
  → Any server can handle any user
```

### Security Considerations

```python
# Token transmitted in Authorization header (standard HTTPS encryption)
Authorization: Token abc123...

# NOT in URL (where it could be logged)
GET /api/appointments/?token=abc123  # BAD

# Our approach:
GET /api/appointments/  # URL clean
# Authorization: Token abc123... (in header, encrypted)
```

---

## Why Role-Based Access Control?

### The Choice
**Role-based permissions system** with 4 roles:
- `patient` - Can book appointments, view own records
- `doctor` - Can manage schedule, view patients, create records
- `admin` - Can view all users, system statistics
- `lab_tech` - Can upload lab test results

### The Alternative
**Attribute-based access control (ABAC)**
```python
# Too complex for our needs:
if user.organization == patient.organization \
   and user.department == "cardiology" \
   and current_time.hour < 18:
    allow_access()
```

### Why Role-Based is Right

#### 1. **Healthcare Requirements**
- Patients see only their own data
- Doctors see only their patients
- Lab techs can upload results but not prescribe
- Admins see everything

These fit naturally into 4 roles. No complex attributes needed.

#### 2. **Simple Implementation**
```python
# Role-based (us):
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_endpoint(request):
    pass

# ABAC (alternative):
@permission_classes([HasAttribute1, HasAttribute2, HasAttribute3])
def complex_endpoint(request):
    pass
```

#### 3. **Scales Better**
With 4 roles and 8 endpoints, we need ~32 permission checks.

With ABAC and 10 attributes per user, permission logic becomes combinatorial explosion.

### How Enforced in Our System

```python
# 1. View-level: Whole endpoint restricted
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_only_view(request):
    # Can't enter without being doctor

# 2. Object-level: Can see object but only if have relationship
@api_view(['GET'])
def view_appointment(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    
    # Check if user is in this appointment
    is_patient_in_appt = (
        hasattr(request.user, 'patient_profile') and 
        appointment.patient == request.user.patient_profile
    )
    is_doctor_in_appt = (
        hasattr(request.user, 'doctor_profile') and 
        appointment.doctor == request.user.doctor_profile
    )
    
    if not (is_patient_in_appt or is_doctor_in_appt):
        return 403 Forbidden
```

---

## Why PostgreSQL?

### The Choice
**PostgreSQL** (managed service on Render)

### Alternatives Evaluated
- SQLite (lightweight, file-based)
- MySQL (popular, similar to PostgreSQL)
- MongoDB (NoSQL, document-based)
- Firebase (fully managed, no infrastructure)

### Why PostgreSQL

#### 1. **ACID Compliance (Data Integrity)**
```
ACID = Atomicity, Consistency, Isolation, Durability

Example scenario: Patient books appointment
1. Check slot availability
2. Create appointment record
3. Create notification record

What if step 2 fails after step 1?
- Consistency violated (notification references non-existent appointment)

PostgreSQL guarantees:
- Either all 3 steps succeed or all 3 fail
- No partial state possible
```

**Critical for healthcare:**
- A prescription can't exist without a medical record
- An appointment can't be double-booked
- Patient can't see other patient's data due to foreign key constraint

#### 2. **Advanced Data Types**
```python
# Our models use JSON fields
class Patient(models.Model):
    allergies = JSONField(default=list)  # ["Penicillin", "Shellfish"]
    chronic_conditions = JSONField(default=list)  # ["Diabetes", "Hypertension"]
    medical_history = JSONField(default=dict)  # {"surgeries": [], ...}
```

PostgreSQL natively supports JSON with:
- Indexing for fast queries
- Validation
- Querying into structure

**SQLite alternative:**
- Can't index JSON fields
- Must retrieve entire field to query subsets
- Much slower for complex data

#### 3. **Scalability**
```
SQLite:
- File-based
- Database locked during writes
- Single server only
- Max ~10 concurrent users

PostgreSQL:
- Client-server architecture
- Many concurrent users
- Replication for backup
- Millions of records without slowdown
```

#### 4. **Production-Ready**
PostgreSQL has:
- Point-in-time recovery (restore to any moment)
- Streaming replication
- Hot standby
- Monitoring tools

**Critical for HIPAA compliance** (healthcare data protection regulation):
- Audit logs
- Encryption at rest/in transit
- User authentication
- Backup strategies

---

## Why Separate User, Patient, Doctor Models?

### The Design
```python
# Base authentication model
class User(AbstractUser):
    user_type = CharField(choices=['patient', 'doctor', 'admin', 'lab_tech'])

# Profiles extend User  
class Patient(models.Model):
    user = OneToOneField(User)
    DOB = DateField()
    blood_type = CharField()
    
class Doctor(models.Model):
    user = OneToOneField(User)
    license_number = CharField()
    specialization = CharField()
```

### The Alternative (Single Model)
```python
# Everything in one table
class User(AbstractUser):
    user_type = CharField()
    DOB = DateField(blank=True, null=True)  # Only for patients
    license_number = CharField(blank=True, null=True)  # Only for doctors
    specialization = CharField(blank=True, null=True)  # Only for doctors
    blood_type = CharField(blank=True, null=True)  # Only for patients
```

### Why Separate Models Win

#### 1. **Schema Clarity**
```python
# With separation:
patient = Patient.objects.get(user__email="patient@curova.com")
patient.DOB  # Definitely exists, never null

# Without separation:
user = User.objects.get(email="doctor@curova.com")
user.DOB  # Could be null - what does this mean? Was it never set? Is user a doctor?
```

#### 2. **Database Normalization**
Violating normalization rules creates anomalies:

```
Insertion anomaly:
Can't create doctor record without setting patient fields (DOB, blood_type)

Deletion anomaly:
Remove "cardiology" from specializations list
→ Accidentally deletes all cardiologists' user records? (Bad design!)

Update anomaly:
Update working_hours for one doctor
→ Accidentally changed for others? (Schema design bug)
```

#### 3. **Query Performance**
```python
# With separate models
doctor = Doctor.objects.get(id=5)
# Selects from doctor table only (small, indexed)

# Without separation (single User table has 50 fields)
doctor = User.objects.get(id=5)
# Selects from huge User table with many null columns
# Index efficiency reduced
```

#### 4. **Validation at Database Level**
```python
# With separate models
class Patient(models.Model):
    user = OneToOneField(User)
    # Database enforces: one patient per user
    
# To add patient profile:
Patient.objects.create(user=user, DOB="1990-01-01")

# Without separation
# How do you know if user is a patient?
if user.DOB is not None:  # Fragile logic
    # Treat as patient
```

---

## Why Immutable Prescriptions?

### The Design
```python
class Prescription(models.Model):
    medical_record = ForeignKey(MedicalRecord)
    medication_name = CharField()
    dosage = CharField()
    # ...
    created_at = DateTimeField(auto_now_add=True)
    # No update_at field - intentional!
```

**In views:** No PUT/PATCH endpoints for Prescription  
**In frontend:** No edit button for prescriptions

### Why Immutable?

#### 1. **Legal/Regulatory Compliance**
```
Medical board audit:
"Show me the prescription for acetaminophen on March 15"

If mutable:
- Could have been edited after issued
- "Proof" of what was prescribed is lost
- Liability for medication errors

If immutable:
- Exact record of when issued
- Matches pharmacy's records
- Provable history for legal cases
```

#### 2. **Audit Trail**
```
Scenario: Patient reports adverse reaction to medication

Mutable version:
Dr. Smith says: "I prescribed aspirin"
But database shows: "ibuprofen"
→ Contradiction, unclear liability

Immutable version:
Prescription shows: "aspirin 500mg, issued 2026-03-15 by Dr. Smith"
→ Clear historical record
```

#### 3. **Safety**
```
Without immutability:
Doctor creates prescription → Goes to pharmacy
→ Pharmacy misses communication, fills wrong drug
→ Doctor edits prescription in system
→ But pharmacy already filled original
→ Medication error, patient harmed
→ Doctor vs. pharmacy blame game

With immutability:
Doctor creates prescription → Pharmacy gets exact copy
→ If error happens, prescription record matches pharmacy
→ Easy to trace root cause
```

### How You Handle Corrections

**Scenario:** Doctor realizes they prescribed wrong dosage

**WRONG approach:**
```python
prescription.dosage = "500mg"  # Previously "1000mg"
prescription.save()  # Lost history!
```

**RIGHT approach:**
```python
# Keep original (immutable)
original_prescription = Prescription.objects.get(id=123)

# Create corrected version
corrected = Prescription.objects.create(
    medical_record=original_prescription.medical_record,
    medication_name=original_prescription.medication_name,
    dosage="500mg",  # Corrected
    notes="CORRECTION: Previous dosage was 1000mg, patient not allergic to lower dose"
)

# Link them so both appear in history
corrected.previous_version = original_prescription
corrected.save()
```

Result: Both prescriptions exist in database forever.

---

## Why Notifications App?

### The Design
Separate app dedicated to notifications:
```
Models: Notification
Views: list, mark_read, unread_count, delete
Triggers: Anywhere important happens (appointment booked, lab result ready, etc.)
```

### The Alternative (No Separate App)
```python
# Scattered logic across apps
class Appointment(models.Model):
    def save(self):
        super().save()
        # In appointment_created signal, send notifications
        if self.is_new:
            send_notification_to_doctor()
            send_notification_to_patient()

class LabTest(models.Model):
    def save(self):
        super().save()
        # Different notification logic
        send_notification_to_patient()
        send_notification_to_doctor()
```

### Why Dedicated App Wins

#### 1. **Consistency**
All notifications flow through one system:
- Same database table
- Same API endpoints
- Same "mark as read" logic
- Same filtering/searching

Without it:
- Notifications scattered in 5 different apps
- Update notification logic → Change in 5 places
- Patient sees different behaviors for different notification types

#### 2. **Reusability**
```python
# Generic helper function (in notifications/helpers.py)
def create_notification(recipient, title, message, notification_type, obj=None):
    """Used everywhere in the system"""
    return Notification.objects.create(...)

# Usage:
create_notification(doctor.user, "New appointment booking", ...)  # From appointments app
create_notification(patient.user, "Lab results ready", ...)      # From lab_tests app
create_notification(patient.user, "Prescription filled", ...)    # From medical app
```

#### 3. **Frontend Simplicity**
```javascript
// One notification feed shows everything
GET /api/notifications/
{
  results: [
    {type: "appointment", title: "New booking from Patient John"},
    {type: "lab_result", title: "Your blood test is ready"},
    {type: "prescription", title: "Dr. Smith prescribed Aspirin"}
  ]
}

// Without notification app, frontend would call 5 different endpoints
GET /api/appointments/my-pending/  // Could have notifications
GET /api/lab-tests/  // Could have results
GET /api/records/  // Could have new records
// etc...
```

#### 4. **Feature Extension**
```python
# Easy to add in future:
class NotificationPreferences(models.Model):
    user = OneToOneField(User)
    notify_appointments = BooleanField(default=True)
    notify_lab_results = BooleanField(default=True)
    email_notifications = BooleanField(default=False)
    quiet_hours_start = TimeField(default="18:00")
    quiet_hours_end = TimeField(default="08:00")

# With single app, easy to implement:
notifications = Notification.objects.filter(
    recipient=user,
    created_at__hour__gte=user.preferences.quiet_hours_start.hour
)
```

---

## Why Pagination?

### The Design
```python
GET /api/appointments/?page=1
{
  "count": 150,
  "next": ".../?page=2",
  "previous": null,
  "results": [{...}, {...}, ...]  # 20 items
}
```

### Why Not Return Everything?

#### 1. **Network Bandwidth**
```
Patient with 5 years of medical records (1000+ appointments)
Without pagination:
- Single response: ~5MB (if including full details)
- Download time: 10-20 seconds
- Uses cellular data quota

With pagination (20 per page):
- Single response: ~100KB
- Download time: 0.1-0.2 seconds
- User can navigate page by page
```

#### 2. **Database Performance**
```
Query all appointments:
- PostgreSQL loads 1000+ records into memory
- Serializes all to JSON
- Transfers over network
- Long response time while lock held

Query 20 at a time:
- PostgreSQL loads 20 records
- Quick response
- Database available for other users
```

#### 3. **Frontend Responsiveness**
```javascript
// Without pagination
const appointments = await fetch('/api/appointments');  // 10 seconds!
const data = await appointments.json();
// User stares at blank screen for 10 seconds

// With pagination
const firstPage = await fetch('/api/appointments/?page=1');  // 200ms
const data = await firstPage.json();
// UI shows first 20 appointments instantly
// Load more button available
```

### Why 20 Items Per Page?

**Balance:**
- 20 items = ~100KB response (fast download)
- 20 items = shows meaningful amount (don't need 500+ pages)
- 20 items = standard in most web apps (users expect it)

**Per-page customization:**
```python
GET /api/appointments/?page=1&page_size=50
# User can get 50 per page if preferred

# But backend limits it:
PAGE_SIZE_LIMIT = 100  # Can't request more than 100
```

---

## Why Unique Constraint on Appointments?

### The Design (Database Level)
```python
class Appointment(models.Model):
    class Meta:
        unique_together = ('doctor', 'appointment_date', 'appointment_time')
```

**Result:** PostgreSQL rejects any duplicate booking at database level

### Why Database-Level (Not Just Application Logic)?

#### 1. **Race Condition Prevention**
```
Imagine both are processing simultaneously:

Request 1: Check if 2:00 PM slot is free for Dr. Smith on March 30
Wait... database is busy
Request 2: Check if 2:00 PM slot is free for Dr. Smith on March 30
Slot is free. Create appointment.
Request 1: Slot is still free (checked before Request 2 created appt).
          Create appointment.
→ DUPLICATE BOOKING!

With database unique constraint:
Request 2 creates appointment, succeeds
Request 1 tries to create, database rejects
→ Error returned to user "Slot already taken"
```

This is called a "race condition" - multithreading is dangerous.

#### 2. **Multiple Backups**
Application logic validation:
```python
if Appointment.objects.filter(doctor=doctor, ...).exists():
    return error
```

Database constraint:
```sql
UNIQUE(doctor_id, appointment_date, appointment_time)
```

**Scenario:** Your code has a bug, allows invalid appointment  
- Application logic: Bug creates bad data, nobody notices for months
- Database constraint: Database rejects it, error logged immediately

#### 3. **Scalability**
```
If you deploy 10 backend servers:
All 10 can check availability simultaneously
But database UNIQUE constraint is single point of truth
Prevents all concurrency issues

Without constraint:
Would need distributed locking (very complex)
```

---

## Comparison: Our Choices vs. Alternatives

| Decision | Our Choice | Alternative | Why Ours |
|----------|-----------|-------------|---------|
| **Framework** | Django + DRF | Flask | Built-in ORM, migrations, admin, security |
| **Authentication** | Token-based | Session-based | works with SPA + API decoupling |
| **Access Control** | Role-based | Attribute-based | Simpler for 4 roles, scales better |
| **Database** | PostgreSQL | SQLite | ACID, JSON support, production-ready |
| **User Models** | Separate User/Patient/Doctor | Single User table | Schema clarity, normalization, queries |
| **Prescriptions** | Immutable | Mutable | Legal compliance, audit trail, safety |
| **Notifications** | Dedicated app | Scattered logic | Consistency, reusability, extensibility |
| **Pagination** | 20 items/page | All items | Performance, UX, bandwidth |
| **Double-booking Prevention** | DB unique constraint | App logic only | Race condition prevention, multi-deployment |

---

## How to Answer "Why" Questions in Viva

### Pattern for answering design questions:

1. **State the choice clearly**
   "We chose PostgreSQL as our database..."

2. **Explain the problem it solves**
   "Healthcare data must be reliable and never corrupt..."

3. **Contrast with alternative**
   "SQLite would be fine for small apps, but:"

4. **Give concrete example**
   "Imagine two patients booking same appointment slot simultaneously..."

5. **Connect to requirements**
   "This aligns with our requirement for data integrity and HIPAA compliance"

### Example Answer

**Q: "Why don't you let doctors edit prescriptions after creating them?"**

**A:** "We made prescriptions immutable by design. Here's why:

First, from a legal perspective, prescriptions are legal documents. If a doctor prescribes medication and the patient has a reaction, the pharmacy has their copy and the doctor system has ours. If the system record could be edited, we lose proof of what was actually prescribed.

Second, it prevents subtle bugs. Imagine doctor prescribes aspirin. Pharmacy fills it. Doctor later realizes they made a mistake and edits to ibuprofen in the system. But the patient already got aspirin from pharmacy - medication mismatch happens.

Third, it forces us to handle corrections properly. Instead of editing, we create a new corrected prescription and link the old one as history. This is actually safer and provides an audit trail.

So while it might seem restrictive, immutability actually makes the system safer and more compliant with healthcare regulations."

---

This document should give you answers for ANY design question they ask!
