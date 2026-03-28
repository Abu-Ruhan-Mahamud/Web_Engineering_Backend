# Curova — Windows Setup Guide

> Complete instructions to set up the Curova Healthcare Management System on a **Windows** machine.

---

## Prerequisites

Install these before starting:

| Tool | Version | Download |
|------|---------|----------|
| **Python** | 3.12+ | https://www.python.org/downloads/ (check "Add to PATH") |
| **Node.js** | 20+ (LTS) | https://nodejs.org/ |
| **PostgreSQL** | 16+ | https://www.postgresql.org/download/windows/ |
| **Git** | latest | https://git-scm.com/download/win |
| **VS Code** | latest | https://code.visualstudio.com/ |

> ⚠️ During Python install, **check "Add Python to PATH"**.  
> ⚠️ During PostgreSQL install, **remember the password** you set for the `postgres` superuser.

---

## Step 1: Database Setup

Open **pgAdmin** (installed with PostgreSQL) or a terminal and run:

```sql
-- Connect as the postgres superuser first, then run:
CREATE DATABASE curova_db;
CREATE USER curova_user WITH PASSWORD 'your-chosen-password';
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
ALTER DATABASE curova_db OWNER TO curova_user;
```

**Or via command line** (open Command Prompt):
```cmd
psql -U postgres
```
Then paste the SQL above (replace `your-chosen-password` with your actual password).

---

## Step 2: Extract the Project

1. Unzip `Curova_Project.zip` to a folder, e.g. `C:\Projects\WebProject_Curova\`
2. Open this folder in VS Code: **File → Open Folder**

---

## Step 3: Backend Setup

Open a terminal in VS Code (`Ctrl+`` `) and run:

```cmd
cd backend

:: Create virtual environment
python -m venv venv

:: Activate it
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt
```

### Configure Environment Variables

Copy the example env file:
```cmd
copy ..\.env.example .env
```

Edit `backend\.env` and fill in your values:
```dotenv
SECRET_KEY=any-random-string-at-least-50-chars-long
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=curova_db
DB_USER=curova_user
DB_PASSWORD=your-chosen-password
DB_HOST=127.0.0.1
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Run Migrations & Seed Data

```cmd
python manage.py migrate
python manage.py seed_data
```

The `seed_data` command creates demo users:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@curova.com | Admin@123 |
| Doctor | doctor@curova.com | Doctor@123 |
| Patient | patient@curova.com | Patient@123 |
| Patient 2 | patient2@curova.com | Patient@123 |
| Lab Tech | labtech@curova.com | LabTech@123 |

### Start Backend Server

```cmd
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

---

## Step 4: Frontend Setup

Open a **second terminal** in VS Code and run:

```cmd
cd frontend

:: Install dependencies
npm install

:: Start dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Step 5: Verify

1. Open **http://localhost:5173** in your browser
2. Log in with `patient@curova.com` / `Patient@123`
3. You should see the patient dashboard with sample appointments

---

## Project Structure

```
WebProject_Curova/
├── backend/               Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env               Your local config (create from .env.example)
│   ├── curova_backend/    Django project settings
│   ├── users/             Auth, profiles (Patient, Doctor, Admin, Lab Tech)
│   ├── appointments/      Booking & scheduling
│   ├── medical/           Medical records
│   ├── medications/       Prescriptions & reminders
│   ├── lab_tests/         Lab orders & results
│   ├── documents/         Document uploads
│   ├── messaging/         In-app messaging
│   └── notifications/     Notification system
├── frontend/              React + Vite SPA
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── pages/         Route pages (patient/, doctor/, lab/, admin/)
│       ├── components/    Shared components (Navbar, Sidebar, etc.)
│       ├── services/      API client (axios)
│       ├── contexts/      React contexts (Auth)
│       ├── hooks/         Custom hooks
│       ├── utils/         Utilities (lab templates, icons)
│       └── styles/        CSS files
├── project_docs/          Design docs & HTML mockups
└── .env.example           Environment variable template
```

---

## Tech Stack

- **Backend:** Django 6.0 + Django REST Framework 3.16, PostgreSQL, Token Auth
- **Frontend:** React 19 + Vite 7, React Router 7, Axios
- **Auth:** Token-based (DRF TokenAuthentication)
- **User Types:** patient, doctor, admin, lab_tech (custom User model)

---

## Common Issues

### "psycopg2" install fails on Windows
Install the binary version (already in requirements.txt):
```cmd
pip install psycopg2-binary
```

### Port 5173 already in use
```cmd
npx vite --port 5174
```
Then update `CORS_ALLOWED_ORIGINS` in `backend/.env` to include the new port.

### "No module named 'decouple'"
Make sure you activated the virtual environment:
```cmd
backend\venv\Scripts\activate
```

### Database connection refused
- Ensure PostgreSQL service is running (check Windows Services)
- Verify credentials in `backend/.env` match what you set in Step 1

---

## Running Both Servers

You need **two terminals** running simultaneously:

| Terminal | Command | URL |
|----------|---------|-----|
| Terminal 1 | `cd backend && venv\Scripts\activate && python manage.py runserver` | http://127.0.0.1:8000 |
| Terminal 2 | `cd frontend && npm run dev` | http://localhost:5173 |
