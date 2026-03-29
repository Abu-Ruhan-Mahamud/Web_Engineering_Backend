# Curova Backend Interview Guide (Viva + Hardcore Q&A)

This guide is designed for oral defense, viva, and backend interviews.
It is based on your current codebase architecture and implementation patterns.

---

## 1. How to Present the Project in 30 Seconds

Curova is a healthcare backend built with Django and Django REST Framework, using PostgreSQL and token-based authentication. It supports multi-role users (patient, doctor, admin, lab technician), appointment scheduling with slot validation, medical records and prescriptions, lab test workflows, document uploads, medications with reminders, and an in-app notifications system. The architecture is modular by domain apps and role-aware at API level.

---

## 2. How to Present in 2 Minutes (Architecture Pitch)

1. Framework and stack:
- Django + DRF for API layer
- PostgreSQL for relational integrity
- DRF token auth for session/token simplicity

2. Domain modularization:
- users: identity, auth, role profiles
- appointments: booking + scheduling rules
- medical: records + immutable prescriptions
- medications: mutable active meds + reminders
- lab_tests: order-to-result workflow
- documents: secure file upload and retrieval
- notifications: unified event inbox
- messaging: model stub for future real-time feature

3. Key design choices:
- Custom User model with role field for role-based logic
- Patient/Doctor as one-to-one profile extensions
- Serializer-centric business validation (time slots, availability, upload constraints)
- Notifications generated from domain events
- DRF throttling + CORS configured globally

4. Why this architecture:
- Clear separation of healthcare domains
- Easier maintenance and feature ownership
- Role and data integrity enforced at multiple layers

---

## 3. Core Design Decisions and Why

### Decision A: Custom User + one-to-one role profiles

Why chosen:
- Keeps authentication fields centralized in one user table
- Keeps role-specific fields out of a bloated single user schema
- Makes patient and doctor entities explicit for foreign keys in medical workflows

Why not a single giant user table:
- Too many nullable fields
- Harder to maintain and validate
- Weak domain boundaries

Why not multiple independent auth tables:
- Harder login and permission management
- Complicated token lifecycle

### Decision B: Token auth (DRF token) instead of JWT

Why chosen:
- Simpler setup and debugging for early-stage product
- Easy server-side invalidation by deleting token
- Good fit for controlled internal API usage

Why not JWT initially:
- JWT adds refresh/access complexity
- Harder immediate revocation without blacklist patterns

### Decision C: Separate Prescription from Medication

Why chosen:
- Prescription is immutable medical/legal history from a visit
- Medication is mutable current-state tracking for ongoing care
- Supports auditability and practical medication management

Why not one combined model:
- Loses distinction between historical decision and current treatment
- Complicates legal/audit explanations

### Decision D: Function-based views instead of full ViewSets

Why chosen:
- Explicit role checks and branch logic are easy to read in healthcare workflows
- Faster for custom endpoint behavior

Why not ViewSets everywhere:
- More abstraction; less explicit in complex permission branching
- Team preferred direct control over request methods

### Decision E: PostgreSQL with relational constraints

Why chosen:
- Strong data integrity for healthcare entities
- Foreign keys and constraints prevent invalid graph states
- Supports transactional consistency for critical writes

Why not NoSQL:
- Relationship-heavy medical domain maps naturally to relational model
- Referential integrity is crucial

---

## 4. File-by-File Interview Walkthrough (What to say and why)

## 4.1 Settings and global behavior

Primary file:
- backend/curova_backend/settings.py

Explain these blocks:
1. SECRET_KEY, DEBUG, ALLOWED_HOSTS from env:
- Keeps environment-specific behavior outside code
- Required for secure deployment

2. INSTALLED_APPS:
- Domain apps are explicit; third-party apps are minimal and intentional

3. MIDDLEWARE order:
- Security and CORS are positioned early for request handling correctness

4. REST_FRAMEWORK defaults:
- Global IsAuthenticated gives secure-by-default posture
- Throttling prevents abuse
- Pagination improves API performance and payload control

5. DATABASE_URL fallback:
- Production can use single URL
- Local dev can use DB_* variables

