# CUROVA Healthcare Management System

## Final Project Documentation

This document is the final consolidated project documentation, prepared by following the capstone guideline flow (deliverable sequence without timeline dependence), reconciling early D1/D2 plans with the final implemented system.

---

## 1. Deliverable-Based Development Flow (Guideline-Aligned)

The project is documented in the standard development progression:

1. Problem definition and scope
2. Requirements analysis (functional and non-functional)
3. System architecture and design decisions
4. Data model and API design
5. Implementation (backend and frontend)
6. Testing and validation
7. Deployment and operational setup
8. Limitations, lessons learned, and future work

This follows the expected capstone structure while intentionally ignoring date constraints, as requested.

---

## 2. Problem Statement and Scope

Healthcare workflows for appointment booking, medical record access, prescriptions, and lab workflows are usually fragmented and role-dependent. Curova addresses this by providing a role-based web system for:

- Patients: profile, appointments, records, prescriptions, documents, medications, lab results
- Doctors: schedule, patients, record creation, lab test review
- Lab technicians: lab order handling and result updates
- Admin: user and appointment oversight

The scope is web-first, with REST APIs powering a React frontend.

---

## 3. D1 and D2 vs Final Implementation

## 3.1 D1 (Initial Requirements) Baseline

From [project_docs/d1.tex](project_docs/d1.tex), core goals included:

- Multi-role auth and access control
- Patient booking and history
- Doctor schedule and treatment workflow
- Admin user oversight
- Document handling
- Medication tracking and reminders

## 3.2 D2 (Initial Design) Baseline

From [project_docs/d2.tex](project_docs/d2.tex), planned design emphasized:

- Three-tier architecture (frontend, backend, database)
- Django + DRF backend and PostgreSQL relational model
- Role-segmented UI and endpoint responsibilities
- ER-driven data model design with healthcare entities

## 3.3 What Changed During Implementation

Compared with early D1/D2, final implementation evolved in these ways:

1. Stronger domain modularization
- The backend is split across dedicated apps: users, appointments, medical, medications, documents, lab_tests, notifications, messaging.

2. Notifications matured as a separate bounded context
- Unified notification model and endpoints were implemented in [backend/notifications/models.py](backend/notifications/models.py), [backend/notifications/views.py](backend/notifications/views.py), [backend/notifications/urls.py](backend/notifications/urls.py).

3. Messaging remained deferred
- Messaging URL module exists but has no active endpoints in [backend/messaging/urls.py](backend/messaging/urls.py).

4. Medication reminder model exists, but reminder CRUD routes are not currently exposed in URLs
- View functions exist in [backend/medications/views.py](backend/medications/views.py), but [backend/medications/urls.py](backend/medications/urls.py) currently exposes only medications list/create.

5. Production/deployment strategy pivoted
- Final deployment was moved to Render (frontend, backend, database), replacing earlier platform directions.

---

## 4. Final System Architecture

Curova uses a three-tier architecture:

1. Presentation tier
- React + Vite frontend in [frontend/src](frontend/src)

2. Application tier
- Django + DRF backend in [backend](backend)

3. Data tier
- PostgreSQL as primary relational database

## 4.1 Request Flow Summary

A typical request follows:

1. Frontend route/action in [frontend/src/App.jsx](frontend/src/App.jsx)
2. Axios request via service layer (for example [frontend/src/services/api.js](frontend/src/services/api.js))
3. Django URL resolution in [backend/curova_backend/urls.py](backend/curova_backend/urls.py)
4. DRF view with authentication/permission checks
5. Serializer validation
6. ORM read/write to PostgreSQL
7. JSON response to frontend

---

## 5. Technology Stack

## 5.1 Backend

- Python
- Django 6.x
- Django REST Framework
- PostgreSQL
- Token authentication (DRF token auth)
- django-cors-headers
- gunicorn (deployment)

Dependencies are listed in [backend/requirements.txt](backend/requirements.txt).

## 5.2 Frontend

- React 19
- Vite 7
- React Router
- Axios

Dependencies are listed in [frontend/package.json](frontend/package.json).

---

## 6. Backend Module Documentation

## 6.1 Root Configuration

- Global URLs: [backend/curova_backend/urls.py](backend/curova_backend/urls.py)
- Settings: [backend/curova_backend/settings.py](backend/curova_backend/settings.py)
- Custom pagination helper: [backend/curova_backend/pagination.py](backend/curova_backend/pagination.py)

