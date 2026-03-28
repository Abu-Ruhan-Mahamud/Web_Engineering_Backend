# COMPREHENSIVE INVESTIGATION REPORT
## Curova Healthcare Application - March 27, 2026

---

## 📋 ISSUE CHECKLIST BY CATEGORY

### 🔴 CRITICAL ISSUES (Blocks Core Features)

#### 1. **NOTIFICATION NAVIGATION MISSING**
- **Status**: ❌ BROKEN
- **Impact**: Users cannot navigate to lab results/appointments by clicking notifications
- **Severity**: CRITICAL - Core feature non-functional
- **Components Affected**:
  - `/frontend/src/pages/common/Notifications.jsx` (Full notifications page)
  - `/frontend/src/components/layout/DashboardLayout.jsx` (Notification dropdown)

**Issue Details**:
- Backend: ✅ Correctly creates notifications with `related_object_type` and `related_object_id`
  - Example: Lab test notification includes `related_object_type="lab_test"`, `related_object_id=123`
  - File: `/backend/lab_tests/views.py` (lines 80-86)
- API: ✅ Correctly returns related object data
  - Notification serializer includes these fields
  - File: `/backend/notifications/serializers.py` (lines 16-17)
- Frontend: ❌ **IGNORES THESE FIELDS COMPLETELY**
  - Notifications.jsx: Shows notification text but has NO click handler for navigation
  - DashboardLayout.jsx: Only marks as read, no navigation logic
  - No function to route based on `notification_type` and `related_object_id`

**Fix Required**:
1. Add click handler to notification items that checks `related_object_type`
2. Route based on type:
   - `lab_test` → Navigate to `/patient/lab-tests/{related_object_id}`
   - `appointment` → Navigate to `/patient/appointments/{related_object_id}`
   - `medication_reminder` → Navigate to `/patient/medications/{related_object_id}`
   - `medical_record` → Navigate to `/patient/medical-records/{related_object_id}`
3. Update both Notifications.jsx and DashboardLayout.jsx

---

#### 2. **DOCTOR LISTING ENDPOINT REQUIRES AUTHENTICATION**
- **Status**: ❌ BROKEN
- **Impact**: Public users cannot see doctors before login; homepage has hardcoded dummy data
- **Severity**: CRITICAL - Blocks public doctor discovery
- **Endpoint**: `GET /api/auth/doctors/`

**Issue Details**:
- Marked as "public for booking" in code comment (line 375)
- Declaration: `@permission_classes([IsAuthenticated])` (line 380)
- File: `/backend/users/views.py` (lines 375-400)
- Result: Only authenticated users see real doctors
- Workaround: Homepage uses hardcoded dummy doctor data

**Usage**:
- Patient appointments booking: `/frontend/src/pages/patient/Appointments.jsx` (line 367)
  - Calls `api.get('/auth/doctors/', { params })`
  - Only works if user is logged in
- Public homepage: Shows fake doctors because it can't access real API

**Fix Required**:
Change line 380 from:
```python
@permission_classes([IsAuthenticated])
```
To:
```python
@permission_classes([AllowAny])
```
This allows public access while still requiring auth for authenticated users.

---

#### 3. **HOMEPAGE USES HARDCODED DUMMY DOCTOR DATA**
- **Status**: ❌ NOT USING REAL DATA
- **Impact**: Homepage displays fake doctors, not real system doctors
- **Severity**: CRITICAL - Destroys credibility
- **File**: `/frontend/src/pages/public/Homepage.jsx` (lines 7-12)

**Hardcoded Data**:
```javascript
const doctors = [
  { name: 'Dr. Nusrat Jahan', specialty: 'Orthotic Surgeon', location: 'Chattogram, Bangladesh', 
    img: 'https://images.unsplash.com/photo-1559839734-...' },
  { name: 'Dr. Tanvir Rahman', specialty: 'Neurologist', location: 'Dhaka, Bangladesh',
    img: 'https://images.unsplash.com/photo-1612349317150-...' },
  // ... 4 more fake doctors
];
```

**TODO Comment** (Line 6):
```javascript
// TODO: Replace with real API data when doctor public profiles are ready.
```

**Issues**:
1. All doctor names are fake
2. All photos are from Unsplash CDN, not actual doctor photos
3. Cannot be updated without code change
4. No connection to actual doctors in database

