# Fresh Render Deployment Guide

## Complete Setup for New Render Service

### Prerequisites
- GitHub repository: `https://github.com/RianCole001/Growfun-backend.git`
- Render account: https://dashboard.render.com/

---

## Step 1: Create PostgreSQL Database

1. Go to **Render Dashboard** → Click **New +** → Select **PostgreSQL**
2. Configure:
   - **Name**: `growfund-database` (or your preferred name)
   - **Database**: `growfund_db`
   - **User**: `growfund_user` (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free or Starter (based on your needs)
3. Click **Create Database**
4. **Save the Internal Database URL** (you'll need this in Step 3)
   - Format: `postgresql://user:password@host/database`

---

## Step 2: Create Web Service

1. Go to **Render Dashboard** → Click **New +** → Select **Web Service**
2. Connect your GitHub repository:
   - Select **Growfun-backend** repository
   - Click **Connect**
3. Configure Basic Settings:
   - **Name**: `growfund-backend` (or your preferred name)
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Root Directory**: `backend-growfund`
   - **Runtime**: `Python 3`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `bash start.sh`
   - **Plan**: Free or Starter

---

## Step 3: Configure Environment Variables

Click **Advanced** → Add the following environment variables:

### Required Variables

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production-min-50-chars
DEBUG=False
ALLOWED_HOSTS=*

# Database (use Internal Database URL from Step 1)
DATABASE_URL=postgresql://user:password@host/database

# Frontend URLs
FRONTEND_URL=https://growfundapp.us
BACKEND_URL=https://your-service-name.onrender.com

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://your-service-name.onrender.com,https://growfundapp.us,https://www.growfundapp.us

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email Configuration (Optional - for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@growfund.com

# Payment Gateway - Korapay (Optional)
KORAPAY_BASE_URL=https://api.korapay.com/merchant/api/v1
KORAPAY_SECRET_KEY=your-korapay-secret-key
KORAPAY_PUBLIC_KEY=your-korapay-public-key
KORAPAY_ENCRYPTION_KEY=your-korapay-encryption-key
KORAPAY_WEBHOOK_URL=https://your-service-name.onrender.com/api/transactions/korapay/webhook/

# USDT TRC20 Configuration (Optional)
USDT_WALLET_ADDRESS=TNGbuN1FPWJDsxd9wtoyoAqeRvCVuPuDXm
TRONGRID_API_KEY=your-trongrid-api-key

# CoinGecko API (Optional)
COINGECKO_API_KEY=your-coingecko-api-key

# Celery/Redis (Optional - if using background tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Generate SECRET_KEY

Run this locally to generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Step 4: Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repository
   - Run `build.sh` (install dependencies, collect static files)
   - Run `start.sh` (run migrations, setup platform, start server)
3. Wait for deployment to complete (5-10 minutes)

---

## Step 5: Verify Deployment

### Check Logs
Look for these success messages:
```
📦 Installing dependencies...
📁 Collecting static files...
✅ Build completed successfully!
🔄 Running database migrations...
⚙️ Setting up platform settings...
💰 Setting up crypto prices...
🚀 Starting Gunicorn server...
```

### Test API Endpoints
```bash
# Health check
curl https://your-service-name.onrender.com/

# Admin login
curl https://your-service-name.onrender.com/api/admin/login/

# User registration
curl https://your-service-name.onrender.com/api/accounts/register/
```

---

## Step 6: Create Admin User

### Option 1: Using Render Shell
1. Go to your service → **Shell** tab
2. Run:
```bash
cd backend-growfund
python manage.py createsuperuser
```

### Option 2: Using Management Command
1. Go to your service → **Shell** tab
2. Run:
```bash
cd backend-growfund
python create_tabby_admin.py
```

---

## Step 7: Configure Custom Domain (Optional)

1. Go to your service → **Settings** → **Custom Domains**
2. Add your domain (e.g., `api.growfundapp.us`)
3. Update DNS records as instructed by Render
4. Update environment variables:
   - `BACKEND_URL=https://api.growfundapp.us`
   - `CSRF_TRUSTED_ORIGINS=https://api.growfundapp.us,...`

---

## Important Files Reference

### `build.sh` (Build Phase - No Database Access)
```bash
#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build completed successfully!"
```

### `start.sh` (Runtime Phase - Database Available)
```bash
#!/usr/bin/env bash

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "⚙️ Setting up platform settings..."
python manage.py setup_platform_settings || true

echo "💰 Setting up crypto prices..."
python manage.py setup_crypto_prices || true

echo "🚀 Starting Gunicorn server..."
gunicorn growfund.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
```

---

## Troubleshooting

### Build Fails with Database Error
- **Cause**: Migrations running during build phase
- **Fix**: Ensure Build Command is `bash build.sh` (not running migrations)

### Service Starts but 404 Errors
- **Cause**: Root directory not set correctly
- **Fix**: Set Root Directory to `backend-growfund`

### CORS Errors from Frontend
- **Cause**: Frontend URL not in ALLOWED_HOSTS or CORS settings
- **Fix**: Add frontend URL to `CSRF_TRUSTED_ORIGINS` environment variable

### Static Files Not Loading
- **Cause**: Collectstatic not running or WhiteNoise not configured
- **Fix**: Already configured in `build.sh` and `settings.py`

---

## Post-Deployment Checklist

- [ ] Database created and connected
- [ ] Service deployed successfully
- [ ] Migrations ran successfully
- [ ] Admin user created
- [ ] API endpoints responding
- [ ] Frontend can connect to backend
- [ ] Environment variables configured
- [ ] Custom domain configured (if applicable)

---

## Service URLs

After deployment, your service will be available at:
- **Render URL**: `https://your-service-name.onrender.com`
- **Admin Panel**: `https://your-service-name.onrender.com/admin/`
- **API Base**: `https://your-service-name.onrender.com/api/`

---

## Auto-Deployment

Render automatically redeploys when you push to the `main` branch:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Render Support**: https://render.com/support

---

## Summary

Your Render service is now configured with:
✅ Proper build/runtime separation
✅ Database migrations on startup
✅ Static files handling with WhiteNoise
✅ CORS configured for frontend
✅ Environment variables for security
✅ Auto-deployment from GitHub
✅ Production-ready Gunicorn server

**Your backend is ready for production!** 🚀