6. Static/media config:
- Separates static assets and user uploads

7. CORS and CSRF controls:
- Required for frontend-backend cross-origin flow in deployment

## 4.2 Authentication and role APIs

Primary files:
- backend/users/models.py
- backend/users/serializers.py
- backend/users/views.py
- backend/users/permissions.py

Explain flow:
1. Registration creates role-aware user (default patient)
2. Login validates credentials and returns token
3. Google login path supports social auth onboarding
4. Permission classes enforce role-level endpoint protection

Key talking point:
- Role checks are not only UI-level; backend enforces access boundaries.

## 4.3 Appointment engine

Primary files:
- backend/appointments/models.py
- backend/appointments/serializers.py
- backend/appointments/views.py

Explain high-value logic:
1. Unique doctor/date/time constraint prevents slot collision
2. Serializer validation enforces:
- no past date
- day availability
- working hour boundaries
- slot-duration alignment
3. View filters data by role to prevent unauthorized read access

Why this matters:
- Interviewers often test if you understand where business rules belong.
- Your answer: structural constraints in model, temporal/business rules in serializer, ownership checks in view.

## 4.4 Medical records and prescriptions

Primary files:
- backend/medical/models.py
- backend/medical/serializers.py
- backend/medical/views.py

Explain:
1. MedicalRecord links patient, doctor, and optional appointment
2. Prescription linked to medical record for immutable treatment snapshot
3. Nested serializer support for writing records plus multiple prescriptions

Key design defense:
- Historical treatment decision and current medication adherence are intentionally decoupled.

## 4.5 Medications and reminders

Primary files:
- backend/medications/models.py
- backend/medications/views.py
- backend/medications/reminders.py

Explain:
1. Medication supports active/inactive lifecycle with date constraints
2. Reminder model supports multiple reminder times per medication
3. Reminder generation uses deterministic mapping by frequency and duplicate guards

Tradeoff explanation:
- Current reminder generation approach avoids infra overhead; future can move to scheduled workers.

## 4.6 Lab tests workflow

Primary files:
- backend/lab_tests/models.py
- backend/lab_tests/serializers.py
- backend/lab_tests/views.py

Explain:
1. Order pipeline statuses support lab operations lifecycle
2. Separate LabTestResult model supports both structured and narrative results
3. Reviewer fields represent doctor review stage explicitly

Interview insight:
- This is a multi-actor workflow model (doctor, lab tech, patient visibility).

## 4.7 Documents and uploads

Primary files:
- backend/documents/models.py
- backend/documents/serializers.py
- backend/documents/views.py

Explain:
1. Allowed file types and max-size validation protect backend
2. Patient-scoped upload path supports organization and access control
3. View-level checks prevent unauthorized cross-patient access

## 4.8 Notifications

Primary files:
- backend/notifications/models.py
- backend/notifications/helpers.py
- backend/notifications/views.py

Explain:
1. Unified model receives events from multiple domain apps
2. Unread count endpoint supports UI badge polling pattern
3. Notification linking supports related object tracing

---

## 5. What Not Implementing Something Means (Important interview angle)

When asked "Why did you not do X?", use this structure:

1. Say what you chose now.
2. Say why it was right for current stage.
3. Say what you would do at scale.

Examples:

1. Why no Celery yet?
- Current approach reduces operational complexity and cost.
- For scale, move reminders and periodic jobs to Celery + Redis.

2. Why no WebSockets yet?
- Polling is sufficient for MVP notifications.
- For real-time chat/reminders, adopt Django Channels.

3. Why no JWT yet?
- DRF token is easier operationally and enough for current risk profile.
- For mobile multi-device and expiring sessions, migrate to JWT with refresh rotation.

4. Why no microservices?
- Monolith with modular apps keeps velocity high and boundaries clear.
- If scale and team size grow, split high-load domains first (notifications/lab processing).

---

## 6. Hardcore Interview Questions and Strong Answers

## Q1. Where do you enforce double-booking prevention?
A:
- DB constraint on doctor/date/time (hard guarantee)
- Serializer validation before write (friendly error)
- Combined approach gives UX + integrity

