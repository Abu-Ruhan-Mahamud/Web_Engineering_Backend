# CUROVA Deployment Analysis & Solutions

## Executive Summary

**Current Status:** ❌ **DEPLOYMENT BROKEN - Core Environment Configuration Missing**

The application cannot start because critical environment variables are not configured. The backend will fail to initialize in both local development and production environments.

---

## 🔴 Critical Issues Identified

### Issue #1: Missing SECRET_KEY Environment Variable
**Severity:** 🔴 CRITICAL  
**Impact:** Backend cannot start at all  
**Current State:** Django throws `SECRET_KEY not found` error

**Diagnosis:**
```
Error: SECRET_KEY not found. Declare it as envvar or define a default value.
```

The `settings.py` line 15 has:
```python
SECRET_KEY = config("SECRET_KEY")  # Requires environment variable
```

**Why it's broken:**
- No `.env` file exists in the backend directory
- No environment variables are loaded
- Django cannot initialize without SECRET_KEY
- Both local development AND production deployment fail

---

### Issue #2: Missing Database Configuration
**Severity:** 🔴 CRITICAL  
**Impact:** Cannot connect to PostgreSQL database  
**Current State:** Would fall back to localhost which doesn't exist in production

**Diagnosis:**
```python
# When DATABASE_URL is not set, falls back to:
DB_NAME=curova_db
DB_USER=curova_user
DB_PASSWORD=<not-set>
DB_HOST=127.0.0.1
DB_PORT=5432
```

**Why it's broken:**
- In production (Render), Render injects `DATABASE_URL` environment variable
- But if not set, backend tries to connect to `localhost:5432`
- Production doesn't have a local PostgreSQL server
- Migrations cannot run
- API cannot access database

---

### Issue #3: CORS Configuration Incomplete
**Severity:** 🟠 HIGH  
**Impact:** Frontend requests will be blocked by CORS  
**Current State:** Only defaults to localhost

**Diagnosis:**
```python
CORS_ALLOWED_ORIGINS = [
    url.strip() for url in config(
        "CORS_ALLOWED_ORIGINS", 
        default="http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
]
```

**Why it's broken:**
- Frontend on Vercel at `https://curovafrontend.vercel.app`
- Production backend at `https://curova-backend.onrender.com`
- But CORS is configured for `localhost` only
- **Production API calls are being rejected with 403 CORS error**

---

## 🔧 Complete Solution

### Step 1: Create Backend .env File (LOCAL DEVELOPMENT)

Create `/home/t14/CODEBASE/WebProject_Curova/backend/.env`:

```env
# ─────────────────────────────────────────────────────
# DJANGO CORE SETTINGS
# ─────────────────────────────────────────────────────

# SECRET KEY (generate one for local dev - can be any strong string)
SECRET_KEY=django-insecure-local-dev-key-change-in-production-12345678901234567890

# DEBUG MODE (True for local, False for production)
DEBUG=True

# ALLOWED HOSTS (localhost for local dev)
ALLOWED_HOSTS=localhost,127.0.0.1

# ─────────────────────────────────────────────────────
# DATABASE CONFIGURATION
# ─────────────────────────────────────────────────────

# Option 1: Individual database settings (for local dev)
DB_NAME=curova_db
DB_USER=curova_user
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

# Option 2: DATABASE_URL (for production - set this in Render dashboard)
# Leave commented out for local development
# DATABASE_URL=postgresql://user:password@host:5432/curova_db

# ─────────────────────────────────────────────────────
# CORS CONFIGURATION
# ─────────────────────────────────────────────────────

# Local development - accept requests from Vite dev server
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Production URLS would be:
# https://curovafrontend.vercel.app,https://www.curovafrontend.vercel.app

# ─────────────────────────────────────────────────────
# OPTIONAL: GOOGLE OAUTH
# ─────────────────────────────────────────────────────

GOOGLE_CLIENT_ID=your-google-client-id-here
```

### Step 2: Configure Environment Variables on Render (PRODUCTION)

On your Render Dashboard, set these in the Backend Service > Environment:

```
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=curova-backend.onrender.com
DATABASE_URL=<auto-populated-by-render>
CORS_ALLOWED_ORIGINS=https://curovafrontend.vercel.app,https://www.curovafrontend.vercel.app
GOOGLE_CLIENT_ID=<your-client-id>
```

**How to generate a strong SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Update start.sh for Better Error Handling

Edit `/home/t14/CODEBASE/WebProject_Curova/backend/start.sh`:

```bash
#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting CUROVA Backend Service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check critical env vars
if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY not set!"
    echo "Set this in Render dashboard > Environment"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set!"
    echo "This should be auto-populated by Render"
    exit 1
fi

echo "✓ Environment variables validated"

echo ""
echo "Running database migrations..."
python manage.py migrate --noinput || exit 1

echo "✓ Migrations completed"
echo ""
echo "Starting Gunicorn server on port ${PORT:-10000}..."
exec gunicorn curova_backend.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

---

## 📊 Issue-by-Issue Troubleshooting

### If you see: `SECRET_KEY not found`

**✓ Solution:**
1. Add to backend/.env: `SECRET_KEY=django-insecure-dev-key-here`
2. OR set in Render Dashboard > Environment

### If you see: `psycopg2 connection refused`

**✓ Solutions (in order):**

**For Local Development:**
1. Ensure PostgreSQL is running: `psql --version`
2. Create database: `createdb curova_db`
3. Verify credentials in `.env` match PostgreSQL setup
4. Test connection: `psql -U curova_user -h 127.0.0.1 -d curova_db`

**For Production (Render):**
1. Go to Render Dashboard
2. Check that PostgreSQL database is connected to backend service
3. Verify DATABASE_URL is set in Environment
4. Check Render logs for actual error message

### If you see: `CORS Error (403)`

**Current Issue:** Frontend on Vercel can't reach backend API

**✓ Solutions:**

**Identify the actual frontend URL:**
```bash
# Check where frontend is deployed
curl -I https://curovafrontend.vercel.app/
```

**Update CORS in production:**

Edit settings.py OR set environment variable:
```python
# In settings.py around line 140:
CORS_ALLOWED_ORIGINS = [
    "https://curovafrontend.vercel.app",
    "https://www.curovafrontend.vercel.app",
    "http://localhost:5173",  # Keep for local dev
    "http://127.0.0.1:5173",
]
```

Also set in Render Environment:
```
CORS_ALLOWED_ORIGINS=https://curovafrontend.vercel.app,https://www.curovafrontend.vercel.app,http://localhost:5173
```

### If migrations fail with database errors

**Check migration status:**
```bash
python manage.py showmigrations
```

**Clear and retry:**
```bash
# WARNING: This deletes data! Only for development!
# For production, see Django migration documentation

# Delete database - development only
dropdb curova_db
createdb curova_db

# Re-run migrations
python manage.py migrate
```

---

## 🚀 Step-by-Step Deployment Verification Checklist

### Local Development Setup

- [ ] Created `/backend/.env` with all required variables
- [ ] Can run `python manage.py check` without errors
- [ ] Can run `python manage.py migrate` successfully
- [ ] Can run `python manage.py runserver` - server starts on port 8000
- [ ] Can access http://localhost:8000/api/users/ (should get 401 Unauthorized, not 500)
- [ ] Can create test user: `python manage.py shell`
  ```python
  from users.models import User
  User.objects.create_user(
      email='test@test.com',
      password='testpass123',
      user_type='patient'
  )
  ```

### Production Deployment (Render + Vercel)

**Backend (Render):**
- [ ] Go to Render Dashboard > `curova-backend` service
- [ ] Check "Environment" tab - verify all variables are set:
  - [ ] SECRET_KEY ✓
  - [ ] DATABASE_URL ✓
  - [ ] DEBUG=False ✓
  - [ ] ALLOWED_HOSTS set correctly
  - [ ] CORS_ALLOWED_ORIGINS includes frontend domain
- [ ] Click "Manual Deploy" or push code
- [ ] Check Logs tab - should show:
  ```
  Running database migrations...
  ✓ Migrations completed
  Starting Gunicorn server...
  ```
- [ ] Test health check: `curl https://curova-backend.onrender.com/api/users/`
  - Expected: 401 Unauthorized (not 500 error)