## 6.2 users app

Key files:

- Models: [backend/users/models.py](backend/users/models.py)
- Views: [backend/users/views.py](backend/users/views.py)
- Permissions: [backend/users/permissions.py](backend/users/permissions.py)
- User endpoints: [backend/users/urls.py](backend/users/urls.py)
- Admin endpoints: [backend/users/admin_urls.py](backend/users/admin_urls.py)

Responsibilities:

- Registration, login, logout, Google login
- Profile and password updates
- Patient/doctor role-specific profile behavior
- Admin APIs for user and appointment oversight

## 6.3 appointments app

- Models: [backend/appointments/models.py](backend/appointments/models.py)
- Serializers: [backend/appointments/serializers.py](backend/appointments/serializers.py)
- Views: [backend/appointments/views.py](backend/appointments/views.py)
- URLs: [backend/appointments/urls.py](backend/appointments/urls.py)

Responsibilities:

- Booking flow and slot validation
- Appointment list/detail per role context
- Status update handling
- Booked-slots query endpoint

## 6.4 medical app

- Models: [backend/medical/models.py](backend/medical/models.py)
- Serializers: [backend/medical/serializers.py](backend/medical/serializers.py)
- Views: [backend/medical/views.py](backend/medical/views.py)
- URLs: [backend/medical/urls.py](backend/medical/urls.py)

Responsibilities:

- Medical record read/write
- Prescription linkage
- Doctor-centric record creation

## 6.5 medications app

- Models: [backend/medications/models.py](backend/medications/models.py)
- Serializers: [backend/medications/serializers.py](backend/medications/serializers.py)
- Views: [backend/medications/views.py](backend/medications/views.py)
- URLs: [backend/medications/urls.py](backend/medications/urls.py)
- Reminder utility: [backend/medications/reminders.py](backend/medications/reminders.py)

Responsibilities:

- Medication listing/creation
- Reminder model support and helper logic
- Reminder API methods present in views but currently not mounted in URLs

## 6.6 documents app

- Models: [backend/documents/models.py](backend/documents/models.py)
- Serializers: [backend/documents/serializers.py](backend/documents/serializers.py)
- Views: [backend/documents/views.py](backend/documents/views.py)
- URLs: [backend/documents/urls.py](backend/documents/urls.py)

Responsibilities:

- Medical document upload and retrieval
- Ownership and role-aware access checks

## 6.7 lab_tests app

- Models: [backend/lab_tests/models.py](backend/lab_tests/models.py)
- Serializers: [backend/lab_tests/serializers.py](backend/lab_tests/serializers.py)
- Views: [backend/lab_tests/views.py](backend/lab_tests/views.py)
- URLs: [backend/lab_tests/urls.py](backend/lab_tests/urls.py)

Responsibilities:

- Lab test order lifecycle
- Result upload and update
- Doctor/lab role-specific transitions

## 6.8 notifications app

- Models: [backend/notifications/models.py](backend/notifications/models.py)
- Serializers: [backend/notifications/serializers.py](backend/notifications/serializers.py)
- Views: [backend/notifications/views.py](backend/notifications/views.py)
- URLs: [backend/notifications/urls.py](backend/notifications/urls.py)
- Helpers: [backend/notifications/helpers.py](backend/notifications/helpers.py)

Responsibilities:

- Notification list and unread counts
- Mark read, mark all read, delete, clear
- Event notifications from other domains

## 6.9 messaging app (deferred)

- URLs currently empty: [backend/messaging/urls.py](backend/messaging/urls.py)

---

## 7. Data Model Overview

Primary entities and relationship intent:

1. User (custom auth entity)
2. Patient (1:1 extension of user)
3. Doctor (1:1 extension of user)
4. Appointment (patient-doctor scheduling)
5. MedicalRecord (patient-doctor clinical data)
6. Prescription (linked to medical record)
7. Medication (current medication tracking)
8. MedicationReminder (reminder definition)
9. MedicalDocument (patient document uploads)
10. LabTest (ordered test)
11. LabTestResult (test result payload)
12. Notification (cross-domain user notifications)

For exact schema fields, see model files under:
- [backend/users/models.py](backend/users/models.py)
- [backend/appointments/models.py](backend/appointments/models.py)
- [backend/medical/models.py](backend/medical/models.py)
- [backend/medications/models.py](backend/medications/models.py)
- [backend/documents/models.py](backend/documents/models.py)
- [backend/lab_tests/models.py](backend/lab_tests/models.py)
- [backend/notifications/models.py](backend/notifications/models.py)

