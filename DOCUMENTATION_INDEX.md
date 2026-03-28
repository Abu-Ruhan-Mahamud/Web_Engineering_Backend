# CUROVA Backend Engineering — Complete Documentation Index

**Created:** March 28, 2026  
**Purpose:** Comprehensive backend documentation for Capstone Viva Presentation

---

## Quick Start: What to Read First

### For Tomorrow's Viva Presentation:

**1. START HERE:** `BACKEND_DESIGN_DECISIONS.md`
- Teaches you the "WHY" behind every decision
- Answering "why did you design it this way?" questions
- Covers Django vs. alternatives, PostgreSQL vs. SQLite, token auth rationale
- **Read time:** 45 minutes

**2. UNDERSTAND THE CODE:** `BACKEND_ENGINEERING_GUIDE.md`
- Complete technical guide from architecture to deployment
- Database schema with diagrams
- Every API endpoint documented
- Authentication flow step-by-step  
- **Read time:** 1.5 hours

**3. SEE IT IN ACTION:** `BACKEND_CODE_WALKTHROUGHS.md`
- Real code examples you can copy/explain
- "How to add a new endpoint" walkthrough
- Common debugging patterns
- Interview preparation examples
- **Read time:** 45 minutes

**4. PROFESSIONAL REFERENCE:** `BACKEND_ENGINEERING_GUIDE.tex`
- LaTeX typeset version for printing
- Compile to PDF with: `pdflatex BACKEND_ENGINEERING_GUIDE.tex`
- Professional format for handout distribution
- Same content as markdown but publication-ready

---

## Document Descriptions

### 1. BACKEND_ENGINEERING_GUIDE.md
**Most Comprehensive - 3000+ lines**

#### Chapters:
- Project Overview (what problem does CUROVA solve?)
- Architecture & Philosophy (design principles)
- Tech Stack Breakdown (why Django, PostgreSQL, Gunicorn)
- Database Schema (complete ER diagram in text)
- Authentication System (token flow explained)
- Core Backend Applications (all 8 apps documented)
- API Endpoints Reference (every endpoint listed)
- Key Design Patterns (serializers, permissions, pagination)
- Common Operations Walkthrough (patient books appointment, doctor creates record)
- Deployment Architecture (Render + Vercel)
- Testing & Debugging (common errors and solutions)
- Frontend Integration (how frontend calls backend)

#### Use When:
- You need complete technical understanding
- Someone asks about how endpoints work
- You need to explain database relationships
- Wondering how authentication works end-to-end

#### Sample Sections:
- Complete database schema with all relationships
- Authentication flow with JWT/token examples
- 30+ API endpoints with request/response examples
- Deployment pipeline explanation

---

### 2. BACKEND_CODE_WALKTHROUGHS.md
**Implementation-Focused - 2000+ lines**

#### Chapters:
- Adding a New API Endpoint (step-by-step)
- Creating Notifications When Events Happen (with examples)
- Adding Permission Restrictions (role-based)
- Database Query Patterns (smart select_related, pagination, etc)
- Serializer Validation Examples (field validation, cross-field)
- Common Code Locations (where to find what)
- How to Debug (500 errors, 403 forbidden, CORS issues)
- Extending Models (adding fields, relationships)
- Interview Prep Questions (with answer patterns)

#### Use When:
- Asked to explain/rewrite a service
- Need to add new feature quickly
- Debugging production issues
- Preparing code examples for viva
- Following request-response flow

#### Sample Sections:
- Adding prescription refill endpoint (complete code)
- Notification helper usage in 5 real scenarios
- Permission classes with object-level checks
- Serializer validation with 4-level checks
- Django shell commands for debugging

---

### 3. BACKEND_DESIGN_DECISIONS.md
**Philosophy & Rationale - 2000+ lines**

