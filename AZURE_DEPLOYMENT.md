# Curova - Azure Deployment Guide

This guide covers deploying Curova to **Azure** using:
- **Backend**: Azure App Service (Django)
- **Frontend**: Azure Static Web Apps (React)
- **Database**: Azure Database for PostgreSQL
- **Authentication**: Azure Entra ID + Google OAuth

## Prerequisites

✅ Azure account with student credit ($100+)
✅ GitHub repositories connected
✅ Azure CLI installed locally

## Quick Setup (5 mins)

### 1. Create Azure Resource Group
```bash
az group create --name curova-rg --location eastus
```

### 2. Deploy PostgreSQL Database
```bash
az postgres server create \
  --resource-group curova-rg \
  --name curova-db \
  --admin-user postgres \
  --admin-password YourSecurePassword123 \
  --sku-name B_Gen5_1 \
  --storage-size 51200
```

### 3. Get Connection String
```bash
# Copy the connection string from Azure Portal
# Format: postgresql://user:password@host:5432/postgres
```

### 4. Deploy Backend to App Service
```bash
# Create App Service Plan
az appservice plan create \
  --name curova-api-plan \
  --resource-group curova-rg \
  --sku B1 \
  --is-linux

# Create App Service
az webapp create \
  --resource-group curova-rg \
  --plan curova-api-plan \
  --name curova-api \
  --runtime "PYTHON|3.11"

# Set environment variables
az webapp config appsettings set \
  --resource-group curova-rg \
  --name curova-api \
  --settings \
    SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
    DEBUG=False \
    ALLOWED_HOSTS="*.azurewebsites.net,localhost" \
    DATABASE_URL="postgresql://user:password@curova-db.postgres.database.azure.com:5432/postgres" \
    CORS_ALLOWED_ORIGINS="https://your-frontend.azurestaticapps.net" \
    GOOGLE_CLIENT_ID="your-google-client-id"
```

### 5. Deploy Backend Code
```bash
cd backend
az webapp up --resource-group curova-rg --name curova-api
```

### 6. Deploy Frontend to Static Web Apps
```bash
# Via Azure Portal:
# 1. Create Static Web Apps resource
# 2. Connect to your GitHub frontend repository
# 3. Select "React" as build preset
# 4. Build output: "dist"
# 5. Azure will auto-build and deploy on every push
```

### 7. Configure CORS
Update `CORS_ALLOWED_ORIGINS` in App Service to match your Static Web Apps URL:
```
https://your-app-name.azurestaticapps.net
```

## Environment Variables Required

**Backend (.env)**
```
SECRET_KEY=<generated-strong-key>
DEBUG=False
ALLOWED_HOSTS=curova-api.azurewebsites.net,localhost
DATABASE_URL=postgresql://user:password@host:5432/dbname
DJANGO_SETTINGS_MODULE=curova_backend.settings
CORS_ALLOWED_ORIGINS=https://your-frontend.azurestaticapps.net
GOOGLE_CLIENT_ID=your-client-id
```

**Frontend (.env)**
```
VITE_API_URL=https://curova-api.azurewebsites.net/api
VITE_GOOGLE_CLIENT_ID=your-client-id
```

## Running Database Migrations

```bash
# SSH into App Service
az webapp remote-connection create \
  --resource-group curova-rg \
  --name curova-api

# Then run:
python manage.py migrate
python manage.py createsuperuser
```

## Cost Estimate

- **App Service Plan (B1)**: ~$10/month
- **Static Web Apps**: ~$10/month (free tier available)
- **PostgreSQL (B_Gen5_1)**: ~$15/month
- **Total**: ~$35/month (well within $100 credit)

## Troubleshooting

### Health Check Failing
- Ensure `/health/` endpoint returns 200 OK
- Check ALLOWED_HOSTS configuration

### Database Connection Issues
- Verify CONNECTION_STRING is correct
- Check firewall rules allow Azure resources
- Test locally with same DATABASE_URL

### API Calls from Frontend Failing
- Verify CORS_ALLOWED_ORIGINS matches frontend URL
- Check if API returns `Access-Control-Allow-Origin` header
- Frontend should make requests to `/api` (configured in routes)

## Next Steps

1. ✅ Create Azure Resource Group
2. ✅ Deploy PostgreSQL
3. ✅ Deploy Django to App Service
4. ✅ Deploy React to Static Web Apps
5. ✅ Test full stack integration
6. ✅ Set up monitoring/alerts
7. ✅ Configure custom domain (optional)
