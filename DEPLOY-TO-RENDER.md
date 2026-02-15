# Deploy to Render - Quick Guide

## What Changed ✅

Your backend now uses smart CORS configuration:
- **Development (DEBUG=True)**: Allows ALL origins (works with any ngrok URL, localhost, etc.)
- **Production (DEBUG=False)**: Restricts to specific allowed origins

## Deploy Steps

### 1. Commit Changes

```bash
git add backend-growfund/growfund/settings.py
git commit -m "Smart CORS configuration for development and production"
git push origin main
```

### 2. Deploy on Render

**Option A: Automatic Deploy**
- If you have auto-deploy enabled, Render will deploy automatically after push

**Option B: Manual Deploy**
1. Go to https://dashboard.render.com/
2. Click on your backend service
3. Click "Manual Deploy" button
4. Select "Deploy latest commit"
5. Wait for deployment to complete (usually 2-5 minutes)

### 3. Verify Environment Variables

Make sure these are set in Render dashboard:

**Required:**
- `DEBUG=True` (for development)
- `SECRET_KEY=your-secret-key`
- `DATABASE_URL=your-database-url`

**Optional but Recommended:**
- `ALLOWED_HOSTS=growfun-backend.onrender.com`
- `FRONTEND_URL=https://f9ce-41-81-28-77.ngrok-free.app`

### 4. Check Deployment Logs

In Render dashboard:
1. Click "Logs" tab
2. Look for:
   ```
   Starting gunicorn
   Listening at: http://0.0.0.0:10000
   ```
3. Check for any errors

### 5. Test CORS

From your React app console:

```javascript
// Test OPTIONS request (CORS preflight)
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'https://f9ce-41-81-28-77.ngrok-free.app',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'content-type'
  }
})
.then(response => {
  console.log('✅ CORS Status:', response.status);
  console.log('✅ CORS Headers:', [...response.headers.entries()]);
})
.catch(error => console.error('❌ CORS Error:', error));
```

Expected response headers:
```
Access-Control-Allow-Origin: https://f9ce-41-81-28-77.ngrok-free.app
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
```

### 6. Test Login

```javascript
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    email: 'admin@growfund.com',
    password: 'your-password'
  })
})
.then(res => res.json())
.then(data => {
  console.log('✅ Login Success:', data);
  localStorage.setItem('accessToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);
})
.catch(err => console.error('❌ Login Error:', err));
```

## Troubleshooting

### Issue: Still getting CORS errors

**Check 1: Verify deployment completed**
- Go to Render dashboard
- Check "Events" tab for successful deployment
- Look for "Deploy succeeded" message

**Check 2: Verify DEBUG=True**
```bash
# Check in Render dashboard → Environment
DEBUG=True
```

**Check 3: Clear browser cache**
- Open DevTools (F12)
- Right-click refresh button
- Select "Empty Cache and Hard Reload"

**Check 4: Check response headers**
- Open DevTools → Network tab
- Look at the OPTIONS request
- Check Response Headers for `Access-Control-Allow-Origin`

### Issue: 500 Internal Server Error

**Check Render logs:**
1. Go to Render dashboard
2. Click "Logs" tab
3. Look for Python errors
4. Common issues:
   - Missing environment variables
   - Database connection errors
   - Import errors

### Issue: Admin page not loading

**Solution:**
1. Run migrations on Render:
   - Go to Shell tab in Render dashboard
   - Run: `python manage.py migrate`

2. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Production Deployment

When ready for production:

### 1. Update settings.py

Set `DEBUG=False` in Render environment variables

### 2. Add Production Frontend URL

In `settings.py`, update:
```python
else:
    # Production: Restrict to specific origins
    CORS_ALLOWED_ORIGINS = [
        'https://your-production-frontend.com',
        'https://www.your-production-frontend.com',
    ]
```

### 3. Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Set specific `ALLOWED_HOSTS`
- [ ] Use production database (PostgreSQL)
- [ ] Enable HTTPS only
- [ ] Set up proper logging
- [ ] Configure static files serving
- [ ] Set up monitoring/alerts
- [ ] Regular backups

## Quick Commands

### View Logs
```bash
# In Render dashboard → Logs tab
# Or use Render CLI:
render logs -s your-service-name
```

### Run Migrations
```bash
# In Render dashboard → Shell tab
python manage.py migrate
```

### Create Admin User
```bash
# In Render dashboard → Shell tab
python manage.py createsuperuser
```

### Check Django Settings
```bash
# In Render dashboard → Shell tab
python manage.py diffsettings
```

## Support

If deployment fails:
1. Check Render logs for errors
2. Verify all environment variables are set
3. Test locally first: `python manage.py runserver`
4. Check database connection
5. Verify requirements.txt is up to date

## Next Steps

After successful deployment:
1. ✅ Test all API endpoints
2. ✅ Test login/register from frontend
3. ✅ Test Korapay integration
4. ✅ Monitor logs for errors
5. ✅ Set up error tracking (Sentry, etc.)
