# Backend Foundations Guide (Zero to Curova)

This guide is for understanding backend development from first principles up to the architecture used in this project.

## 1. Backend Basics

Backend is the server-side part of an application. It handles:
- Data storage and retrieval
- Business logic and validation
- Authentication and authorization
- API responses for frontend and mobile clients
- Security, reliability, and performance

In Curova, backend responsibilities include user roles, appointments, medical records, prescriptions, lab workflow, document uploads, and notifications.

## 2. What Is Django?

Django is a Python web framework that provides:
- ORM (database layer)
- Auth system
- URL routing
- Middleware
- Admin panel
- Security-focused defaults

Why Django for this project:
- Strong relational modeling for healthcare workflows
- Fast development with proven patterns
- Good maintainability through app-based modular structure

## 3. Django vs DRF

Django (core):
- General web framework
- Good for server-rendered pages and business logic

DRF (Django REST Framework):
- API-first toolkit on top of Django
- Serializers for validation and response shaping
- API views and permissions
- Token auth, throttling, pagination helpers

Simple summary:
- Django gives the platform
- DRF gives API engineering tools

## 4. MVT Pattern (Django Architecture)

MVT means:
- Model: data schema and constraints
- View: request handling and flow control
- Template: HTML presentation (less relevant for API-first systems)

For API projects like Curova, practical flow is:
- Model + Serializer + View + URL

## 5. Components of a Django Project

1. Project package
- Global settings, root URLs, WSGI/ASGI

2. Apps
- Domain modules with their own models, views, serializers, URLs

3. Settings
- DB config, installed apps, middleware, auth, security

4. URL routing
- Maps endpoints to handlers

5. Migrations
- Versioned DB schema changes

6. Management commands
- CLI tasks like migration, seeding, maintenance

## 6. Request Lifecycle (API)

1. Client sends HTTP request
2. URL router selects endpoint view
3. Middleware runs (security, CORS, etc.)
4. DRF view parses payload/header
5. Serializer validates data
6. Business logic runs and DB is updated/read
7. Serializer builds response JSON
8. Response is returned with status code

## 7. Data Modeling Fundamentals

Important concepts:
- Primary key: unique row id
- Foreign key: relation to another table
- One-to-one: profile extension
- Constraints: integrity guards at DB level
- Indexes: query speed improvements

Why constraints matter:
- They protect data even if app logic has a bug.

Examples in this project:
- Unique doctor appointment slot
- Medication date consistency checks

## 8. Auth and Permissions

Authentication = who you are.
Authorization = what you can do.

In Curova:
- Token-based authentication
- Role-based access control (patient, doctor, admin, lab_tech)
- Resource ownership checks in endpoints

## 9. Serializer and Validation Strategy

Serializer responsibilities:
- Validate request data
- Transform model instances to JSON
- Enforce business rules before database writes

Validation layers:
1. Field-level (format/type)
2. Cross-field (date/time and rule combinations)
3. Database constraints (final integrity guard)

## 10. API Design Basics

HTTP verbs:
- GET: fetch
- POST: create
- PUT/PATCH: update
- DELETE: remove/deactivate

Key status codes:
- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 500 Server Error

API consistency principles:
- Predictable URLs
- Stable response formats
- Useful validation errors

## 11. Pagination, Filtering, Throttling

Pagination:
- Prevents huge responses
- Improves performance and UX

Filtering:
- Role- and status-specific views
- Reduces payload and client computation

Throttling:
- Limits abuse and accidental spikes
- Protects service stability

## 12. Security Foundations

CORS:
- Controls which frontend origins can call backend from browsers

CSRF:
- Protects session/cookie-based flows and origin trust boundaries

Security baseline checklist:
- Secrets via environment variables
- DEBUG off in production
- Strict allowed hosts/origins
- Upload validation (type and size)
- Endpoint-level permission checks
- Logging and monitoring

## 13. File Upload Fundamentals

Important concerns:
- Allowed file extension/type
- Max file size
- Storage path organization
- Access control for retrieval

In this project, document upload is patient-scoped and role-guarded.

## 14. Curova Backend Domain Breakdown

users:
- Custom user model, roles, auth/profile APIs

appointments:
- Booking and doctor slot logic

medical:
- Medical records and immutable prescriptions

medications:
- Active medication tracking and reminders

lab_tests:
- Order/result lifecycle with priority and interpretation

documents:
- Medical document upload and retrieval

notifications:
- Unified in-app event notifications

messaging:
- Model scaffold present for future chat expansion

## 15. Why Some Choices Were Deferred

MVP-first tradeoffs are normal:
- Simpler token auth before JWT complexity
- Polling reminders before task queue infrastructure
- Modular monolith before microservices

Interview framing:
- "Intentionally sequenced by value, risk, and delivery speed."

## 16. Database Operations Every Backend Engineer Should Know

Core operations:
- makemigrations / migrate
- Atomic transactions for multi-step writes
- Query optimization with select_related/prefetch_related
- Index tuning based on real query patterns
- Seed data commands for reproducible environments

## 17. Testing Fundamentals

Testing layers:
1. Unit tests (serializers/utils)
2. Integration tests (API + DB)
3. Permission tests (role and ownership)
4. Regression tests (prevent bug reintroduction)

## 18. Deployment Fundamentals

Backend deployment essentials:
- App server (Gunicorn)
- Managed Postgres
- Environment variable configuration
- Health endpoint
- Migration strategy
- Logging and alerting

## 19. Observability and Reliability

Track:
- Error rate
- Request latency
- Throughput
- Database query performance
- Availability

Use:
- Structured logs
- Basic dashboards and alerts

## 20. Healthcare-Sensitive Engineering Mindset

For healthcare-like systems, prioritize:
- Data integrity
- Access control rigor
- Auditability
- Privacy-aware retention/deletion behavior

These concerns directly shape schema, permissions, and API decisions.

## 21. Learning Path (Ground Zero to Project Build)

Stage 1: Python + HTTP + JSON

Stage 2: Django fundamentals
- apps, models, views, urls, migrations

Stage 3: DRF API engineering
- serializers, auth, permissions, throttling, pagination

Stage 4: Relational database and performance
- constraints, indexing, query optimization

Stage 5: Security and deployment
- CORS/CSRF/env config and production hardening

Stage 6: Domain architecture
- role workflows and lifecycle states

Stage 7: Production maturity
- observability, testing depth, scaling roadmap

## 22. Viva/Interview Quick Checklist

You should be ready to explain clearly:
- What Django provides
- Why DRF is needed for APIs
- What MVT means in API context
- Where validation lives and why
- How auth differs from authorization
- Why relational modeling fits this project
- Why constraints/indexes are used
- Which tradeoffs were intentional and what comes next

## 23. Final Preparation Advice

When answering tough questions, use this structure:
1. Problem
2. Current implementation
3. Why this decision
4. Tradeoff
5. Improvement roadmap

That structure makes answers sound both practical and senior.