#### Chapters:
- Why Django + REST Framework?
- Why Token-Based Authentication?
- Why Role-Based Access Control?
- Why PostgreSQL?
- Why Separate User/Patient/Doctor Models?
- Why Immutable Prescriptions?
- Why Notifications App?
- Why Pagination?
- Why Unique Constraint on Appointments?
- Comparison: Our Choices vs. Alternatives
- How to Answer "Why" Questions in Viva

#### Use When:
- Someone asks "Why did you choose X over Y?"
- Defending architectural decisions
- Explaining design rationale
- Understanding trade-offs
- Comparing with alternatives

#### Sample Sections:
- Django vs Flask vs FastAPI vs Spring (detailed comparison)
- Sessions vs Token authentication (table comparing)
- ACID compliance explanation with healthcare example
- Race condition prevention with appointment booking
- Legal/regulatory rationale for immutable prescriptions

---

### 4. BACKEND_ENGINEERING_GUIDE.tex
**Professional PDF Version**

#### Format:
- LaTeX typeset (publishable quality)
- 11pt font, professional margins
- Full table of contents and index
- Syntax-highlighted code blocks
- Professional header/footer with page numbers
- Hyperlinked cross-references

#### How to Compile:
```bash
cd /home/t14/CODEBASE/WebProject_Curova
pdflatex BACKEND_ENGINEERING_GUIDE.tex
# Creates: BACKEND_ENGINEERING_GUIDE.pdf
```

#### Use When:
- Need to print handout for viva
- Want professional document for portfolio
- Presenting to client/stakeholders
- Formal documentation requirement

---

## Knowledge Map: What You Should Be Able to Explain

### Foundation (Must Know)
- [ ] What is Django and why we chose it
- [ ] How token authentication works (login → token → request)
- [ ] What is 4-role RBAC (patient/doctor/admin/lab_tech)
- [ ] Database schema: User → Patient/Doctor 1:1 relationships
- [ ] Why PostgreSQL ACID compliance matters for healthcare

### Architecture (Should Know)
- [ ] RESTful API design principles
- [ ] How serializers validate input and convert objects
- [ ] Who is allowed to access what (permission classes)
- [ ] How unique constraints prevent double-booking at DB level
- [ ] Why prescriptions are immutable

### Implementation (Nice to Know)
- [ ] How to add new endpoint (view → serializer → url → migration)
- [ ] How notifications are created and triggered
- [ ] Common query patterns (select\_related, pagination, filtering)
- [ ] Debugging 401/403/404/500 errors
- [ ] How frontend integrates with backend

### Demonstration (Be Ready)
- [ ] Rewrite an endpoint if asked
- [ ] Explain code flow from frontend request to database
- [ ] Add a new field to model and migrate
- [ ] Fix a bug (common scenarios)
- [ ] Design a new feature

---

## Preparation Timeline

### If you have 3 hours:
1. Read BACKEND_DESIGN_DECISIONS.md (45 min) - Learn the rationale
2. Read BACKEND_ENGINEERING_GUIDE.md key chapters (90 min) - Understand architecture
3. Review CODE_WALKTHROUGHS.md examples (45 min) - See real code

### If you have 2 hours:
1. Read BACKEND_DESIGN_DECISIONS.md chapters 1-5 (30 min)
2. Skim BACKEND_ENGINEERING_GUIDE.md chapters 1-3, 5-6 (60 min)
3. Read CODE_WALKTHROUGHS.md sections 1-3 (30 min)

### If you have 1 hour:
1. Read "Why" answers in BACKEND_DESIGN_DECISIONS.md (30 min)
2. Skim API endpoints in BACKEND_ENGINEERING_GUIDE.md (15 min)
3. Review common viva questions in CODE_WALKTHROUGHS.md (15 min)

---

## Interview Question Categories & How to Answer

### Category 1: Architecture & Design

**Q: "Why did you design it this way?"**
→ Read: BACKEND_DESIGN_DECISIONS.md corresponding chapter
→ Structure: Choice → Problem → Alternative → Why Ours

**Q: "What's the difference between your system and alternatives?"**
→ Read: BACKEND_DESIGN_DECISIONS.md "Comparison" tables
→ Structure: Feature → Our approach → Alternative approach → Trade-off

