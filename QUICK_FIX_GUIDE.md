# Quick Deployment Troubleshooting Guide

## 🚀 Your Current Status

| Component | Status | Evidence |
|-----------|--------|----------|
| Django Settings Load | ✅ FIXED | Created backend/.env - Django initializes successfully |
| PostgreSQL Installation | ✅ OK | PostgreSQL 18.1 is installed |
| PostgreSQL Service | ⚠️ UNKNOWN | Need to verify it's running |
| Database Created | ❓ UNKNOWN | Need to create curova_db |
| Migrations Run | ❓ UNKNOWN | Will work once DB is created & service is running |
| API Accessible Locally | ❓ UNKNOWN | Need to test after migrations |
| API Accessible from Vercel | ❌ NO | Production environment variables not set on Render |
| Frontend-to-Backend Connection | ❌ NO | CORS not configured for production URLs |

---

## 🛠️ Immediate Actions Required

### MANDATORY: Fix PostgreSQL (Cannot proceed without this)

The error `psycopg2.OperationalError: could not connect to server` happens because:
- PostgreSQL service is NOT running, OR
- Database doesn't exist, OR
- Credentials are wrong

**Run these commands ONE by ONE in your terminal:**

```bash
# 1. Start PostgreSQL service
sudo systemctl start postgresql

# 2. Verify it's running
sudo systemctl status postgresql
# Should show "● postgresql.service - PostgreSQL (your version)"
# And line: Active: active (running)

# 3. Create the database
sudo -u postgres createdb curova_db

# 4. Create the user and set password
sudo -u postgres createuser curova_user

# 5. Set password for the user
sudo -u postgres psql -c "ALTER USER curova_user WITH PASSWORD 'postgres';"

# 6. Grant permissions
sudo -u postgres psql -d curova_db -c "GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;"

# 7. Test connection
psql -U curova_user -h 127.0.0.1 -d curova_db -c "SELECT 1;"
# Expected output: ?column? \n 1
```

If step 1 fails, PostgreSQL might not be installed. Contact DevOps.
If step 7 fails, credentials are wrong. Redo steps 4-6.

---

### AFTER PostgreSQL is fixed: Test Django

```bash
cd /home/t14/CODEBASE/WebProject_Curova/backend

# This runs Django system checks
python manage.py check

# This should output:
# System check identified no issues (0 silenced).

# If you get errors, come back and show me the exact message.
```

---

### AFTER Django Check passes: Run Migrations

```bash
cd /home/t14/CODEBASE/WebProject_Curova/backend

python manage.py migrate

# Should output many lines like:
# Running migrations...
# Applying contenttypes.0001_initial... OK
# Applying auth.0001_initial... OK
# Applying users.0001_initial... OK
# etc...
# 
# Finally:
# Operations to perform:
#   Apply all migrations: (list of apps)
# Running migrations:
#   Applying ... OK
```

If migrations fail with database error, PostgreSQL isn't running. Go back to PostgreSQL section.

---

### AFTER Migrations: Start Dev Server

```bash
cd /home/t14/CODEBASE/WebProject_Curova/backend

python manage.py runserver 0.0.0.0:8000

# Expected output:
# Starting development server at http://0.0.0.0:8000/
# Quit the server with CONTROL-C.
```

Open in browser: http://localhost:8000/api/users/

**Expected response:**
```json
{"detail":"Authentication credentials were not provided."}
```

**NOT expected (these mean problems):**
- 500 error → Django error, check console logs
- 404 error → URL path wrong
- Blank response → Server crashed

---

## 🔴 Common Error Messages & Fixes

### Error: `DJANGO_SETTINGS_MODULE not set`

**Cause:** Not in the right directory or Python path is wrong
**Fix:**
```bash
cd /home/t14/CODEBASE/WebProject_Curova/backend
export DJANGO_SETTINGS_MODULE=curova_backend.settings
python manage.py check
```

---

### Error: `SECRET_KEY not found` 

**Cause:** .env file not loaded or doesn't exist
**Fix:**
```bash
# Verify .env exists
ls -la /home/t14/CODEBASE/WebProject_Curova/backend/.env

# If not, it was created. Check content:
cat /home/t14/CODEBASE/WebProject_Curova/backend/.env

# If missing, run this to recreate:
cat > /home/t14/CODEBASE/WebProject_Curova/backend/.env << 'EOF'
SECRET_KEY=django-insecure-local-dev-key-v1-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=curova_db
DB_USER=curova_user
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GOOGLE_CLIENT_ID=your-google-client-id-here
EOF
```

