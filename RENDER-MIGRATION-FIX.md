# Render Migration Fix - Database Connection Error

## Problem
The build was failing with:
```
django.db.utils.OperationalError: could not translate host name "dpg-d7c3cm58nd3s73f7u4e0-a" to address: Name or service not known
```

This happens because migrations were running during the **build phase** when the database isn't accessible yet.

## Solution
Separated build and runtime commands:

### 1. Build Script (`build.sh`)
- Only installs dependencies and collects static files
- Does NOT run migrations (database not accessible during build)

### 2. Start Script (`start.sh`) - NEW
- Runs migrations when the service starts (database is accessible)
- Sets up platform settings and crypto prices
- Starts the Gunicorn server

## Render Configuration Update Required

### Update Your Render Service Settings:

1. **Go to your Render Dashboard**
   - Navigate to: https://dashboard.render.com/
   - Select your `growfun-backend` service

2. **Update the Start Command**
   - Go to **Settings** tab
   - Find **Start Command** field
   - Change from:
     ```
     gunicorn growfund.wsgi:application --bind 0.0.0.0:$PORT
     ```
   - To:
     ```
     bash start.sh
     ```

3. **Verify Build Command** (should already be set)
   - Build Command should be: `bash build.sh`

4. **Save Changes**
   - Click **Save Changes** button
   - Render will automatically redeploy

## What Changed

### `build.sh` (Build Phase - No Database Access)
```bash
- Install dependencies
- Collect static files
✅ NO migrations here
```

### `start.sh` (Runtime Phase - Database Available)
```bash
- Run migrations
- Setup platform settings
- Setup crypto prices
- Start Gunicorn server
```

## Verification

After deployment, check the logs:
1. Build logs should show: "Build completed successfully!"
2. Runtime logs should show:
   - "Running database migrations..."
   - "Setting up platform settings..."
   - "Starting Gunicorn server..."

## Alternative: Using Render's Release Command

If you prefer, you can also use Render's built-in **Release Command** feature:

1. In Render Dashboard → Settings
2. Find **Release Command** field (under Advanced)
3. Set to:
   ```
   python manage.py migrate --noinput && python manage.py setup_platform_settings && python manage.py setup_crypto_prices
   ```
4. Keep Start Command as:
   ```
   gunicorn growfund.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```

This runs migrations after build but before starting the service.

## Files Modified
- ✅ `backend-growfund/build.sh` - Removed migration commands
- ✅ `backend-growfund/start.sh` - Created new startup script with migrations

## Next Steps
1. Commit and push these changes (already done)
2. Update Render Start Command to `bash start.sh`
3. Redeploy and verify in logs
