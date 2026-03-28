# Curova — Quick Start Guide

## 🚀 Get Up and Running in 15 Minutes

Set up the full Curova healthcare app (Django + React) on your local machine.

---

## Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.12+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | any | `git --version` |

---

## Step 1 — Clone & Verify (2 min)

```bash
cd ~/workspace
git clone <repository-url>
cd WebProject_Curova
ls
# Expected: backend/  frontend/  venv/  project_docs/  README.md
```

---

## Step 2 — Database Setup (3 min)

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE curova_db;
CREATE USER curova_user WITH PASSWORD 'curova_pass_2026';
ALTER ROLE curova_user SET client_encoding TO 'utf8';
ALTER ROLE curova_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE curova_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
\q
```

✅ Verify: `psql -U curova_user -d curova_db -h 127.0.0.1` → you should see `curova_db=>`.

---

## Step 3 — Backend Setup (5 min)

The virtual environment lives at the **project root**, not inside `backend/`.

```bash
# From project root (WebProject_Curova/)
python -m venv venv          # Create venv (skip if venv/ already exists)
source venv/bin/activate     # Linux/Mac
# OR: venv\Scripts\activate  # Windows

cd backend
pip install -r requirements.txt   # Django 6.0.2, DRF 3.16, etc.
```

### Environment File

Make sure `backend/.env` exists with:

```
SECRET_KEY=django-insecure-curova-dev-key-change-in-production-2026
DEBUG=True
DB_NAME=curova_db
DB_USER=curova_user
DB_PASSWORD=curova_pass_2026
DB_HOST=127.0.0.1
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Migrate & Seed

```bash
python manage.py migrate
python manage.py seed_data        # Creates test users, appointments & records
python manage.py runserver        # http://127.0.0.1:8000/
```

✅ Checkpoint: "Starting development server at http://127.0.0.1:8000/"

**Keep this terminal open.**

---

## Step 4 — Frontend Setup (5 min)

Open a **new terminal**:

```bash
cd WebProject_Curova/frontend
npm install
npm run dev
```

✅ Checkpoint: `VITE v7.x.x ready` on http://localhost:5173/

**Keep this terminal open too.**

---

## Step 5 — Test the App (2 min)

Open http://localhost:5173/ — you should see the Curova homepage.

### Pre-seeded Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | testpatient@curova.com | testpass123 |
| Doctor | testdoctor@curova.com | testpass123 |
| Admin | admin@curova.com | adminpass123 |

- **Patient login** → redirects to `/patient/dashboard` (appointments, records, documents)
- **Doctor login** → redirects to `/doctor/dashboard` (schedule, patients, create records)
- **Admin login** → use Django admin at http://127.0.0.1:8000/admin/

### Or Register a New Patient

1. Click **Sign Up**
2. Fill in email / username / name / password
3. Click **Register** → redirects to patient dashboard

---

## 🎯 You're All Set!

- ✅ Backend: http://127.0.0.1:8000/
- ✅ Frontend: http://localhost:5173/
- ✅ Admin panel: http://127.0.0.1:8000/admin/
- ✅ Database connected and seeded

---

## Daily Commands Reference

### Start Servers

```bash
# Terminal 1 — Backend
cd WebProject_Curova
source venv/bin/activate
cd backend && python manage.py runserver

# Terminal 2 — Frontend
cd WebProject_Curova/frontend
npm run dev
```

### Database

```bash
psql -U curova_user -d curova_db -h 127.0.0.1
\dt              -- list tables
SELECT * FROM users_user LIMIT 5;
\q
```

### Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Git

```bash
git pull origin main
cd backend && pip install -r requirements.txt && python manage.py migrate
cd ../frontend && npm install
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `psycopg2.OperationalError` | `sudo systemctl start postgresql`, check `backend/.env` |
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Port 5173 in use | `lsof -i :5173` then `kill -9 <PID>` |
| Module not found (frontend) | `cd frontend && rm -rf node_modules && npm install` |
| CORS / network errors | Verify both servers running, check `CORS_ALLOWED_ORIGINS` in `.env` |
| DB connection failed | `sudo systemctl start postgresql`, verify credentials in `.env` |

---

## 📁 Project Structure

```
WebProject_Curova/
├── venv/                     # Python virtual environment (project root)
├── backend/
│   ├── manage.py
│   ├── requirements.txt      # pip install -r requirements.txt
│   ├── .env                  # DB credentials, CORS, etc.
│   ├── curova_backend/       # Django settings & root URL conf
│   ├── users/                # Auth, patient & doctor APIs
│   ├── appointments/         # Appointment CRUD
│   ├── medical/              # Medical records & prescriptions
│   ├── documents/            # Document uploads
│   └── medications/          # Medication tracking
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── public/       # Home, Login, Register
│   │   │   ├── patient/      # Patient dashboard & 5 sub-pages
│   │   │   └── doctor/       # Doctor dashboard & 4 sub-pages
│   │   ├── components/       # Layout, DashboardLayout, Navbar
│   │   ├── services/api.js   # Axios config (baseURL)
│   │   ├── contexts/         # AuthContext
│   │   └── styles/           # CSS files per feature
│   └── package.json
│
├── project_docs/             # PLAN.md, demo HTML mockups
├── README.md                 # Full documentation
├── DEVELOPMENT_LOG.md        # Phase-by-phase progress
└── QUICK_START.md            # ← You are here
```

---

## 👥 User Roles

| Role | How to Create | Dashboard Route |
|------|--------------|-----------------|
| Patient | Self-register via Sign Up | `/patient/dashboard` |
| Doctor | Admin creates via Django admin panel | `/doctor/dashboard` |
| Admin | `python manage.py createsuperuser` | Django admin panel |

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173/ |
| Backend API | http://127.0.0.1:8000/api/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |
| PostgreSQL | localhost:5432 |

---

## ✅ Pre-flight Checklist

- [ ] PostgreSQL running
- [ ] `(venv)` shown in terminal prompt
- [ ] Backend: "Starting development server…"
- [ ] Frontend: "VITE ready…"
- [ ] `backend/.env` exists with correct DB credentials
- [ ] No CORS errors in browser console

---

**Quick Start Version**: 2.0 — Updated for Phase 4 (Doctor Features)  
**Last Updated**: July 2025