---

## 8. Authentication and Authorization

Authentication:

- Token-based authentication using DRF token flow
- Primary auth endpoints in [backend/users/urls.py](backend/users/urls.py)

Authorization:

- Role-aware permission classes in [backend/users/permissions.py](backend/users/permissions.py)
- Endpoint-level checks in each app view

User roles:

- patient
- doctor
- admin
- lab_tech

---

## 9. API Documentation (Backend)

Base URL pattern:

- Health: /health/
- API root: /api/
- Auth namespace: /api/auth/
- Admin namespace: /api/admin/

## 9.1 Health

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | /health/ | Service health check | No |

Defined in [backend/curova_backend/urls.py](backend/curova_backend/urls.py).

## 9.2 Auth and User Endpoints

From [backend/users/urls.py](backend/users/urls.py) and [backend/users/views.py](backend/users/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | /api/auth/register/ | Register user | No |
| POST | /api/auth/login/ | Login and token issue | No |
| POST | /api/auth/google-login/ | Google login | No |
| POST | /api/auth/logout/ | Logout/token invalidation | Yes |
| POST | /api/auth/delete-account/ | Account anonymization/deactivation | Yes |
| GET, PUT | /api/auth/me/ | Current user profile details/update | Yes |
| POST | /api/auth/change-password/ | Password change | Yes |
| GET, PUT | /api/auth/profile/ | Patient profile view/update | Patient |
| GET | /api/auth/dashboard-stats/ | Patient dashboard stats | Patient |
| GET | /api/auth/doctors/ | Doctor list | Authenticated |
| GET | /api/auth/doctor/dashboard-stats/ | Doctor dashboard stats | Doctor |
| GET, PUT | /api/auth/doctor/profile/ | Doctor profile | Doctor |
| GET, PUT | /api/auth/doctor/schedule/ | Doctor schedule | Doctor |
| GET | /api/auth/doctor/patients/ | Doctor patient list | Doctor |
| GET | /api/auth/doctor/patients/{patient_id}/ | Doctor patient detail | Doctor |

## 9.3 Admin Endpoints

From [backend/users/admin_urls.py](backend/users/admin_urls.py) and [backend/users/admin_views.py](backend/users/admin_views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | /api/admin/stats/ | Admin statistics | Admin |
| GET, POST | /api/admin/users/ | List/create users | Admin |
| GET, PATCH | /api/admin/users/{user_id}/ | User detail/update state | Admin |
| GET | /api/admin/appointments/ | Appointment oversight list | Admin |
| GET | /api/admin/appointments/export/ | Appointment export | Admin |

## 9.4 Appointments

From [backend/appointments/urls.py](backend/appointments/urls.py) and [backend/appointments/views.py](backend/appointments/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET, POST | /api/appointments/ | List appointments / create appointment | Authenticated (role-scoped) |
| GET | /api/appointments/booked-slots/ | Get booked slots by doctor/date | Authenticated |
| GET, PATCH | /api/appointments/{id}/ | Appointment detail / status update | Authenticated (ownership/role constrained) |

## 9.5 Medical Records

From [backend/medical/urls.py](backend/medical/urls.py) and [backend/medical/views.py](backend/medical/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | /api/records/ | List accessible medical records | Authenticated |
| GET | /api/records/{id}/ | Medical record detail | Authenticated |
| POST | /api/records/create/ | Create medical record | Doctor |

## 9.6 Medications

From [backend/medications/urls.py](backend/medications/urls.py) and [backend/medications/views.py](backend/medications/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | /api/medications/ | List active medications | Patient |

Note:
- Reminder endpoints are implemented in views but not exposed in current URL config.

## 9.7 Documents

From [backend/documents/urls.py](backend/documents/urls.py) and [backend/documents/views.py](backend/documents/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET, POST | /api/documents/ | List documents / upload document | Authenticated (role checks) |
| GET, DELETE | /api/documents/{id}/ | Document detail / delete | Authenticated (ownership/role checks) |

## 9.8 Lab Tests

From [backend/lab_tests/urls.py](backend/lab_tests/urls.py) and [backend/lab_tests/views.py](backend/lab_tests/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET, POST | /api/lab-tests/ | List/order lab tests | Authenticated (role constrained) |
| GET, PATCH | /api/lab-tests/{id}/ | Lab test detail / status update | Authenticated (role constrained) |
| GET, POST | /api/lab-tests/{id}/result/ | View or create test result | Authenticated (role constrained) |
| PATCH | /api/lab-tests/{id}/result/update/ | Update existing test result | Authenticated (role constrained) |

## 9.9 Notifications

From [backend/notifications/urls.py](backend/notifications/urls.py) and [backend/notifications/views.py](backend/notifications/views.py):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | /api/notifications/ | List notifications | Authenticated |
| PATCH | /api/notifications/{id}/read/ | Mark one notification read | Authenticated |
| DELETE | /api/notifications/{id}/delete/ | Delete one notification | Authenticated |
| POST | /api/notifications/mark-all-read/ | Mark all notifications read | Authenticated |
| GET | /api/notifications/unread-count/ | Get unread notification count | Authenticated |
| DELETE | /api/notifications/clear/ | Clear all notifications | Authenticated |

---

## 10. Frontend Documentation Summary

Routing and role-segmented page architecture are defined in [frontend/src/App.jsx](frontend/src/App.jsx).

Route groups:

- Public: homepage, login, registration, policy pages
- Patient: dashboard, appointments, records, prescriptions, documents, lab results, medications, notifications, profile
- Doctor: dashboard, schedule, patients, patient detail, create record, notifications, profile
- Admin: dashboard, users, appointments, notifications
- Lab tech: orders, notifications, profile

---

## 11. Testing and Validation Status

Current status is primarily manual validation and integration checks.

Evidence in repository:

- Backend test placeholders exist in each app tests file under [backend](backend)
- Functionality validated through manual role-based flows and deployment checks

Improvement needed:

1. Unit tests for serializers and validators
2. API integration tests by role
3. Permission boundary tests
4. End-to-end smoke tests for key user journeys

---

## 12. Deployment Documentation (Render)

Current deployment model:

- Frontend on Render static service
- Backend on Render web service (Gunicorn)
- PostgreSQL on Render managed database

Operational details in repository:

- Root Render blueprint: [render.yaml](render.yaml)
- Backend env-based settings: [backend/curova_backend/settings.py](backend/curova_backend/settings.py)

Production essentials:

1. Correct environment variables (ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS, DATABASE_URL, secrets)
2. Migrations executed on deploy
3. Health endpoint monitoring at /health/

---

## 13. Known Limitations and Risks

1. Messaging feature is not exposed yet
- [backend/messaging/urls.py](backend/messaging/urls.py)

2. Medication reminder endpoint exposure gap
- View logic exists but URL routing incomplete in [backend/medications/urls.py](backend/medications/urls.py)

3. Automated test coverage is limited
- Tests are minimal and mostly placeholders across apps

4. Some advanced UX/ops hardening is pending
- Deeper observability, stricter automation, and richer admin analytics

---

## 14. Future Work Roadmap

Short term:

1. Expose reminder CRUD routes and complete reminder UI workflow
2. Complete messaging API and frontend feature
3. Add comprehensive backend automated tests
4. Improve audit and reporting capabilities in admin

Medium term:

1. Event-driven notification pipeline improvements
2. Enhanced observability (metrics, dashboards, alerts)
3. Scalability and performance profiling for high-load flows

Long term:

1. Deeper compliance hardening and audit trail extension
2. Mobile client integration over existing API surface

---

## 15. Appendix: Key Project References

Core design and planning references:

- Guideline source: [project_docs/capstone_project_guidelines.pdf](project_docs/capstone_project_guidelines.pdf)
- D1 requirements baseline: [project_docs/D1_requirement_doc.pdf](project_docs/D1_requirement_doc.pdf), [project_docs/d1.tex](project_docs/d1.tex)
- D2 design baseline: [project_docs/D2 Design Decisions (1).pdf](project_docs/D2%20Design%20Decisions%20(1).pdf), [project_docs/d2.tex](project_docs/d2.tex)
- Implementation plan and decisions: [project_docs/PLAN.md](project_docs/PLAN.md), [project_docs/FINAL_DECISIONS.md](project_docs/FINAL_DECISIONS.md)

Interview-oriented technical references created in this repository:

- Backend deep-dive viva guide: [BACKEND_INTERVIEW_GUIDE.md](BACKEND_INTERVIEW_GUIDE.md)
- Backend fundamentals guide: [BACKEND_FOUNDATIONS_GUIDE.md](BACKEND_FOUNDATIONS_GUIDE.md)
