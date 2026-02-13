# NGROK Login/Register Fix - Complete Guide

## The Problem

When accessing the frontend via ngrok URL (`https://e1e1-105-160-17-43.ngrok-free.app`), login/register fails with CORS errors:

```
Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login/' from origin 'https://e1e1-105-160-17-43.ngrok-free.app' has been blocked by CORS policy
```

## Root Cause

The frontend was trying to call `http://localhost:8000/api` (localhost) from an ngrok URL (internet). This violates CORS policy because:
- Frontend origin: `https://e1e1-105-160-17-43.ngrok-free.app` (internet)
- API endpoint: `http://localhost:8000/api` (localhost)
- These are different origins → CORS blocks the request

## The Solution

You need to use ngrok URLs for BOTH frontend and backend when accessing via ngrok.

### Step 1: Get Your Ngrok URLs

**Terminal 1 - Frontend (Port 3000):**
```bash
ngrok http 3000
```
Output: `https://e1e1-105-160-17-43.ngrok-free.app` ✅ (you already have this)

**Terminal 2 - Backend (Port 8000):**
```bash
ngrok http 8000
```
Output: `https://XXXX-XXX-XXX-XXX.ngrok-free.app` ← **You need this URL**

### Step 2: Update Frontend .env

Replace the API URL with your backend ngrok URL:

```env
# OLD (WRONG - this is frontend URL):
REACT_APP_API_URL=https://e1e1-105-160-17-43.ngrok-free.app

# NEW (CORRECT - use backend ngrok URL):
REACT_APP_API_URL=https://XXXX-XXX-XXX-XXX.ngrok-free.app/api
```

**Example:**
```env
REACT_APP_API_URL=https://1234-56-78-90.ngrok-free.app/api
```

### Step 3: Update Backend settings.py

Add your backend ngrok URL to `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'e1e1-105-160-17-43.ngrok-free.app',  # Frontend ngrok URL
    'XXXX-XXX-XXX-XXX.ngrok-free.app',    # Backend ngrok URL (ADD THIS)
]
```

The `CORS_ALLOWED_ORIGINS` already has the frontend URL, so that's good.

### Step 4: Restart Services

1. **Stop frontend** (Ctrl+C in Terminal 1)
2. **Stop backend** (Ctrl+C in Terminal 2)
3. **Restart backend:**
   ```bash
   cd backend-growfund
   python manage.py runserver
   ```
4. **Restart frontend:**
   ```bash
   cd Growfund-Dashboard/trading-dashboard
   npm start
   ```

### Step 5: Test

1. Open ngrok frontend URL: `https://e1e1-105-160-17-43.ngrok-free.app`
2. Try to login/register
3. Check browser console (F12) for errors
4. Should work now!

## Important Notes

- **Ngrok URLs change every time you restart** - you'll need to update .env and settings.py each time
- **Use HTTPS** - ngrok provides HTTPS tunnels, so all URLs should be `https://`
- **Include `/api` in frontend URL** - the backend API is at `/api/` path
- **Both URLs must be in ALLOWED_HOSTS** - frontend and backend ngrok URLs

## Quick Reference

| Component | URL | Where |
|-----------|-----|-------|
| Frontend (localhost) | `http://localhost:3000` | Browser |
| Frontend (ngrok) | `https://e1e1-105-160-17-43.ngrok-free.app` | Browser |
| Backend (localhost) | `http://localhost:8000` | settings.py ALLOWED_HOSTS |
| Backend (ngrok) | `https://XXXX-XXX-XXX-XXX.ngrok-free.app` | settings.py ALLOWED_HOSTS |
| API endpoint (localhost) | `http://localhost:8000/api` | .env REACT_APP_API_URL |
| API endpoint (ngrok) | `https://XXXX-XXX-XXX-XXX.ngrok-free.app/api` | .env REACT_APP_API_URL |

## Troubleshooting

**Still getting CORS errors?**
- Check that backend ngrok URL is in `ALLOWED_HOSTS`
- Check that frontend ngrok URL is in `CORS_ALLOWED_ORIGINS`
- Restart both services
- Clear browser cache (Ctrl+Shift+Delete)

**Getting "Connection refused"?**
- Backend is not running - start it with `python manage.py runserver`
- Ngrok tunnel is not running - start it with `ngrok http 8000`

**Getting "Invalid host header"?**
- Backend ngrok URL is not in `ALLOWED_HOSTS`
- Add it and restart backend

## Current Status

✅ Frontend .env updated to use localhost API (for local testing)
⏳ Backend settings.py needs backend ngrok URL added to ALLOWED_HOSTS
⏳ You need to provide backend ngrok URL from `ngrok http 8000`

## Next Steps

1. Run `ngrok http 8000` in a new terminal
2. Copy the ngrok URL (e.g., `https://1234-56-78-90.ngrok-free.app`)
3. Update `backend-growfund/growfund/settings.py` ALLOWED_HOSTS with this URL
4. Restart backend and frontend
5. Test login via ngrok URL
