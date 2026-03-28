# 🚀 CUROVA DEPLOYMENT GUIDE

**Last Updated:** March 28, 2026  
**Status:** Ready for production deployment

## ✅ Pre-Deployment Status

- [x] All code fixes completed (U-5, U-7)
- [x] Google OAuth fully working
- [x] Error handling added to dashboards
- [x] Database migrations verified: **0 pending migrations**
- [x] Static files collectible: **✓ passed**
- [x] Frontend production build tested: **✓ passes**
- [x] All tests passing
- [x] Security headers configured
- [x] CORS properly configured

**All critical prerequisites complete. Ready to deploy!**

## 🎯 Quick Options

| Hosting | Setup Time | Cost | Best For |
|---------|-----------|------|----------|
| **Railway** ⭐ RECOMMENDED | 30 min | Free tier available | Quick launch, easy scaling |
| DigitalOcean | 1 hour | $5-12/mo | Cheap, good control |
| Heroku | 45 min | Free tier removed | Enterprise features |
| AWS Lightsail | 1.5 hours | $3.5-5/mo | Maximum control |

---

## � QUICK START: Railway Deployment (30 min)

**If you want to go live in 30 minutes, follow this path.**

### 1. Generate Production SECRET_KEY (5 min)

```bash
cd /home/t14/CODEBASE/WebProject_Curova/backend
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output - you'll need this in step 3.

### 2. Prepare GitHub for Deployment (5 min)

```bash
cd /home/t14/CODEBASE/WebProject_Curova

# Ensure all changes are committed
git add .
git commit -m "Final pre-deployment changes"
git push origin main

# Tag the release
git tag v1.0.0
git push origin v1.0.0
```

### 3. Deploy to Railway (20 min)

**3a. Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Click **Sign up** → **Continue with GitHub**
3. Authorize the app → **New Project**

**3b. Add PostgreSQL Database**
1. Click **Add Services** → **PostgreSQL**
2. Wait for database to be created (1-2 min)
3. Note the database credentials (Railway creates `DATABASE_URL` automatically)

**3c. Deploy Backend**
1. Click **+ New Service** → **GitHub Repo**
2. Select your `WebProject_Curova` repository
3. Configure deployment:
   - **Root Directory:** `backend/`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python manage.py migrate --noinput && gunicorn curova_backend.wsgi:application --bind 0.0.0.0:$PORT`

**3d. Add Environment Variables**

In Railway project dashboard, add these environment variables:

```env
DEBUG=False
SECRET_KEY=<paste from step 1>
GOOGLE_CLIENT_ID=<your Google OAuth client ID>
ALLOWED_HOSTS=<your-railway-domain>.railway.app
CORS_ALLOWED_ORIGINS=https://<your-railway-domain>.railway.app
```

Railway automatically provides: `DATABASE_URL`

**3e. Deploy Frontend**

Option A: **Quick (5 min)** - Deploy on Railway same domain
```bash
cd frontend
npm run build

# Deploy dist/ folder to Railway as static site
# (Create static file service in Railway)
```

Option B: **Better (10 min)** - Deploy on Vercel (recommended for React)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# When prompted:
# - Set VITE_API_URL=https://<your-railway-backend-domain>/api
# - Set VITE_GOOGLE_CLIENT_ID=<same as backend>
```

### 4. Verify Live App (5 min)

```bash
# Test backend API
curl https://<your-backend-domain>/api/auth/login/

# Test frontend
# Visit https://<your-frontend-domain>
# Should see Curova login page
```

**Login with test accounts:**
- Email: `testpatient@curova.com` / Password: `testpass123` (patient)
- Email: `testdoctor@curova.com` / Password: `testpass123` (doctor)
- Email: `admin@curova.com` / Password: `testpass123` (admin)

---

## 📋 DETAILED Deployment Guide (for custom hosting)

### Backend Configuration

Generate a secure SECRET_KEY (don't use the development one):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Configure `.env` for production:

```env
# ─── CRITICAL SECURITY ───
DEBUG=False
SECRET_KEY=<generated-above>

