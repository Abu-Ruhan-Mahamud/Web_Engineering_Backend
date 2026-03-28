# ISSUE SUMMARY CHECKLIST
## Curova Healthcare Application - March 27, 2026

---

## 🔴 CRITICAL ISSUES (MUST FIX)

### Issue #1: Notification Click Navigation Missing
- **Severity**: 🔴 CRITICAL
- **Impact**: Users cannot navigate to lab results/appointments by clicking notifications
- **Files Affected**: 
  - `/frontend/src/pages/common/Notifications.jsx`
  - `/frontend/src/components/layout/DashboardLayout.jsx`
- **Details**: 
  - Backend correctly creates notifications with `related_object_type` and `related_object_id`
  - Frontend API receives this data but has NO click handlers
  - Currently only marks notification as read
  - Need to add routing logic based on notification type
- **Example**: Click "Lab Test Ready" → Should navigate to lab results, currently does nothing

---

### Issue #2: Doctor Listing Endpoint Requires Authentication
- **Severity**: 🔴 CRITICAL  
- **Impact**: Public homepage cannot show real doctors; homepage hardcoded with dummy data
- **File Affected**: `/backend/users/views.py` line 380
- **Details**:
  - Endpoint: `GET /api/auth/doctors/`
  - Current: `@permission_classes([IsAuthenticated])` - REQUIRES LOGIN
  - Should be: `@permission_classes([AllowAny])` - PUBLIC ACCESS
  - Comment in code says "public for booking" but has auth decorator
  - Blocks public doctor discovery
- **Fix**: 1 line change in one file

---

### Issue #3: Homepage Uses Hardcoded Fake Doctor Data
- **Severity**: 🔴 CRITICAL
- **Impact**: Homepage displays fake doctors instead of real ones
- **File Affected**: `/frontend/src/pages/public/Homepage.jsx` lines 7-12
- **Hardcoded Doctors**:
  - Dr. Nusrat Jahan (Fake)
  - Dr. Tanvir Rahman (Fake)
  - Dr. Shakil Ahmed (Fake)
  - Dr. Mahmudul Islam (Fake)
  - Dr. Md. Arif Hossain (Fake)
- **Images**: All from Unsplash CDN, not real profiles
- **Code Comment**: "TODO: Replace with real API data when doctor public profiles are ready." (Line 6)
- **Status**: Not yet updated despite having the infrastructure
- **Fix Requires**: 
  1. First fix Issue #2 (make endpoint public)
  2. Then fetch real doctors dynamically in Homepage.jsx

---

## 🟡 MEDIUM PRIORITY ISSUES

### Issue #4: No Notification Route Handlers
- **Severity**: 🟡 MEDIUM
- **Impact**: Some notification types cannot navigate properly
- **Files Affected**: `/frontend/src/components/layout/DashboardLayout.jsx`
- **Details**:
  - Notification types: APPOINTMENT, MEDICATION, LAB_RESULT, PRESCRIPTION, SYSTEM
  - All have related_object_id data in API response
  - No switch/if statement to handle routing by type
  - Need different navigation for each type:
    - LAB_RESULT → `/patient/lab-tests/{id}`
    - APPOINTMENT → `/patient/appointments/{id}`
    - MEDICATION → `/patient/medications/{id}`
    - PRESCRIPTION → `/patient/medical-records/{id}`
    - SYSTEM → No navigation needed

---

### Issue #5: Notification Metadata Not Utilized
- **Severity**: 🟡 MEDIUM
- **Impact**: Frontend has access to IDs but never uses them
- **Details**:
  - Backend sends: `related_object_type` and `related_object_id` in every notification
  - Frontend receives: These fields from API
  - Frontend uses: NONE of this data
  - Fields just sit unused in the JSON response
- **Status**: Data properly created and sent, just not used on frontend

---

## 🟢 WORKING CORRECTLY

### ✅ Profile Photo System
- **Status**: Working
- **What's Done Right**:
  - User model has `profile_picture` field
  - Photos uploaded correctly to `/media/profile_pics/`
  - Serializer returns absolute URLs
  - Frontend displays correctly in dashboard and profiles
  - CORS configured for media access
- **No Action Needed**: This works perfectly

---

### ✅ Notification Creation
- **Status**: Working
- **Details**:
  - All notification types created with proper metadata
  - Related object IDs correctly stored
  - Lab test notifications created when test ordered
  - Appointment notifications created when scheduled
  - Medication reminders created on schedule
  - Prescription notifications created when issued