**Fix Required**:
1. First: Make `/api/auth/doctors/` endpoint public (see issue #2)
2. Then: Fetch real doctors in Homepage.jsx:
   ```javascript
   useEffect(() => {
     const fetchDoctors = async () => {
       try {
         const res = await api.get('/auth/doctors/?page_size=6');
         setDoctors(res.data.results || []);
       } catch (err) {
         setDoctors([]); // Fallback to empty
       }
     };
     fetchDoctors();
   }, []);
   ```
3. Use real doctor data instead of hardcoded array

---

### 🟡 MEDIUM PRIORITY ISSUES

#### 4. **PROFILE PICTURE FIELD NAMING INCONSISTENCY (MINOR)**
- **Status**: ⚠️ WORKING BUT COULD BE CLEARER
- **Impact**: None (naming consistency only)
- **Severity**: LOW
- **Details**:
  - User model field name: `profile_picture` (✅ consistent)
  - API returns: `profile_picture` (✅ consistent)
  - Frontend expects: `profile_picture` (✅ consistent)

**What Works**:
- Profile upload: ✅ Working via PUT `/api/auth/me/`
- Profile display: ✅ Working in DashboardLayout and patient profile
- Doctor list display: ✅ Returns profile_picture URLs
- Absolute URL handling: ✅ Using custom AbsoluteImageURLField

**Potential Issue**: None identified. System is working correctly.

---

#### 5. **MISSING NOTIFICATION TYPE HANDLERS**
- **Status**: ⚠️ PARTIAL IMPLEMENTATION
- **Impact**: Not all notification types can navigate to resources
- **Severity**: MEDIUM
- **File**: DashboardLayout notification dropdown (lines 150-160 approx.)

**Current Notification Types** (from notifications/models.py):
1. ✅ `APPOINTMENT` - Has related_object_type="appointment"
2. ✅ `MEDICATION` - Has related_object_type="medication_reminder"
3. ✅ `LAB_RESULT` - Has related_object_type="lab_test"
4. ✅ `PRESCRIPTION` - Has related_object_type="medical_record"
5. ✅ `SYSTEM` - No related object (general notifications)

**What's Missing**:
- No navigation routes for ANY type
- No switch statement to handle different types
- Currently just marks as read

---

### 🟢 WORKING AS INTENDED

#### 6. **PROFILE PHOTO UPLOAD & STORAGE**
- **Status**: ✅ WORKING
- **Components**:
  - Model field: `profile_picture` in User model
  - Upload handler: PUT `/api/auth/me/` with multipart form data
  - Storage: Django's media files to `/media/profile_pics/`
  - Serialization: AbsoluteImageURLField returns full URLs
  - Display: Works in DashboardLayout and profile pages

---

#### 7. **NOTIFICATION CREATION WITH METADATA**
- **Status**: ✅ WORKING
- **Details**:
  - All notifications include `related_object_type` and `related_object_id`
  - Lab tests (views.py line 80-86): Creates notification with lab_test reference
  - Appointments (helpers.py line 12-14): Creates notification with appointment reference
  - Medications (reminders.py line 108-110): Creates notification with medication reference
  - API returns all metadata in serializer response

---

#### 8. **MEDIA FILE SERVING & CORS**
- **Status**: ✅ WORKING
- **Configuration**:
  - CORS enabled for localhost (http://localhost:5173, http://127.0.0.1:5173)
  - Media URL: `/media/` served from Django
  - Profile pictures accessible at: `http://localhost:8000/media/profile_pics/{filename}`
  - Lab results accessible at: `http://localhost:8000/media/lab_results/{filename}`

---

## 📊 DETAILED ANALYSIS BY COMPONENT

### NOTIFICATION SYSTEM

**Backend (✅ Working)**:
| Component | Status | Details |
|-----------|--------|---------|
| Notification Model | ✅ | Has related_object_type, related_object_id fields |
| Serializer | ✅ | Includes all fields in API response |
| Lab Test Creation | ✅ | Creates with related_object_id=lab_test.id |
| Appointment Creation | ✅ | Creates with related_object_id=appointment.id |
| Medication Creation | ✅ | Creates with related_object_id=medication.id |
| Prescription Creation | ✅ | Creates with related_object_id=medical_record.id |

**Frontend (❌ Broken)**:
| Component | Status | Issue |
|-----------|--------|-------|
| Notifications Page | ❌ | No navigation on click |
| Notification Dropdown | ❌ | Only marks as read, no routing |
| Related Object Handling | ❌ | Fields received but never used |
| Type-based Routing | ❌ | No switch for routing by type |

---

### DOCTOR DISCOVERY

**Backend Issue**:
| Endpoint | Permission | Expected | Actual | Issue |
|----------|-----------|----------|--------|-------|
| `/api/auth/doctors/` | AllowAny? | Public | IsAuthenticated | ❌ Requires auth |
| Comment says | "public" | - | "public for booking" | Auth mismatch |

**Frontend Issue**:
| Location | Status | Issue |
|----------|--------|-------|
| Homepage.jsx | ❌ | Uses hardcoded dummy data |
| TODO comment | ❌ | "Replace with real API data" |
| Appointment booking | ⚠️ | Works but only for logged-in users |

---

### PROFILE PHOTOS

**User Model**:
- Field: `profile_picture: ImageField(upload_to="profile_pics/", blank=True, null=True)`
- Location: `/backend/users/models.py` line 21

**Doctor Access**:
- Doctors inherit profile_picture from User (1:1 relationship)
- Accessed via: `doctor.user.profile_picture`
- Serialized in DoctorListSerializer: `source="user.profile_picture"`

**Serialization**:
- AbsoluteImageURLField: Converts relative to absolute URLs
- Returns: `http://localhost:8000/media/profile_pics/filename.jpg`
- Works in: DoctorListSerializer, UserSerializer

**Frontend Display**:
- DashboardLayout: Uses `user.profile_picture` for avatar
- Patient profile: Shows and allows upload
- Doctor profile: Cannot show (no frontend page to display)

---

## 🔍 CODE LOCATIONS REFERENCE

### Backend Files

**Notification System**:
- Models: `/backend/notifications/models.py` (lines 1-43)
- Serializers: `/backend/notifications/serializers.py` (lines 1-35)
- Views: `/backend/notifications/views.py` (all endpoints)
- Helpers: `/backend/notifications/helpers.py` (creation functions)

**Lab Tests**:
- Views: `/backend/lab_tests/views.py` (line 80-86 for notification creation)
- Models: `/backend/lab_tests/models.py` (LabTest, LabTestResult)

**User/Doctor**:
- Models: `/backend/users/models.py` (User line 21, Doctor model)
- Serializers: `/backend/users/serializers.py` (UserSerializer, DoctorListSerializer)
- Views: `/backend/users/views.py` (doctor_list_view at line 380)
- URLs: `/backend/users/urls.py` (line 18)

**Medications**:
- Reminders: `/backend/medications/reminders.py` (line 108-110)

---

### Frontend Files

**Notifications**:
- Full Page: `/frontend/src/pages/common/Notifications.jsx` (lines 1-400+)
- Dropdown: `/frontend/src/components/layout/DashboardLayout.jsx` (lines 233-280)
- Styles: `/frontend/src/styles/notifications.css`

**Homepage**:
- File: `/frontend/src/pages/public/Homepage.jsx` (lines 7-12 dummy data)

**Doctor Related**:
- Appointments: `/frontend/src/pages/patient/Appointments.jsx` (line 367 API call)
- Doctor Profile: `/frontend/src/pages/doctor/Profile.jsx`

---

## 🛠️ RECOMMENDED FIXES (Implementation Order)

### PHASE 1: AUTHENTICATION (Required for other fixes)
1. **Make doctor endpoint public** (5 min)
   - Change: `/backend/users/views.py` line 380
   - From: `@permission_classes([IsAuthenticated])`
   - To: `@permission_classes([AllowAny])`

### PHASE 2: HOMEPAGE (Depends on Phase 1)
2. **Replace dummy doctors with real data** (30 min)
   - File: `/frontend/src/pages/public/Homepage.jsx`
   - Add useEffect to fetch from `/api/auth/doctors/?page_size=6`
   - Remove hardcoded doctors array
   - Update rendering to use real data

### PHASE 3: NOTIFICATION NAVIGATION (Most Complex)
3. **Add notification click handlers** (1-2 hours)
   - Files: `Notifications.jsx`, `DashboardLayout.jsx`
   - Add function to route based on `related_object_type` and `related_object_id`
   - Route to appropriate page for each type:
     - lab_test → Lab test detail
     - appointment → Appointment detail
     - medication_reminder → Medication detail
     - medical_record → Medical record detail
     - (Other types as applicable)

---

## 📈 IMPACT SUMMARY

| Issue | Category | Users Affected | Critical | Fixable |
|-------|----------|----------------|----------|---------|
| Notification navigation | Feature | Authenticated users | Yes | Yes |
| Doctor listing auth | Feature | Public + Authenticated | Yes | Yes |
| Homepage dummy data | Feature | Public visitors | Yes | Yes |
| Profile photo naming | Clarity | Developers | No | N/A |
| Notification type handlers | UI/UX | All users | No | Yes |

---

## 🎯 VERIFICATION CHECKLIST

After fixes are implemented, verify:

- [ ] Clicking a lab result notification navigates to `/patient/lab-tests/{id}`
- [ ] Clicking an appointment notification navigates to `/patient/appointments/{id}`
- [ ] Public users can see real doctors on homepage (no auth required)
- [ ] Logged-in users can search/filter doctors when booking
- [ ] Profile pictures display correctly for all doctors
- [ ] Notification dropdown and full page have consistent behavior
- [ ] All notification types have proper navigation
- [ ] API `/auth/doctors/` works for both authenticated and public requests

---

**Generated**: March 27, 2026
**Investigation Scope**: Notification system, profile photos, doctor discovery, related auth/media issues
**Status**: 3 Critical Issues Found + 2 Medium Issues + 3 Components Working Correctly