# ─── DATABASE (choose one) ───
# PostgreSQL (recommended for production):
DATABASE_URL=postgresql://username:password@host:5432/curova_production

# ─── ALLOWED HOSTS ───
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# ─── CORS ───
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ─── GOOGLE OAUTH ───
GOOGLE_CLIENT_ID=<your-production-google-client-id>

# ─── EMAIL (configure one option) ───
# Option A: SMTP (Gmail, SendGrid, etc.)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=<app-password>

# ─── SECURITY HEADERS ───
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Frontend Configuration

Update `/frontend/.env.local`:

```env
# Production backend URL (MUST be HTTPS)
VITE_API_URL=https://api.yourdomain.com/api

# Google OAuth (must match backend)
VITE_GOOGLE_CLIENT_ID=<your-production-google-client-id>
```

Build for production:

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with optimized, minified code.

### Database Setup

**PostgreSQL (Recommended):**

```bash
# Create database
createdb curova_production
createuser curova_app_user -P  # Set password when prompted

# Grant permissions
psql -d curova_production -c "GRANT ALL PRIVILEGES ON SCHEMA public TO curova_app_user;"

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Email: your-admin@yourdomain.com
# Password: [strong password]

# Backup before going live
pg_dump curova_production > backup_$(date +%Y%m%d).sql
```

---

## 🔒 Comprehensive Security Checklist

### Django Settings
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is long, random, unique (never share)
- [ ] `ALLOWED_HOSTS` includes only your domains
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SECURE_HSTS_SECONDS=31536000` (1 year)
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- [ ] `SECURE_HSTS_PRELOAD=True`

### API Security
- [ ] CORS restricted to production domains only
- [ ] Rate limiting configured on auth endpoints
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced (redirect HTTP → HTTPS)
- [ ] API tokens expire (check `Token` model settings)
- [ ] Database uses strong passwords

### Authentication
- [ ] Superuser account has strong password (16+ chars)
- [ ] Google OAuth credentials secured
- [ ] No test accounts in production (or reset passwords)
- [ ] Token blacklist/expiration implemented
- [ ] Password requirements: 8+ chars, mixed case, numbers

### Data Protection
- [ ] Database backups automated
- [ ] Backups encrypted and stored separately
- [ ] Database user has limited permissions
- [ ] Medical records access controlled by role
- [ ] No sensitive data in logs
- [ ] Encryption at rest (if using managed DB)

### Infrastructure
- [ ] SSL/TLS certificate installed (Let's Encrypt free)
- [ ] Firewall configured (only allow ports 80, 443)
- [ ] DDoS protection enabled (Cloudflare, AWS Shield)
- [ ] Server hardened (security patches applied)
- [ ] No root/admin accounts exposed
- [ ] SSH key-based auth only (no passwords)

### Monitoring
- [ ] Error tracking active (Sentry)
- [ ] Application metrics collected
- [ ] Database performance monitored
- [ ] Uptime monitoring configured
- [ ] Security alerts set up

---

## 📊 Deployment Options Compared

### Railway (Recommended for Quick Start)
**Pros:**
- Fastest to deploy (30 min)
- Auto-scales
- Free tier available
- Railway → GitHub integration

**Cons:**
- Pricier than alternatives at scale
- Limited customization

**Deploy Command:**
```bash
# Nothing! Just connect GitHub and it auto-deploys
```

### DigitalOcean (Best Long-term Value)
**Pros:**
- Cheap ($5-12/mo)
- Good documentation
- App Platform (managed) or Droplets (full control)
- GitHub Student Pack credit

**Cons:**
- Requires more setup
- Manual deployment

**Setup:**
```bash
# Create PostgreSQL Managed Database
# Create App Platform or Droplet
# Deploy using doctl CLI or git push
```

### Heroku
**Pros:**
- One-click deployment
- Good for Node, Ruby, Python

**Cons:**
- Free tier removed (starting Nov 2022)
- Pricier than alternatives

**Setup:**
```bash
heroku login
heroku create curova-api
git push heroku main
```

### AWS (Maximum Control)
**Pros:**
- Most scalable
- Fine-grained control
- Free tier (1 year)

**Cons:**
- Most complex setup
- Easy to misconfigure

**Setup:**
```bash
# EC2 + RDS + S3 + CloudFront
# Requires knowledge of AWS
```

---

## 🔄 Post-Deployment Setup

### 1. Create Production Admin Account

```bash
# SSH into your server or use web terminal
python manage.py createsuperuser