## Q2. How do you prevent patient A from reading patient B data?
A:
- Role-aware permission classes
- View queryset filtering by request.user profile
- Ownership checks on retrieval endpoints

## Q3. Why use JSONField for allergies/conditions?
A:
- Flexibility for variable-length and evolving health metadata
- Faster iteration than introducing many join tables early
- If analytics-heavy queries needed, normalize into lookup/join tables later

## Q4. What is your consistency strategy for medical writes?
A:
- Use relational FK constraints and DRF serializer validation
- For multi-write critical operations, use atomic transaction blocks

## Q5. How do you handle soft deletion/legal retention?
A:
- Account deletion anonymizes personal identity but keeps medical history for compliance/audit

## Q6. How is API abuse mitigated?
A:
- Global DRF throttling for anonymous and authenticated users
- Can add endpoint-specific throttles if traffic profile changes

## Q7. What are your known technical debts?
A:
- Messaging app API not complete yet
- Could improve query optimization with broader select_related/prefetch_related
- Reminder infra can move to scheduled background workers

## Q8. If I ask you to production-harden this in one sprint, what would you do?
A:
1. Add structured logging + error monitoring
2. Add Celery for scheduled notifications/reminders
3. Add endpoint-level throttles + stricter upload scanning
4. Add integration tests for booking and role access control
5. Add DB indexes from observed slow queries

## Q9. Why model-first then serializer validations?
A:
- Models enforce non-negotiable invariants
- Serializers enforce request-context business rules
- Views enforce authorization and endpoint semantics

## Q10. How do you explain your architecture maturity level?
A:
- Production-capable MVP with strong domain modeling and clear expansion points
- Not enterprise-complete yet, but intentionally structured for iterative hardening

---

## 7. Viva Drill Script (Memorize this format)

Use this 5-step response method for any question:

1. Problem statement:
- "In healthcare, incorrect access and invalid scheduling are high-risk."

2. Current implementation:
- "I enforce this through model constraints, serializer rules, and role-aware view filtering."

3. Why this choice:
- "This balances correctness, clarity, and developer velocity."

4. Tradeoff:
- "It increases code verbosity and still needs infra upgrades for real-time workflows."

5. Future improvement:
- "Next step is Celery/Channels, stronger indexing, and test-depth increase."

---

## 8. Quick Credential and Demo Story for Interview

If interviewer asks for demonstration users (seeded):

- Admin: admin@curova.com / Admin@123
- Doctor: doctor@curova.com / Doctor@123
- Patient: patient@curova.com / Patient@123
- Lab tech: labtech@curova.com / LabTech@123

Demo narrative order:
1. Doctor login and schedule visibility
2. Patient books appointment
3. Doctor creates medical record + prescription
4. Lab test ordered and result uploaded
5. Notifications and reminders shown in patient dashboard

---

## 9. Advanced Topics You Can Mention Proactively

1. Event-driven transition path:
- Domain events can decouple notifications from business endpoints.

2. Audit trail depth:
- Add historical tables for updates/deletes in clinical models.

3. Security hardening:
- Field-level encryption for sensitive PII in database.

4. Interoperability:
- Future FHIR mapping layer for healthcare data exchange.

5. Observability:
- Add metrics for request latency, booking conflicts, and reminder dispatch success.

---

## 10. Final Prep Checklist Before Interview

1. Re-read these key files once:
- backend/curova_backend/settings.py
- backend/users/models.py
- backend/users/views.py
- backend/appointments/serializers.py
- backend/medical/models.py
- backend/lab_tests/models.py
- backend/documents/serializers.py
- backend/notifications/helpers.py

2. Practice 3 versions of explanation:
- 30 seconds
- 2 minutes
- 5 minutes

3. Prepare 3 weaknesses and 3 upgrade plans.

4. Be explicit about tradeoffs and roadmap. Interviewers prefer pragmatic honesty over fake perfection.

---

If you want, next I can generate a second file with:
- 50 probable viva questions
- model answers in first-person speaking style
- rapid-fire one-line responses for panel interviews
