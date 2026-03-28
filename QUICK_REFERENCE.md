# QUICK REFERENCE GUIDE
## File Locations & Code Snippets

---

## 🔴 CRITICAL ISSUE #1: Notification Navigation Missing

### Where to Find It

**Issue Location 1: Full Notifications Page**
```
File: /frontend/src/pages/common/Notifications.jsx
Lines: 195-278 (Notification rendering loop)
Problem: No click handler for navigation
```

**Issue Location 2: Notification Dropdown**  
```
File: /frontend/src/components/layout/DashboardLayout.jsx
Lines: 233-280 (Notification dropdown items)
Problem: Only handles markAsRead, no navigation
```

### The Broken Code

**Current Code (NOT WORKING):**
```javascript
// DashboardLayout.jsx, Lines 233-243
<button
  key={n.id}
  className={`notif-dropdown-item ${!n.is_read ? 'unread' : ''}`}
  onClick={() => !n.is_read && handleMarkOneRead(n.id)}  // ❌ ONLY marks as read
>
  <span className="notif-dropdown-item-dot" ... />
  <div className="notif-dropdown-item-content">
    <p className="notif-dropdown-item-title">{n.title}</p>
    <p className="notif-dropdown-item-msg">{n.message}</p>
```

**What Data Is Available But Unused:**
```javascript
n.related_object_type   // "lab_test", "appointment", etc.
n.related_object_id     // 123, 456, etc.
n.notification_type     // "lab_result", "appointment", etc.
```

### Proof Backend Is Working

**Backend creates notifications correctly:**
```python
# /backend/lab_tests/views.py, Lines 80-86
create_notification(
    recipient=lab_test.patient.user,
    title="Lab Test Ordered",
    message=f"Dr. {lab_test.doctor.user.get_full_name()} has ordered a...",
    notification_type="lab_result",          # ✅ Correct
    related_object_type="lab_test",          # ✅ Correct
    related_object_id=lab_test.id,           # ✅ Correct
)
```

**API returns correct data:**
```
GET /api/notifications/
Response JSON:
{
  "id": 1,
  "title": "Lab Test Ordered",
  "message": "...",
  "notification_type": "lab_result",
  "related_object_type": "lab_test",
  "related_object_id": 123,         # ✅ SENT TO FRONTEND
  "is_read": false,
  "time_ago": "2m ago"
}
```

---

## 🔴 CRITICAL ISSUE #2: Doctor Endpoint Requires Auth

### Where to Find It

```
File: /backend/users/views.py
Lines: 375-400
Function: doctor_list_view()
```

### The Bug

```python
# /backend/users/views.py, Lines 375-380
# ── Doctor List (public for booking) ──────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # ❌ SHOULD BE: [AllowAny]
def doctor_list_view(request):
    """List all active doctors, optionally filtered by specialization."""
    qs = Doctor.objects.filter(user__is_active=True).select_related("user")
    # ... rest of function ...
```

### The Fix (ONE LINE CHANGE)

**Change from:**
```python
@permission_classes([IsAuthenticated])
```

**Change to:**
```python
@permission_classes([AllowAny])
```

### Affected Code That Calls This

**Patient appointment booking:**
```javascript
// /frontend/src/pages/patient/Appointments.jsx, Line 367
const res = await api.get('/auth/doctors/', { params: controller.signal });
// ❌ Currently fails if not authenticated
// ✅ Will work for all users after fix
```

---

## 🔴 CRITICAL ISSUE #3: Homepage Hardcoded Dummy Data

### Where to Find It

```
File: /frontend/src/pages/public/Homepage.jsx
Lines: 6-12 (Dummy data declaration)
```

### The Fake Data

```javascript
// /frontend/src/pages/public/Homepage.jsx, Lines 7-12
const doctors = [
  { name: 'Dr. Nusrat Jahan', specialty: 'Orthotic Surgeon', location: 'Chattogram, Bangladesh', 
    img: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop' },
  { name: 'Dr. Tanvir Rahman', specialty: 'Neurologist', location: 'Dhaka, Bangladesh', 
    img: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop' },
  { name: 'Dr. Shakil Ahmed', specialty: 'Orthopedist and Joint', location: 'Sylhet, Bangladesh', 
    img: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&h=400&fit=crop' },
  // ... 3 more fake doctors ...
];
```

### The TODO Comment That Was Missed

```javascript
// /frontend/src/pages/public/Homepage.jsx, Line 6
// TODO: Replace with real API data when doctor public profiles are ready.
```

### Where Data Should Come From

The real doctors are in the database and can be fetched from:
```
API Endpoint: GET /api/auth/doctors/
Returns: Array of real Doctor objects with:
  - id, email, first_name, last_name
  - profile_picture (absolute URL from AbsoluteImageURLField)
  - specialization, years_experience, bio, consultation_fee
  - available_days, working_hours_start, working_hours_end
```

---

## 🟡 MEDIUM ISSUE #4: No Type-Based Route Handlers

