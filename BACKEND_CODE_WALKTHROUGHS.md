# CUROVA Backend — Code Walkthroughs & Implementation Details

**Purpose:** Deep dive into actual code locations and how to modify/extend features

---

## Table of Contents

1. [Adding a New API Endpoint](#adding-a-new-api-endpoint)
2. [Creating Notifications When Events Happen](#creating-notifications-when-events-happen)
3. [Adding Permission Restrictions](#adding-permission-restrictions)
4. [Database Query Patterns](#database-query-patterns)
5. [Serializer Validation Examples](#serializer-validation-examples)
6. [Common Code Locations](#common-code-locations)
7. [How to Debug](#how-to-debug)
8. [Extending Models](#extending-models)

---

## Adding a New API Endpoint

### Scenario: Add endpoint for patient to request prescription refill

#### Step 1: Create the View

**File:** `/backend/medical/views.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Prescription
from users.permissions import IsPatient

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def request_prescription_refill(request):
    """
    POST /api/records/prescriptions/{id}/refill-request/
    
    Patient requests a refill of an existing prescription.
    Notifies the prescribing doctor.
    """
    try:
        prescription_id = request.parser_context['kwargs']['pk']
        prescription = Prescription.objects.get(id=prescription_id)
    except Prescription.DoesNotExist:
        return Response(
            {'error': 'Prescription not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify patient owns this prescription
    patient = request.user.patient_profile
    if prescription.medical_record.patient != patient:
        return Response(
            {'error': 'Cannot request refill for someone elses prescription'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if already recently requested (prevent spam)
    from django.utils import timezone
    from datetime import timedelta
    
    recent_request = PrescriptionRefillRequest.objects.filter(
        prescription=prescription,
        created_at__gte=timezone.now() - timedelta(days=1)
    ).exists()
    
    if recent_request:
        return Response(
            {'error': 'Refill already requested in last 24 hours'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Create refill request
    refill_request = PrescriptionRefillRequest.objects.create(
        prescription=prescription,
        patient=patient,
        request_date=timezone.now()
    )
    
    # Notify doctor (prescriber)
    from notifications.helpers import create_notification
    doctor = prescription.medical_record.doctor
    create_notification(
        recipient=doctor.user,
        title=f'Prescription refill request from {patient.user.first_name}',
        message=f'{patient.user.first_name} requested refill of {prescription.medication_name}',
        notification_type='prescription',
        obj=prescription
    )
    
    return Response(
        {
            'id': refill_request.id,
            'prescription': prescription.id,
            'medication': prescription.medication_name,
            'status': 'pending',
            'created_at': refill_request.request_date
        },
        status=status.HTTP_201_CREATED
    )
```

#### Step 2: Add URL Route

**File:** `/backend/medical/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('records/', views.medical_record_list, name='record-list'),
    path('records/<int:pk>/', views.medical_record_detail, name='record-detail'),
    
    # Add this line:
    path('records/prescriptions/<int:pk>/refill-request/', 
         views.request_prescription_refill, name='prescription-refill-request'),
]
```

#### Step 3: Create Supporting Model (if needed)

**File:** `/backend/medical/models.py`

```python
class PrescriptionRefillRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    ]
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    doctor_response_date = models.DateTimeField(null=True, blank=True)
    doctor_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Refill request: {self.prescription.medication_name} by {self.patient.user.email}"
```

#### Step 4: Create Migration

```bash
# Run locally or note for production
python manage.py makemigrations medical

# Output might be:
# Migrations for 'medical':
#   medical/migrations/0018_prescriptionrefillrequest.py
#     - Create model PrescriptionRefillRequest
```

**Then run:** `python manage.py migrate`

#### Step 5: Test the Endpoint

```bash
# Using curl
curl -X POST http://localhost:8000/api/records/prescriptions/5/refill-request/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json"

# Response:
# {
#   "id": 1,
#   "prescription": 5,
#   "medication": "Aspirin 500mg",
#   "status": "pending",
#   "created_at": "2026-03-28T15:30:00Z"
# }
```

---

## Creating Notifications When Events Happen

### Pattern: Notification Helper Usage

**File:** `/backend/notifications/helpers.py`

```python
from .models import Notification

def create_notification(recipient, title, message, notification_type="system", obj=None):
    """
    Generic helper to create notifications.
    
    Args:
        recipient: User object who receives notification
        title: Short title (appears in list)
        message: Longer description (appears in dropdown/detail)
        notification_type: One of ['appointment', 'medication', 'lab_result', 'prescription', 'system']
        obj: Related model instance (Appointment, LabTest, etc.) - optional
    
    Returns:
        Created Notification instance
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_type=obj.__class__.__name__ if obj else None,
        related_object_id=obj.id if obj else None
    )
```

### Example 1: Notify When Appointment Booked

**File:** `/backend/appointments/views.py`

```python
from notifications.helpers import create_notification

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def create_appointment(request):
    # ... validation code ...
    
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        appointment_date=date,
        appointment_time=time,
        status='scheduled'
    )
    
    # Notify doctor
    create_notification(
        recipient=appointment.doctor.user,
        title=f'New appointment booking from {patient.user.first_name} {patient.user.last_name}',
        message=f'Patient: {patient.user.email}\nDate: {appointment.appointment_date}\nTime: {appointment.appointment_time}',
        notification_type='appointment',
        obj=appointment
    )
    
    # Also notify patient
    create_notification(
        recipient=patient.user,
        title='Appointment confirmation',
        message=f'Your appointment with {appointment.doctor.user.first_name} on {appointment.appointment_date} has been booked.',
        notification_type='appointment',
        obj=appointment
    )
    
    return Response(...)
```

### Example 2: Notify When Lab Results Ready

**File:** `/backend/lab_tests/views.py`

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsLabTech])
def upload_lab_results(request, pk):
    lab_test = LabTest.objects.get(id=pk)
    
    # ... validation ...
    
    # Create result
    result = LabTestResult.objects.create(
        lab_test=lab_test,
        results=request.data.get('results'),
        findings=request.data.get('findings'),
        impression=request.data.get('impression')
    )
    
    # Update lab test status
    lab_test.status = 'completed'
    lab_test.save()
    
    # Notify patient
    create_notification(
        recipient=lab_test.patient.user,
        title='Lab test results available',
        message=f'Your {lab_test.test_type} results are ready. Click to view.',
        notification_type='lab_result',
        obj=lab_test
    )
    
    # Also notify prescribing doctor
    create_notification(
        recipient=lab_test.doctor.user,
        title=f'{lab_test.patient.user.first_name}\'s lab results ready',
        message=f'Results for {lab_test.test_type} are available.',
        notification_type='lab_result',
        obj=lab_test
    )
    
    return Response(...)
```

### Example 3: Batch Notifications (Multiple Recipients)

**File:** `/backend/notifications/helpers.py` (extended)

```python
def create_notifications_batch(recipients_list, title, message, notification_type="system", obj=None):
    """Create same notification for multiple recipients efficiently."""
    notifications = [
        Notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_object_type=obj.__class__.__name__ if obj else None,
            related_object_id=obj.id if obj else None
        )
        for recipient in recipients_list
    ]
    Notification.objects.bulk_create(notifications)
    return len(notifications)
```

---

## Adding Permission Restrictions

### Scenario: Only allow doctor to see patients they've treated

#### Current Permission Class

**File:** `/backend/users/permissions.py`

```python
class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == "doctor"
        )
```

#### New Object-Level Permission

```python
class IsPatientOwnDoctor(BasePermission):
    """
    Check if requesting doctor has treated this patient
    (appeared in a completed appointment or created a record)
    """
    def has_object_permission(self, request, view, obj):
        # obj is the Patient instance
        if not request.user.user_type == "doctor":
            return False
        
        doctor = request.user.doctor_profile
        
        # Check if doctor has treated this patient
        has_appointment = Appointment.objects.filter(
            doctor=doctor,
            patient=obj,
            status__in=['completed', 'in_progress']
        ).exists()
        
        has_record = MedicalRecord.objects.filter(
            doctor=doctor,
            patient=obj
        ).exists()
        
        return has_appointment or has_record
```

#### Usage in View

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
def view_patient_detail(request, patient_id):
    """GET /api/auth/doctor/patients/{id}/"""
    
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404)
    
    # Check object-level permission
    if not IsPatientOwnDoctor().has_object_permission(request, None, patient):
        return Response(
            {'error': 'You can only view patients youve treated'},
            status=403
        )
    
    serializer = PatientDetailSerializer(patient)
    return Response(serializer.data)
```

### Multiple Permission Classes (AND logic)

```python
# Endpoint only accessible to authenticated lab techs
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsLabTech, HasActiveContract])
def upload_lab_results(request):
    # User must pass ALL three checks
    pass
```

### Custom Permission with Arguments

```python
class CanModifyAppointment(BasePermission):
    """
    Allow modification only if:
    - User created it (patient), OR
    - User is the doctor in it
    AND appointment is not already completed
    """
    def has_object_permission(self, request, view, obj):
        # obj is Appointment instance
        is_patient = hasattr(request.user, 'patient_profile')
        is_doctor = hasattr(request.user, 'doctor_profile')
        
        if is_patient:
            patient_in_appt = obj.patient == request.user.patient_profile
            not_completed = obj.status != 'completed'
            return patient_in_appt and not_completed
        
        elif is_doctor:
            doctor_in_appt = obj.doctor == request.user.doctor_profile
            not_completed = obj.status != 'completed'
            return doctor_in_appt and not_completed
        
        return False
```

---

## Database Query Patterns

### Pattern 1: Get User's Appointments (Smart Query)

```python
# File: backend/appointments/views.py

def get_user_appointments(user, status_filter=None):
    """Efficiently get appointments based on user role."""
    
    if user.user_type == 'patient':
        query = Appointment.objects.filter(
            patient=user.patient_profile
        ).select_related('doctor', 'doctor__user', 'patient', 'patient__user')
        # select_related() does LEFT JOIN to avoid N+1 queries
        # (instead of 1 query + N queries for each appointment's doctor)
    
    elif user.user_type == 'doctor':
        query = Appointment.objects.filter(
            doctor=user.doctor_profile
        ).select_related('patient', 'patient__user', 'doctor', 'doctor__user')
    
    else:
        query = Appointment.objects.none()  # Admin sees nothing by default
    
    if status_filter:
        query = query.filter(status=status_filter)
    
    return query.order_by('-appointment_date', '-appointment_time')
```

### Pattern 2: Count Unread Notifications

```python
# File: backend/notifications/views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """GET /api/notifications/unread-count/"""
    
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})

# Or with breakdown by type:
def unread_by_type(request):
    """Count unread notifications by type."""
    
    counts = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).values('notification_type').annotate(
        count=Count('id')
    )
    
    # Result:
    # [
    #   {'notification_type': 'appointment', 'count': 3},
    #   {'notification_type': 'lab_result', 'count': 1}
    # ]
    
    return Response(counts)
```

### Pattern 3: Complex Filter (Appointments in Next 7 Days)

```python
from django.utils import timezone
from datetime import timedelta

upcoming = Appointment.objects.filter(
    appointment_date__gte=timezone.now().date(),
    appointment_date__lte=timezone.now().date() + timedelta(days=7),
    status__in=['scheduled', 'confirmed'],
    doctor=doctor
).order_by('appointment_date', 'appointment_time')

# Equivalent SQL:
# SELECT * FROM appointments 
# WHERE appointment_date >= TODAY()
#   AND appointment_date <= TODAY() + 7
#   AND status IN ('scheduled', 'confirmed')
#   AND doctor_id = 5
# ORDER BY appointment_date ASC, appointment_time ASC
```

### Pattern 4: Aggregate Data (Dashboard Stats)

```python
# File: backend/users/views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_dashboard(request):
    """GET /api/auth/doctor/dashboard-stats/"""
    
    doctor = request.user.doctor_profile
    
    # Count appointments by status
    stats = {
        'total_appointments': Appointment.objects.filter(doctor=doctor).count(),
        'completed_appointments': Appointment.objects.filter(
            doctor=doctor, 
            status='completed'
        ).count(),
        'upcoming_appointments': Appointment.objects.filter(
            doctor=doctor,
            status__in=['scheduled', 'confirmed'],
            appointment_date__gte=timezone.now().date()
        ).count(),
        'total_patients_treated': Patient.objects.filter(
            appointment__doctor=doctor
        ).distinct().count(),  # DISTINCT to avoid duplicates
        'pending_lab_results': LabTest.objects.filter(
            doctor=doctor,
            status='ordered'
        ).count(),
    }
    
    return Response(stats)
```

### Pattern 5: Update Multiple Records

```python
# Update all past scheduled appointments to no_show
from django.utils import timezone

Appointment.objects.filter(
    appointment_date__lt=timezone.now().date(),
    status='scheduled'
).update(status='no_show')

# Returns: number of records updated
# (5 appointments changed from scheduled to no_show)
```

---

## Serializer Validation Examples

### Basic Field Validation

**File:** `/backend/appointments/serializers.py`

```python
class CreateAppointmentSerializer(serializers.Serializer):
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )
    appointment_date = serializers.DateField()
    appointment_time = serializers.TimeField()
    reason = serializers.CharField(max_length=500)
    
    def validate_appointment_date(self, value):
        """Validate appointment_date field specifically."""
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Cannot book appointments in the past"
            )
        if (value - timezone.now().date()).days > 365:
            raise serializers.ValidationError(
                "Cannot book more than 1 year in advance"
            )
        return value
    
    def validate_reason(self, value):
        """Validate reason field."""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Reason must be at least 5 characters"
            )
        return value
```

### Cross-Field Validation (validate method)

```python
class CreateAppointmentSerializer(serializers.Serializer):
    # ... fields ...
    
    def validate(self, data):
        """Validate across multiple fields."""
        doctor = data['doctor']
        date = data['appointment_date']
        time = data['appointment_time']
        
        # Check 1: Doctor available on that day
        day_name = date.strftime('%A').lower()
        if day_name not in doctor.available_days:
            raise serializers.ValidationError({
                'appointment_date': f"Doctor not available on {day_name}s"
            })
        
        # Check 2: Time within working hours
        if not (doctor.working_hours_start <= time <= doctor.working_hours_end):
            raise serializers.ValidationError({
                'appointment_time': "Time outside doctor's working hours"
            })
        
        # Check 3: Time on slot boundary
        start_seconds = (
            doctor.working_hours_start.hour * 3600 + 
            doctor.working_hours_start.minute * 60
        )
        time_seconds = time.hour * 3600 + time.minute * 60
        offset = (time_seconds - start_seconds) % (doctor.slot_duration * 60)
        
        if offset != 0:
            raise serializers.ValidationError({
                'appointment_time': f"Time must be on {doctor.slot_duration}-minute boundaries"
            })
        
        # Check 4: Slot not booked
        is_taken = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            status__in=['scheduled', 'confirmed', 'in_progress']
        ).exists()
        
        if is_taken:
            raise serializers.ValidationError({
                'appointment_time': "This slot is already booked"
            })
        
        return data
```

### Custom Validator Function

```python
def validate_no_consecutive_same_specialty(value):
    """
    Custom validator: Doctor can't have multiple appointments
    with same patient on same day
    """
    # value is the field being validated
    # Can be applied to multiple fields
    pass

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'appointment_date']
        validators = [validate_no_consecutive_same_specialty]
```

### Nested Serializers (Related Objects)

```python
class DoctorDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer for related User
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'years_experience', 'fee']

# Result:
# {
#   "id": 5,
#   "user": {
#     "id": 12,
#     "email": "dr.smith@curova.com",
#     "first_name": "John",
#     "last_name": "Smith"
#   },
#   "specialization": "Cardiology",
#   "years_experience": 15,
#   "fee": "50.00"
# }
```

---

## Common Code Locations

### Authentication Logic
- **Login endpoint:** `/backend/users/views.py` → `login_view()`
- **Token generation:** DRF handles automatically in `LoginSerializer.validate()`
- **Permission classes:** `/backend/users/permissions.py`

### Appointment Logic
- **Models:** `/backend/appointments/models.py`
- **Booking logic:** `/backend/appointments/serializers.py` → `CreateAppointmentSerializer.validate()`
- **Endpoints:** `/backend/appointments/views.py`
- **URL routes:** `/backend/appointments/urls.py`

### Medical Records
- **Models:** `/backend/medical/models.py` (MedicalRecord, Prescription)
- **Creation:** `/backend/medical/views.py` → `create_medical_record()`
- **Immutability:** Enforced in views (no PUT/PATCH on Prescription)

### Notifications
- **Model:** `/backend/notifications/models.py` → `Notification` model
- **Creation helper:** `/backend/notifications/helpers.py` → `create_notification()`
- **Endpoints:** `/backend/notifications/views.py`
- **Triggers:** Any view that calls `create_notification()`

### Settings & Configuration
- **Database:** `/backend/curova_backend/settings.py` → `DATABASES` dict
- **REST Framework config:** `/backend/curova_backend/settings.py` → `REST_FRAMEWORK` dict
- **CORS settings:** `/backend/curova_backend/settings.py` → `CORS_ALLOWED_ORIGINS`
- **Middleware:** `/backend/curova_backend/settings.py` → `MIDDLEWARE` list

### Global URL Routing
- **Root URLs:** `/backend/curova_backend/urls.py` (imports from each app's urls.py)
- **Admin panel:** `/backend/curova_backend/urls.py` → includes `admin.site.urls`

---

## How to Debug

### Scenario 1: Endpoint Returns 500 Error

```
1. Check Render logs (or console if running locally)
   Command: tail -f /var/log/curova-backend.log
   
2. Look for Python traceback:
   Traceback (most recent call last):
     File "django/core/handlers/wsgi.py", line 111, in __call__
     ...
     KeyError: 'appointment_date'
   
3. This tells you the problem: 'appointment_date' key missing from request
   
4. Solution:
   - Frontend not sending that field?
   - Check POST request JSON body
   - Verify field name matches backend expectation
```

### Scenario 2: Permission Denied (403)

```
1. Endpoint returns: {"detail": "Permission denied."}
   
2. Check permission classes in view:
   @permission_classes([IsAuthenticated, IsDoctor])
   
3. Ask yourself:
   - Is user authenticated? (check Authorization header)
   - Is user_type == "doctor"? (check in database)
   - Are there object-level permissions? (check has_object_permission)
   
4. Debug:
   Use Django shell:
   python manage.py shell
   >>> from users.models import User
   >>> user = User.objects.get(email="test@curova.com")
   >>> user.user_type
   'patient'  # ← Not doctor! That's the issue
```

### Scenario 3: Database Returns Empty Results

```
Endpoint returns [] but should return data

1. Check query in view:
   appointments = Appointment.objects.filter(
       doctor=request.user.doctor_profile
   )
   
2. Debug:
   python manage.py shell
   >>> from appointments.models import Appointment
   >>> from users.models import User, Doctor
   >>> user = User.objects.get(email="dr@curova.com")
   >>> doctor = user.doctor_profile
   >>> Appointment.objects.filter(doctor=doctor)
   <QuerySet []>  # No results
   
3. Verify data exists:
   >>> Appointment.objects.all()  # Any appointments at all?
   <QuerySet [<Appointment: ...>]>
   
4. Check filter conditions:
   >>> Appointment.objects.filter(doctor=doctor).count()
   0
   >>> Appointment.objects.all().count()
   5
   >>> # Maybe filter is wrong? Check doctor ID
   >>> Appointment.objects.filter(doctor_id=999)  # Doesn't exist?
```

### Scenario 4: CORS Error (Frontend Can't Reach Backend)

```
Browser console:
"Access to XMLHttpRequest ... blocked by CORS policy"

1. Check backend CORS configuration:
   /backend/curova_backend/settings.py
   CORS_ALLOWED_ORIGINS = [...]
   
2. Verify frontend URL is in list:
   If frontend is at: https://curovafrontend.vercel.app
   Then CORS_ALLOWED_ORIGINS must include it
   
3. Test with curl:
   curl -X OPTIONS http://curova-backend.onrender.com/api/appointments/ \
     -H "Origin: https://curovafrontend.vercel.app"
   
   Should return:
   Access-Control-Allow-Origin: https://curovafrontend.vercel.app
   
4. If not:
   - Add frontend URL to CORS_ALLOWED_ORIGINS
   - Redeploy backend
```

---

## Extending Models

### Adding a New Field to Existing Model

**Example: Add "notes" field to Appointment**

1. **Edit model:**
   File: `/backend/appointments/models.py`
   ```python
   class Appointment(models.Model):
       # ... existing fields ...
       doctor_notes = models.TextField(blank=True, default="")
   ```

2. **Create migration:**
   ```bash
   python manage.py makemigrations appointments
   # Output: Migrations for 'appointments':
   #   appointments/migrations/0008_appointment_doctor_notes.py
   ```

3. **Apply migration:**
   ```bash
   python manage.py migrate
   # Output: Running migrations:
   #   Applying appointments.0008_appointment_doctor_notes... OK
   ```

4. **Update serializer:**
   File: `/backend/appointments/serializers.py`
   ```python
   class AppointmentSerializer(serializers.ModelSerializer):
       class Meta:
           model = Appointment
           fields = [..., 'doctor_notes']  # Add field
   ```

5. **Update view (if needed):**
   Allow doctor to set notes:
   ```python
   @api_view(['PATCH'])
   @permission_classes([IsAuthenticated, IsDoctor])
   def update_appointment_notes(request, pk):
       appointment = Appointment.objects.get(id=pk)
       appointment.doctor_notes = request.data.get('doctor_notes', '')
       appointment.save()
       return Response(AppointmentSerializer(appointment).data)
   ```

6. **Test:**
   ```bash
   python manage.py shell
   >>> from appointments.models import Appointment
   >>> appt = Appointment.objects.first()
   >>> appt.doctor_notes  # Should work now
   ""
   >>> appt.doctor_notes = "Patient seemed anxious"
   >>> appt.save()
   ```

### Creating a Relationship Between Models

**Example: Allow doctors to flag certain patients as "high priority"**

1. **Create new model:**
   File: `/backend/appointments/models.py` (or new file `medical/models.py`)
   ```python
   class PatientFlag(models.Model):
       FLAG_TYPES = [
           ('high_priority', 'High Priority'),
           ('allergy_alert', 'Allergy Alert'),
           ('follow_up', 'Requires Follow-up'),
           ('research', 'Research Subject'),
       ]
       
       doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
       patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
       flag_type = models.CharField(max_length=20, choices=FLAG_TYPES)
       notes = models.TextField(blank=True)
       created_at = models.DateTimeField(auto_now_add=True)
       
       class Meta:
           unique_together = ('doctor', 'patient', 'flag_type')
   ```

2. **Create migration:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create view:**
   ```python
   @api_view(['POST'])
   @permission_classes([IsAuthenticated, IsDoctor])
   def flag_patient(request, patient_id):
       """POST /api/patients/{id}/flag/"""
       patient = Patient.objects.get(id=patient_id)
       doctor = request.user.doctor_profile
       
       flag, created = PatientFlag.objects.get_or_create(
           doctor=doctor,
           patient=patient,
           flag_type=request.data.get('flag_type'),
           defaults={'notes': request.data.get('notes', '')}
       )
       
       status_code = 201 if created else 200
       return Response({...}, status=status_code)
   ```

---

## Interview Prep: Common Questions You'll Get Asked

### Q1: "Walk me through the appointment booking flow"

**Answer:** (Refer to the Common Operations section in main guide, but emphasize):

1. Database validation prevents double-booking via unique constraint
2. Serializer validates doctor availability via available_days and working hours
3. Frontend uses booked-slots endpoint to prevent user from even trying invalid times
4. Notifications automatically created to both parties
5. Status field ensures only one appointment state at a time

### Q2: "How do you handle role-based access?"

**Answer:**
- User model has `user_type` choice field (patient/doctor/admin/lab_tech)
- Permission classes in `users/permissions.py` check user_type
- Applied with `@permission_classes` decorator
- Object-level permissions check if user owns the resource (e.g., patient can only see own appointments)

### Q3: "What happens if doctor changes their schedule and has conflicting appointments?"

**Answer:**
(Design decision from FINAL_DECISIONS.md)
- Backend checks for conflicting appointments
- Returns list to frontend instead of applying change
- Frontend shows modal to doctor with affected appointments
- If confirmed, backend auto-cancels and notifies patients
- Uses transactions to ensure all-or-nothing

### Q4: "How do you prevent SQL injection?"

**Answer:**
- Use ORM (not raw SQL) — Django converts Python to parameterized SQL
- Serializers validate input before querying
- `.get_or_404()` prevents timing attacks
- Never concatenate user input into queries

### Q5: "Show me how you'd add a new endpoint"

**Answer:**
- Create view function with `@api_view` and `@permission_classes`
- Create corresponding serializer for validation
- Add URL route in app's `urls.py`
- Create migration if touching database
- Write test case

This guide + main guide should cover 99% of questions you'll face. Good luck!