**Q: "How would you scale this system?"**
→ Read: BACKEND_ENGINEERING_GUIDE.md "Deployment Architecture"
→ Answer: Horizontal scaling with stateless tokens + horizontal DB replication

### Category 2: Implementation & Code

**Q: "Can you explain this code?"**
→ Read: BACKEND_CODE_WALKTHROUGHS.md code examples
→ Structure: What it does → How it works → Why this approach

**Q: "How would you add [feature]?"**
→ Read: BACKEND_CODE_WALKTHROUGHS.md "Adding New Endpoint" section
→ Structure: Step-by-step implementation example

**Q: "What's a bug and how would you fix it?"**
→ Read: BACKEND_CODE_WALKTHROUGHS.md "How to Debug" section  
→ Answer: Specific debugging approach, check logs, use shell

### Category 3: Security & Reliability

**Q: "How do you prevent [SQL injection / double-booking / unauthorized access]?"**
→ Read: BACKEND_ENGINEERING_GUIDE.md corresponding section
→ Structure: Threat → Multiple layers of defense → Example

**Q: "What if the database crashes?"**
→ Read: BACKEND_ENGINEERING_GUIDE.md "Database: PostgreSQL"
→ Answer: ACID guarantees, point-in-time recovery, replication

---

## Key Facts to Memorize

### Architecture
- **Framework:** Django 6.0.2 + Django REST Framework 3.14.0
- **Database:** PostgreSQL (Render-managed)
- **Auth:** Token-based (DRF TokenAuthentication)
- **Roles:** 4 (patient, doctor, admin, lab_tech)
- **Endpoints:** 30+ REST endpoints across 8 Django apps
- **Migrations:** 40+ for complete schema

### Deployment
- **Backend:** https://curova-backend.onrender.com (Render)
- **Frontend:** https://curovafrontend.vercel.app (Vercel)
- **Test User:** testpatient@curova.com / testpass123
- **Database:** PostgreSQL on Render

### Key Models
- **User** (base auth)
  - Patient (1:1)
  - Doctor (1:1)
- **Appointment** (booking)
  - Unique constraint: (doctor, date, time)
- **MedicalRecord** (doctor notes)
  - **Prescription** (immutable audit trail)
- **Notification** (event alerts)

### HTTP Status Codes Used
- 200 OK
- 201 CREATED
- 400 BAD REQUEST
- 401 UNAUTHORIZED
- 403 FORBIDDEN
- 404 NOT FOUND
- 500 INTERNAL SERVER ERROR

---

## Failure Mode: What If They Ask X?

### "Can you rewrite the appointment booking logic?"
- Location: `/backend/appointments/views.py`
- Related: serializers.py for validation
- Refer to: CODE_WALKTHROUGHS.md "Operation 1" section
- Say: "Validation happens in serializer, then view creates record"

### "Why did you choose PostgreSQL instead of MySQL?"
- You actually need to compare them
- Refer to: DESIGN_DECISIONS.md "Why PostgreSQL?" 
- Key points: ACID (both have it), JSON (PostgreSQL superior), production features
- Say: "Both work, but PostgreSQL has better JSON and replication"

### "What's your security model?"
- Refer to: ENGINEERING_GUIDE.md "Authentication System"
- Layers: Token validation → Permission class → Object-level check
- Say: "Multiple layers: ORM prevents SQL injection, tokens prevent unauthorized access, permissions control roles"

### "How would you add Google OAuth?"
- It's already there and needs configuration
- Refer to: ENGINEERING_GUIDE.md "Google OAuth" section
- Say: "Frontend sends Google credential token to /api/auth/google-login/, we verify with Google servers, issue our own token"

### "What happens if two patients book the same slot simultaneously?"
- This is the race condition question
- Refer to: DESIGN_DECISIONS.md "Unique Constraint" section
- Say: "Database UNIQUE constraint is insurmountable - first wins, second gets error"

---