### Where to Find It

**Problem Location 1:**
```javascript
// /frontend/src/pages/common/Notifications.jsx, Line 243-250
<p className="notif-page-item-message">{notif.message}</p>
// Items just display, no click handling for navigation
```

**Problem Location 2:**
```javascript
// /frontend/src/components/layout/DashboardLayout.jsx, Line 233-243
onClick={() => !n.is_read && handleMarkOneRead(n.id)}
// Only marks read, no routing logic
```

### What Should Happen

**Switch statement needed:**
```javascript
const handleNotificationClick = (notification) => {
  switch(notification.related_object_type) {
    case 'lab_test':
      navigate(`/patient/lab-tests/${notification.related_object_id}`);
      break;
    case 'appointment':
      navigate(`/patient/appointments/${notification.related_object_id}`);
      break;
    case 'medication_reminder':
      navigate(`/patient/medications/${notification.related_object_id}`);
      break;
    case 'medical_record':
      navigate(`/patient/medical-records/${notification.related_object_id}`);
      break;
    case '':  // System notifications (no routing needed)
      break;
  }
  // Then mark as read
  handleMarkOneRead(notification.id);
};
```

---

## 🟡 MEDIUM ISSUE #5: Unused Metadata

### The Data Available But Not Used

```javascript
// These fields come from API but are never read by frontend:
notification.related_object_type   // "lab_test", "appointment", etc.
notification.related_object_id     // 123, 456, 789, etc.

// These could be used for:
// 1. Router navigation
// 2. Prefetching related data
// 3. Analytics tracking
// 4. Smart notification grouping
```

### Backend Is Sending Correctly

```python
# /backend/notifications/serializers.py, Lines 16-17
fields = [
    "id", "title", "message", "notification_type", "is_read",
    "related_object_type",    # ✅ Sent
    "related_object_id",      # ✅ Sent  
    "created_at", "time_ago",
]
```

---

## 🟢 WORKING CORRECTLY: Profile Photos

### User Model Has It

```python
# /backend/users/models.py, Lines 21-24
profile_picture = models.ImageField(
    upload_to="profile_pics/",
    blank=True,
    null=True,
)
```

### Serializer Returns Absolute URLs

```python
# /backend/users/serializers.py, Lines 29-37
class AbsoluteImageURLField(serializers.ImageField):
    """Custom ImageField that returns absolute URLs."""
    
    def to_representation(self, value):
        """Return absolute URL for the image."""
        if not value:
            return None
        image_url = value.url
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(image_url)  # ✅ Returns full URL
        return image_url
```

### Doctor List Shows It

```python
# /backend/users/serializers.py, Lines 160-165
class DoctorListSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(
        source="user.profile_picture", read_only=True  # ✅ Correctly sourced
    )
```

---

## 🟢 WORKING CORRECTLY: Notification Creation

### Lab Tests

```python
# /backend/lab_tests/views.py, Lines 80-86
create_notification(
    recipient=lab_test.patient.user,
    title="Lab Test Ordered",
    notification_type="lab_result",
    related_object_type="lab_test",
    related_object_id=lab_test.id,
)
# ✅ Every lab test comes with notification
```

### Appointments

```python
# /backend/notifications/helpers.py, Lines 10-15
def create_appointment_notification(appointment):
    notification_type="appointment",
    related_object_type="appointment",
    related_object_id=appointment.id,
# ✅ Every appointment comes with notification
```

### Medications

```python
# /backend/medications/reminders.py, Lines 108-110
notify_with_notification(
    notification_type="medication",
    related_object_type="medication_reminder",
    related_object_id=med.id,
)
# ✅ Every medication reminder comes with notification
```

---

## 📍 REFERENCE MAP

### Backend Files
- Notifications: `/backend/notifications/` (models, views, serializers, helpers)
- Lab tests: `/backend/lab_tests/views.py` (creates notifications)
- Users/Doctors: `/backend/users/` (serializers, views, models)
- Medications: `/backend/medications/reminders.py` (creates reminders)
- Settings: `/backend/curova_backend/settings.py` (CORS, media)

### Frontend Files
- Notifications page: `/frontend/src/pages/common/Notifications.jsx`
- Dashboard layout: `/frontend/src/components/layout/DashboardLayout.jsx`
- Homepage: `/frontend/src/pages/public/Homepage.jsx`
- Patient appointments: `/frontend/src/pages/patient/Appointments.jsx`
- Doctor profile: `/frontend/src/pages/doctor/Profile.jsx`

### Configuration Files
- Backend settings: `/backend/curova_backend/settings.py` (CORS_ALLOWED_ORIGINS, MEDIA_URL, MEDIA_ROOT)
- Main URLs: `/backend/curova_backend/urls.py`
- API routes: `/backend/users/urls.py`, `/backend/notifications/urls.py`, etc.

---

**Report Date**: March 27, 2026
**Format**: Quick Reference & Code Snippets
