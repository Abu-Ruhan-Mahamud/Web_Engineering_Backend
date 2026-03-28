# CUROVA — Project Setup Guide

## Prerequisites
- **Python** 3.12+ (tested with 3.14.2)
- **Node.js** 18+ (tested with 22.x)
- **PostgreSQL** 14+
- **OS:** Linux (Fedora/Mint) or Windows

---

## 1. Database Setup

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE curova_db;
CREATE USER curova_user WITH PASSWORD 'curova_pass_2026';
ALTER ROLE curova_user SET client_encoding TO 'utf8';
ALTER ROLE curova_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE curova_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;
ALTER DATABASE curova_db OWNER TO curova_user;
\q
```

> If your PostgreSQL credentials differ, update `backend/.env` accordingly.

---

## 2. Backend Setup

```bash
cd WebProject_Curova

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
# Edit backend/.env if needed (DB credentials, secret key)

# Run migrations
cd backend
python manage.py migrate

# Create superuser (optional — for admin access)
python manage.py createsuperuser

# Start backend server
python manage.py runserver 8000
```

Backend runs at: `http://127.0.0.1:8000`

---

## 3. Frontend Setup

```bash
cd WebProject_Curova/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 4. Environment Variables

The file `backend/.env` controls all config:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (set) | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `DB_NAME` | `curova_db` | PostgreSQL database name |
| `DB_USER` | `curova_user` | PostgreSQL username |
| `DB_PASSWORD` | `curova_pass_2026` | PostgreSQL password |
| `DB_HOST` | `127.0.0.1` | Database host |
| `DB_PORT` | `5432` | Database port |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Django allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | CORS whitelist |

---

## 5. Test Accounts

After running migrations and creating users (or loading test data):

| Role | Email | Password |
|------|-------|----------|
| Patient | `testpatient@curova.com` | `testpass123` |
| Doctor | `testdoctor@curova.com` | `testpass123` |
| Admin | `admin@curova.com` | `testpass123` |
| Lab Tech | `labtech@curova.com` | `testpass123` |

> These accounts only exist if previously created. Use `/register` or `createsuperuser` to create new ones.

---

## 6. Project Structure

```
WebProject_Curova/
├── backend/                    # Django + DRF API
│   ├── curova_backend/         # Django project settings
│   ├── users/                  # Auth, profiles, roles
│   ├── appointments/           # Appointment booking & management
│   ├── medical/                # Medical records & prescriptions
│   ├── medications/            # Medications & reminders
│   ├── documents/              # Patient document uploads
│   ├── messaging/              # Messaging (models defined, API pending)
│   ├── lab_tests/              # Lab test orders & results
│   ├── media/                  # Uploaded files
│   ├── .env                    # Environment config
│   ├── requirements.txt        # Python dependencies
│   └── manage.py
├── frontend/                   # React 19 + Vite 7
│   ├── src/
│   │   ├── components/         # Shared components (layouts, guards)
│   │   ├── pages/              # All page components by role
│   │   ├── contexts/           # AuthContext
│   │   ├── services/           # API client (axios)
│   │   ├── hooks/              # Custom hooks
│   │   ├── utils/              # Shared utilities (icons, etc.)
│   │   └── styles/             # All CSS files
│   ├── package.json
│   └── vite.config.js
└── project_docs/               # Planning docs & demo HTML designs
    ├── PLAN.md
    ├── project.md
    └── frontend_design_demo/   # 16 reference HTML files
```

---

## 7. Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Django | 6.0.2 |
| API | Django REST Framework | 3.16.1 |
| Database | PostgreSQL | 14+ |
| Frontend | React | 19.2 |
| Bundler | Vite | 7.3.1 |
| Routing | React Router DOM | 7.13 |
| HTTP Client | Axios | 1.13 |
| Auth | DRF TokenAuthentication | — |

---

## 8. Current Status

**Completed (24 features):** Authentication, all Patient/Doctor/Admin/Lab Tech pages, lab test system, documents system, emoji→SVG icon cleanup.

**Pending (2 features):**
1. **Notifications** — No backend app yet. Bell icon in header is decorative only.
2. **Messaging** — Backend models exist (`Conversation`, `Message`) but views/serializers/URLs are empty. No frontend pages. Demo design exists at `project_docs/frontend_design_demo/messaging_chat.html`.

---

## 9. Build for Production

```bash
cd frontend
npm run build    # Outputs to frontend/dist/
```

Last verified: 140 modules, 0 errors.