## Quick Reference: File Locations

| What | Where |
|------|-------|
| Models definition | `/backend/{app}/models.py` |
| REST endpoints | `/backend/{app}/views.py` |
| Input validation | `/backend/{app}/serializers.py` |
| Role checks | `/backend/users/permissions.py` |
| Database config | `/backend/curova_backend/settings.py` |
| URL routing | `/backend/{app}/urls.py` and `/backend/curova_backend/urls.py` |
| Auto-migrations | `/backend/curova_backend/wsgi.py` (lines 12-24) |
| Environment vars | Render dashboard (not in code) |

---

## Final Checklist Before Viva

- [ ] Read two of three main documents
- [ ] Understand appointment booking flow (database → API → frontend)
- [ ] Can explain why Django chosen over alternatives
- [ ] Know what token authentication is and why stateless matters
- [ ] Can list the 4 roles and their permissions
- [ ] Understand unique constraint prevents double-booking
- [ ] Know prescriptions are immutable and why
- [ ] Can explain common HTTP status codes
- [ ] Can walk through how to debug 500 error
- [ ] Can say something intelligent about each of 8 apps

---

## Emergency Prep (Last 30 Minutes)

If you only have 30 minutes left:

1. **Read these sections (20 min):**
   - BACKEND_DESIGN_DECISIONS.md: "Why Token Auth" & "Why PostgreSQL"
   - BACKEND_ENGINEERING_GUIDE.md: "Authentication System" only
   
2. **Memorize these facts (5 min):**
   - Django 6.0.2 + DRF
   - Token auth (stateless, perfect for SPA)
   - 4 roles, 8 apps
   - Render backend + Vercel frontend
   
3. **Practice saying (5 min):**
   - Appointment booking explanation
   - Why PostgreSQL over SQLite
   - How token authentication works

---

## Additional Resources (Not Created Yet)

The following documentation already exists in the project:

- `/project_docs/FINAL_DECISIONS.md` - Original design decisions
- `/project_docs/PLAN.md` - Project planning
- `/project_docs/STATUS.md` - Current status
- `/backend/requirements.txt` - All Python dependencies

---

## How to Compile LaTeX to PDF

```bash
# Navigate to project root
cd /home/t14/CODEBASE/WebProject_Curova

# Compile LaTeX to PDF
pdflatex BACKEND_ENGINEERING_GUIDE.tex

# Fix any cross-references (run twice recommended)
pdflatex BACKEND_ENGINEERING_GUIDE.tex

# Result: BACKEND_ENGINEERING_GUIDE.pdf (ready to print/share)
```

---

## Document Statistics

| Document | Format | Lines | Time to Read | Best For |
|----------|--------|-------|--------------|----------|
| BACKEND_ENGINEERING_GUIDE.md | Markdown | 3500+ | 1.5 hours | Complete understanding |
| BACKEND_CODE_WALKTHROUGHS.md | Markdown | 2500+ | 45 min | Implementation details |
| BACKEND_DESIGN_DECISIONS.md | Markdown | 2200+ | 45 min | Why decisions |
| BACKEND_ENGINEERING_GUIDE.tex | LaTeX | 1200+ | 1.5 hours | Professional PDF |

---

## Success Criteria for Tomorrow's Viva

You've prepared successfully if you can:

✓ Explain why Django chosen without hesitation  
✓ Walk through appointment booking step-by-step  
✓ Defend token authentication over sessions  
✓ Show database schema from memory  
✓ Live-code a simple endpoint  
✓ Debug a fake 403 error  
✓ Answer "architect this feature" question  
✓ Discuss PostgreSQL ACID guarantees confidently  
✓ Explain prescriptions immutability rationale  
✓ Tell them about deployment on Render + Vercel  

Good luck! You've got complete documentation now. Read strategically based on your strongest weak area.

---

**Document Status:** ✅ Complete  
**Last Updated:** March 28, 2026, 17:00 UTC  
**Ready for:** Capstone Viva Presentation Tomorrow
