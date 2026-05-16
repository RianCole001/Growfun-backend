# Update Render Start Command

## Current Status
✅ Build is successful
❌ Migrations are NOT running (using old start command)

## What You Need to Do

### Step 1: Update Start Command in Render

1. Go to **Render Dashboard**: https://dashboard.render.com/
2. Click on your **growfund-backend-2** service
3. Go to **Settings** tab
4. Scroll down to **Start Command**
5. Change from:
   ```
   gunicorn growfund.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
   ```
   To:
   ```
   bash start.sh
   ```
6. Click **Save Changes**
7. Render will automatically redeploy

### Step 2: Verify Deployment

After redeployment, check the logs for:
```
🔄 Running database migrations...
⚙️ Setting up platform settings...
💰 Setting up crypto prices...
🚀 Starting Gunicorn server...
```

## What Was Fixed

### Issue 1: Database Connection During Build
- **Problem**: Migrations tried to run during build phase (no database access)
- **Fix**: Moved migrations to `start.sh` (runs during runtime when database is accessible)

### Issue 2: USDT Scheduler Starting Too Early
- **Problem**: USDT checker tried to access database during app initialization
- **Fix**: Updated `transactions/apps.py` to skip scheduler during migrations and collectstatic

## Files Modified
- ✅ `backend-growfund/build.sh` - Removed database operations
- ✅ `backend-growfund/start.sh` - Added migrations and setup commands
- ✅ `backend-growfund/transactions/apps.py` - Fixed USDT scheduler initialization

## Your Service URL
https://growfund-backend-2.onrender.com

## Next Steps
1. Update Start Command in Render (see Step 1 above)
2. Wait for automatic redeployment
3. Verify migrations ran successfully in logs
4. Test API endpoints
