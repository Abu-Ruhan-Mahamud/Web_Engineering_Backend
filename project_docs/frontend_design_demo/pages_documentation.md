# CUROVA Healthcare Web Application - Pages Documentation

## 📋 Overview

This document provides a complete inventory of all UI pages created for the CUROVA Healthcare Web Application. The application serves three user roles: **Patients**, **Doctors**, and **Administrators**.

---

## 🎨 Design System

All pages follow a consistent design system:

- **Color Palette**: Teal/Blue scheme (#17a2b8, #1e3a8a, #74C3D0)
- **Typography**: Poppins font family
- **Components**: Consistent cards, buttons, forms, and navigation
- **Responsive**: Mobile-friendly across all breakpoints
- **Interactions**: Smooth transitions and hover effects

---

## 📄 Complete Page Inventory (16 Pages)

### **Public Pages (3)**

| # | Page Name | File | Purpose |
|---|-----------|------|---------|
| 1 | Homepage | `curova_homepage.html` | Public landing page with services, doctors, and testimonials |
| 2 | Login | `curova-login-page.html` | User authentication for all roles |
| 3 | Registration | `curova_registration.html` | New user account creation |

---

### **Admin Pages (3)**

| # | Page Name | File | Purpose |
|---|-----------|------|---------|
| 4 | Admin Dashboard | `curova_dashboard.html` | System overview with statistics and charts |
| 5 | Patient Management | `curova-patient-page.html` | View and manage all patients in the system |
| 6 | Appointments Calendar | `curova_appointments.html` | Manage appointments with calendar view |

---

### **Patient Pages (6)**

| # | Page Name | File | Purpose |
|---|-----------|------|---------|
| 7 | Patient Dashboard | `patient_dashboard` | Personal health overview with appointments and medications |
| 8 | Medical Records | `patient_medical_records` | View complete medical history and diagnoses |
| 9 | Profile Settings | `patient_profile` | Manage personal info, medical info, and security |
| 10 | Book Appointment | `patient_book_appointment` | Multi-step appointment booking with doctor selection |
| 11 | Documents Gallery | `patient_documents` | Upload and view medical documents (X-rays, reports) |
| 12 | Messages | `messaging_chat` | Chat with doctors and healthcare providers |

---

### **Doctor Pages (4)**

| # | Page Name | File | Purpose |
|---|-----------|------|---------|
| 13 | Doctor Dashboard | `doctor_dashboard` | Today's schedule overview and quick stats |
| 14 | Patient Details | `doctor_patient_detail` | View complete patient profile and medical timeline |
| 15 | Create Medical Record | `doctor_create_record` | Document consultations, diagnoses, and prescriptions |
| 16 | Schedule Management | `doctor_schedule_management` | Set availability, working hours, and time slots |

---

## 🔑 Key Features by Role

### 👤 Patient Features
- ✅ Dashboard with health overview
- ✅ Book appointments with doctor selection
- ✅ View medical records and history
- ✅ Manage profile and medical information
- ✅ Upload/view medical documents
- ✅ Real-time messaging with doctors
- ✅ Track current medications

### 👨‍⚕️ Doctor Features
- ✅ Dashboard with daily schedule
- ✅ View patient details and complete history
- ✅ Create medical records with prescriptions
- ✅ Manage weekly availability and time slots
- ✅ Real-time messaging with patients
- ✅ Calendar view of appointments
- ✅ Patient management tools

### 🔐 Admin Features
- ✅ System overview dashboard
- ✅ Manage all patients
- ✅ View and manage appointments
- ✅ System statistics and analytics
- ✅ User management capabilities

---

## 📊 Technical Specifications

### Frontend Technologies
- **Framework**: React.js (as per design document)
- **Styling**: Custom CSS with consistent design system
- **Layout**: Responsive grid-based layouts
- **Icons**: SVG icons for scalability
- **Fonts**: Google Fonts (Poppins)

### Design Patterns
- **Three-tier architecture**: Presentation, Application, Data layers
- **Component-based**: Reusable UI components
- **Mobile-first**: Responsive design approach
- **Accessibility**: Semantic HTML and proper contrast ratios

### Integration Points
All pages are designed to integrate with:
- Django REST API backend
- PostgreSQL database
- JWT token authentication
- Role-based access control (RBAC)

---

## 🗂️ Page Categories

### Authentication Flow
1. Homepage → Registration/Login
2. Login → Role-based Dashboard (Patient/Doctor/Admin)

### Patient User Flow
1. Patient Dashboard
2. Book Appointment → Medical Records
3. View Documents → Messages
4. Profile Settings

### Doctor User Flow
1. Doctor Dashboard
2. View Patients → Patient Details
3. Create Medical Record → Schedule Management
4. Messages

### Admin User Flow
1. Admin Dashboard
2. Patient Management → Appointments Calendar
3. System Overview

---

## 📝 Notes

- All pages include proper navigation headers
- Forms include validation and error handling
- Modal dialogs for actions like uploads and scheduling
- Loading states and empty states handled
- Consistent date/time formatting throughout
- Search and filter functionality where applicable

---

## 🚀 Implementation Status

**Status**: ✅ All 16 pages complete and ready for development

**Next Steps**:
1. Integrate with Django REST API
2. Implement authentication flow
3. Connect to PostgreSQL database
4. Add real-time messaging with WebSockets
5. Implement file upload functionality
6. Add data validation and error handling

---

## 📧 Project Information

**Project**: CUROVA Healthcare Web Application  
**Course**: CSE-616: Web Engineering Lab  
**Institution**: University of Chittagong  
**Group**: 11  
**Submission Date**: October 22, 2025

---

*This documentation covers all UI pages created for the D2: Design Document submiss