---

### Error: `psycopg2.OperationalError: could not connect to server`

**Cause:** PostgreSQL service not running
**Fix:**
```bash
# Start the service
sudo systemctl start postgresql

# Check status
sudo systemctl status postgresql

# If it says "inactive", check why
sudo systemctl start postgresql
# Look for error messages

# If still failing, may need to initialize:
sudo -u postgres /usr/lib/postgresql/18/bin/initdb -D /var/lib/postgresql/18/main
```

---

### Error: `role "curova_user" does not exist`

**Cause:** Database user not created
**Fix:**
```bash
sudo -u postgres createuser curova_user
sudo -u postgres psql -c "ALTER USER curova_user WITH PASSWORD 'postgres';"
sudo -u postgres psql -d curova_db -c "GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;"
```

---

### Error: `FATAL: database "curova_db" does not exist`

**Cause:** Database not created
**Fix:**
```bash
sudo -u postgres createdb curova_db
sudo -u postgres psql -d curova_db -c "GRANT ALL PRIVILEGES ON DATABASE curova_db TO curova_user;"
```

---

### Frontend gets CORS error in browser console

**Cause:** CORS_ALLOWED_ORIGINS doesn't include frontend URL
**Fix:**
For local development (already done):
```python
# backend/curova_backend/settings.py around line 140
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server (already there)
    "http://127.0.0.1:5173",   # Alternative localhost (already there)
]
```

For production (need to do):
Go to Render dashboard, set environment variable:
```
CORS_ALLOWED_ORIGINS=https://curovafrontend.vercel.app,https://www.curovafrontend.vercel.app
```

---

## 📋 Production Deployment Checklist

Only do this AFTER local testing works!

### On Render Dashboard:

1. **Select curova-backend service**
2. **Go to Environment tab**
3. **Add these variables:**

```
SECRET_KEY=<generate-with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=curova-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://curovafrontend.vercel.app
GOOGLE_CLIENT_ID=<your-actual-id>
```

4. **Click Save**
5. **Click Manual Deploy**
6. **Wait for deployment** (usually 2-3 minutes)
7. **Check Logs** - look for:
   - ✓ "Running database migrations..."
   - ✓ "Starting Gunicorn..."
   - ✗ Any error messages = fix before next step

8. **Test the API:**
```bash
curl https://curova-backend.onrender.com/api/users/
# Expected: {"detail":"Authentication credentials were not provided."}
```

### On Vercel Dashboard:

1. **Select curovafrontend project**
2. **Go to Settings > Environment Variables**
3. **Add:**
```
VITE_API_URL=https://curova-backend.onrender.com/api
```
4. **Click Redeploy**

---

## 🧪 Complete Test Suite

Run these to verify everything works:

### Test 1: Django loads
```bash
cd /home/t14/CODEBASE/WebProject_Curova/backend
python manage.py check
# Expected: "System check identified no issues"
```

### Test 2: Database connects
```bash
python manage.py dbshell
\dt
\q
# Expected: Should connect and list tables
```

### Test 3: Migrations work
```bash
python manage.py showmigrations --list | head -20
# Expected: List of migration files
```

### Test 4: Server starts
```bash
python manage.py runserver 0.0.0.0:8000 &
sleep 2
curl http://localhost:8000/api/users/
# Expected: JSON with "detail" key
```

### Test 5: API Endpoints
```bash
# List users (401 is OK)
curl -s http://localhost:8000/api/users/ | python -m json.tool | head -5

# Login endpoint (404 is OK, means endpoint doesn't exist yet - that's normal)
curl -s http://localhost:8000/api/auth/login/ 2>&1 | head -5
```

---

## 🎯 Success Criteria

You know everything is fixed when:

✅ `python manage.py check` → No errors  
✅ `python manage.py migrate` → All migrations run  
✅ `python manage.py runserver` → Server starts  
✅ Browser at `http://localhost:8000/api/users/` → JSON response  
✅ Curl to Render backend → JSON response (not error)  
✅ Browser at Vercel frontend → App loads without console errors  

---

## 🆘 Still Stuck?

Share the EXACT error message from:

1. `python manage.py check` output
2. `python manage.py migrate` output  
3. Server console when trying to access API
4. Browser console CORS error details

And I'll help debug!