- **No Action Needed**: Backend is perfect, frontend just needs to use the data

---

### ✅ Media File Serving
- **Status**: Working
- **Details**:
  - Profile pictures served from `/media/profile_pics/`
  - Lab results served from `/media/lab_results/`
  - CORS properly configured
  - Absolute URLs working correctly
- **No Action Needed**: Infrastructure is solid

---

## 📋 DETAILED CHECKLIST

### Notification System
- [ ] ✅ Notification model has metadata fields
- [ ] ✅ Notification creation includes related_object_type
- [ ] ✅ Notification creation includes related_object_id
- [ ] ✅ API serializer returns all fields
- [ ] ❌ Frontend Notifications page shows click handler
- [ ] ❌ Frontend Dropdown shows click handler
- [ ] ❌ Click navigates to related resource
- [ ] ❌ All notification types have routes

### Profile Photo Management
- [ ] ✅ User model has profile_picture field
- [ ] ✅ Doctor inherits profile_picture from User
- [ ] ✅ Serializer includes profile_picture
- [ ] ✅ Upload endpoint working
- [ ] ✅ Download URLs working
- [ ] ✅ Profile display shows picture
- [ ] ✅ Doctor list shows pictures

### Doctor Discovery
- [ ] ❌ Public endpoint allows unauthenticated access
- [ ] ❌ Homepage fetches real doctors
- [ ] ❌ Homepage removes dummy data
- [ ] ❌ Public users can browse doctors
- [ ] ✅ Authenticated users can search doctors

### Routes & Permissions
- [ ] ✅ Registration public (AllowAny)
- [ ] ✅ Login public (AllowAny)
- [ ] ✅ Google auth public (AllowAny)
- [ ] ❌ Doctor list allows public (should be AllowAny, is IsAuthenticated)
- [ ] ✅ Notifications require auth
- [ ] ✅ Lab tests require auth
- [ ] ✅ Appointments require auth

---

## 🎯 QUICK FIX GUIDE

### Fix #1 (5 minutes)
**Make doctor endpoint public**
```
File: /backend/users/views.py
Line: 380
Change: @permission_classes([IsAuthenticated])
To: @permission_classes([AllowAny])
```

### Fix #2 (30 minutes)  
**Replace homepage dummy data with real doctors**
```
File: /frontend/src/pages/public/Homepage.jsx
Action: 
1. Remove hardcoded doctors array (lines 7-12)
2. Add useEffect to fetch from /api/auth/doctors/
3. Handle loading/error states
4. Update rendering to use fetched data
```

### Fix #3 (1-2 hours)
**Add notification click navigation**
```
Files: 
- /frontend/src/pages/common/Notifications.jsx
- /frontend/src/components/layout/DashboardLayout.jsx

Changes:
1. Add function handleNotificationClick(notification)
2. Switch on notification.related_object_type
3. Navigate using useNavigate() based on type
4. Use notification.related_object_id for routing

Example routes:
- lab_test → /patient/lab-tests/${id}
- appointment → /patient/appointments/${id}
- medication_reminder → /patient/medications/${id}
- medical_record → /patient/medical-records/${id}
```

---

## 📊 SUMMARY TABLE

| Issue | Type | Priority | Fixable | Est. Time | Files |
|-------|------|----------|---------|-----------|-------|
| No notification navigation | Bug | 🔴 Critical | Yes | 1-2h | 2 |
| Doctor endpoint auth | Bug | 🔴 Critical | Yes | 5m | 1 |
| Dummy homepage data | Bug | 🔴 Critical | Yes | 30m | 1 |
| No type-based routes | Design | 🟡 Medium | Yes | 1h | 2 |
| Unused metadata | Design | 🟡 Medium | Yes | 30m | 1 |
| Profile photos | Feature | 🟢 OK | - | - | - |
| Notification creation | Feature | 🟢 OK | - | - | - |
| Media serving | Feature | 🟢 OK | - | - | - |

---

## 🚀 NEXT STEPS

1. **Immediate**: Apply Fix #1 (5 minutes)
2. **Short-term**: Apply Fix #2 (30 minutes)  
3. **Medium-term**: Apply Fix #3 (1-2 hours)
4. **Verification**: Test all fixes with actual doctor accounts and notifications

---

**Report Date**: March 27, 2026
**Total Critical Issues**: 3
**Total Medium Issues**: 2  
**Total Working Components**: 3