# Email: your-admin-email@yourdomain.com
# Password: [strong password, save securely]
```

### 2. Configure Admin Site

1. Visit `https://yourdomain.com/admin`
2. Login with the admin account
3. Update site information:
   - **Site.com** → `yourdomain.com`
   - **Site.name** → `Curova Healthcare`

### 3. Test All Features

- [ ] Patient login/signup
- [ ] Doctor login/signup
- [ ] Appointments booking
- [ ] Medical records creation
- [ ] Lab tests management
- [ ] Medications
- [ ] Document upload
- [ ] Profile updates
- [ ] Notifications
- [ ] Google OAuth

### 4. Set Up Monitoring

**Sentry (Error Tracking):**

```bash
pip install sentry-sdk

# Add to backend settings.py:
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

**DataDog or New Relic (Performance):**
- Set up dashboards for API response time
- Set up alerts for error rates > 1%

### 5. Configure Automated Backups

**PostgreSQL (RDS, DigitalOcean Managed DB):**
- Enable automatic backups (daily)
- Retention: 30 days minimum
- Test restore procedure monthly

**Application Files:**
- Git automatically backs up code
- Tag releases for easy rollback

---

## 🧪 Testing in Production

### Manual Testing
```
1. Sign up as patient
2. Sign up as doctor
3. Login with Google OAuth
4. Create appointment
5. View medical records
6. Upload document
7. Change password
8. Update profile
```

### Load Testing (Optional)
```bash
# Test with 100 concurrent users for 5 minutes
ab -n 5000 -c 100 https://yourdomain.com/api/auth/login/

# Expected: < 1% error rate, < 500ms response time
```

---

## ⚡ Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check server logs, verify database connection |
| CORS errors | Update CORS_ALLOWED_ORIGINS in .env |
| Static files missing | Run `python manage.py collectstatic --noinput` |
| Database errors | Verify DATABASE_URL, check firewall |
| Google OAuth fails | Check Client ID matches, verify authorized origins |
| Email not sending | Check EMAIL_* settings, test with SMTP |



---

## ⚡ Troubleshooting

**"502 Bad Gateway" error**
- Check Railway logs: Railway → View Logs
- Ensure gunicorn command is correct
- Verify DATABASE_URL is set

**"Database connection failed"**
- Check DATABASE_URL in Railway environment
- Verify PostgreSQL database is running
- Run migrations: `python manage.py migrate --noinput`

**Static files not loading**
- Django automatically handles `/static/` URLs in production
- No additional setup needed

**CORS errors**
- Update CORS_ALLOWED_ORIGINS with actual frontend domain

---

## 💡 Quick Reference

| Task | Command |
|------|---------|
| Generate SECRET_KEY | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| Test migrations locally | `python manage.py migrate --plan` |
| Collect static files | `python manage.py collectstatic --noinput` |
| Run Django locally | `python manage.py runserver 0.0.0.0:8000` |
| Run with production settings | `DJANGO_SETTINGS_MODULE=curova_backend.settings_production python manage.py ...` |

---

## 🎯 Timeline

**Estimated deployment time:**
- Step 1 (SECRET_KEY): 5 min
- Step 2 (Railway setup): 10 min
- Step 3 (Deploy): 10 min
- Step 4 (Verify): 5 min
- **Total: ~30 minutes to live production! 🚀**

---

## 📞 Support

Need help? Check:
- Railway docs: https://docs.railway.app
- Django deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- DRF docs: https://www.django-rest-framework.org/