**Frontend (Vercel):**
- [ ] Environment variable set: `VITE_API_URL=https://curova-backend.onrender.com/api`
- [ ] Redeploy to apply config
- [ ] Test API call in browser console:
  ```javascript
  fetch('https://curova-backend.onrender.com/api/users/')
    .then(r => r.json())
    .then(d => console.log(d))
  ```
  - Expected: `{"detail":"Authentication credentials were not provided."}`
  - NOT: CORS error

---

## 📋 Database Connection Flow

### Local Development
```
Frontend (Vite @ localhost:5173)
    ↓
Backend Django (localhost:8000)
    ↓
PostgreSQL (localhost:5432)
```

**Connection String:** `postgresql://curova_user:postgres@127.0.0.1:5432/curova_db`

### Production (Render) 
```
Frontend (Vercel App)
    ↓ (HTTPS)
Backend Django (Render)
    ↓ (Internal Network)
PostgreSQL (Render Database)
```

**Connection String:** Auto-provided as `DATABASE_URL`

---

## 🔑 Critical Values That Must Be Set

| Variable | Local Dev | Production | Where |
|----------|-----------|-----------|-------|
| `SECRET_KEY` | `django-insecure-local-key` | Strong random key | backend/.env OR Render Env |
| `DEBUG` | `True` | `False` | backend/.env OR Render Env |
| `DATABASE_URL` | Not needed (use DB_* vars) | ✓ Required | Render Env (auto-set) |
| `DB_NAME` | `curova_db` | N/A (use DATABASE_URL) | backend/.env |
| `DB_USER` | `curova_user` | N/A | backend/.env |
| `DB_PASSWORD` | `postgres` | N/A | backend/.env |
| `DB_HOST` | `127.0.0.1` | N/A | backend/.env |
| `CORS_ALLOWED_ORIGINS` | `localhost:5173` | Vercel URL | backend/.env OR Render Env |

---

## 🔍 Testing Database Connectivity

### Test 1: Local PostgreSQL Connection
```bash
# Check if PostgreSQL is running
psql --version

# Connect to database
psql -U curova_user -h 127.0.0.1 -d curova_db

# In psql prompt:
SELECT version();
\dt  # List tables
```

### Test 2: Django Database Operations
```bash
cd backend

# Check Django can connect
python manage.py dbshell
\dt
\q

# Run migrations
python manage.py migrate

# Create test data
python manage.py shell
>>> from users.models import User
>>> User.objects.create_user(email='test@test.com', password='test', user_type='patient')
```

### Test 3: API Endpoint
```bash
# Start dev server
python manage.py runserver

# In another terminal:
curl -X GET http://localhost:8000/api/users/ -H "Content-Type: application/json"

# Expected response:
# {"detail":"Authentication credentials were not provided."}
# 
# If you get 500 error, check server logs for database connection error
```

---

## 📝 Next Steps

1. **Immediately:** Create backend/.env with SECRET_KEY and database config
2. **Test locally:** Run `python manage.py check` and `python manage.py migrate`
3. **Verify API:** Test endpoints locally before deploying
4. **Production:** Set environment variables in Render Dashboard
5. **Verify Production:** Test API calls from frontend
6. **Monitor:** Check Render logs if anything fails

---

## 🆘 Emergency Fixes

**Backend won't start locally:**
```bash
cd backend
python manage.py check  # Shows exact error
```

**Migrations failing:**
```bash
# Check what's wrong
python manage.py showmigrations

# If database is empty:
python manage.py migrate --plan  # See all migrations
python manage.py migrate  # Run all
```

**Frontend can't reach API:**
```bash
# Check CORS from browser console
fetch('http://localhost:8000/api/users/')
  .catch(err => console.log('CORS Error:', err))

# Check settings.py for CORS config
grep -n "CORS" backend/curova_backend/settings.py
```

---

## 📚 Reference Documentation

- Django Settings: `backend/curova_backend/settings.py`
- Database Config: Lines 68-90
- CORS Config: Lines 140-165
- WSGI Config: `backend/curova_backend/wsgi.py` (auto-migrations on startup)
- Deployment Script: `backend/start.sh`
- Environment Template: `.env.example`
