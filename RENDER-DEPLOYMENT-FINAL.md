# Final Render Deployment Guide

## Your URLs

- **Frontend:** https://growfund-dashboard.onrender.com
- **Backend:** https://growfun-backend.onrender.com
- **Backend API:** https://growfun-backend.onrender.com/api

## What Was Updated ✅

1. **CORS Settings** - Now allows your Render frontend URL
2. **CSRF Trusted Origins** - Added your frontend URL
3. **Frontend URL** - Default changed to your Render frontend
4. **Production CORS** - When DEBUG=False, only allows specific origins

## Current Configuration

### Development Mode (DEBUG=True)
- ✅ Allows ALL origins (ngrok, localhost, Render frontend)
- ✅ Perfect for testing

### Production Mode (DEBUG=False)
- ✅ Only allows:
  - https://growfund-dashboard.onrender.com
  - http://localhost:3000
  - http://localhost:3001
  - http://127.0.0.1:3000

## Deployment Steps

### 1. Update Backend Environment Variables on Render

Go to your backend service on Render dashboard and set:

```env
# Required
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url

# Frontend
FRONTEND_URL=https://growfund-dashboard.onrender.com

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@growfund.com

# Korapay (if using)
KORAPAY_BASE_URL=https://api.korapay.com/merchant/api/v1
KORAPAY_SECRET_KEY=sk_test_your_key
KORAPAY_PUBLIC_KEY=pk_test_your_key
KORAPAY_ENCRYPTION_KEY=your_encryption_key
KORAPAY_WEBHOOK_URL=https://growfun-backend.onrender.com/api/transactions/korapay/webhook/

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Optional
COINGECKO_API_KEY=your-api-key
```

### 2. Deploy Backend

```bash
# Commit changes
git add .
git commit -m "Add Render frontend URL to CORS and CSRF settings"
git push origin main
```

Render will automatically deploy if you have auto-deploy enabled.

Or manually deploy:
1. Go to Render dashboard
2. Click your backend service
3. Click "Manual Deploy" → "Deploy latest commit"

### 3. Update Frontend Environment Variables

In your frontend Render service, set:

```env
REACT_APP_API_URL=https://growfun-backend.onrender.com/api
```

### 4. Test Connection

Open browser console on https://growfund-dashboard.onrender.com and run:

```javascript
// Test CORS
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'https://growfund-dashboard.onrender.com'
  }
})
.then(res => console.log('✅ CORS OK:', res.status))
.catch(err => console.error('❌ CORS Error:', err));

// Test API
fetch('https://growfun-backend.onrender.com/api/investments/')
  .then(res => res.json())
  .then(data => console.log('✅ API Response:', data))
  .catch(err => console.error('❌ API Error:', err));
```

## Email Verification Links

With the updated `FRONTEND_URL`, verification emails will now contain:
```
https://growfund-dashboard.onrender.com/verify-email?token=abc123...
```

Instead of:
```
http://localhost:3000/verify-email?token=abc123...
```

## Testing Checklist

### Backend
- [ ] Backend deployed successfully
- [ ] Environment variables set on Render
- [ ] Can access: https://growfun-backend.onrender.com/admin/
- [ ] Can access: https://growfun-backend.onrender.com/api/investments/

### Frontend
- [ ] Frontend deployed successfully
- [ ] REACT_APP_API_URL set correctly
- [ ] Can access: https://growfund-dashboard.onrender.com
- [ ] No CORS errors in console

### Integration
- [ ] Login works from frontend
- [ ] Registration works
- [ ] Email verification link points to correct URL
- [ ] Admin panel accessible
- [ ] Deposits/withdrawals can be approved

## Common Issues

### Issue: Still getting CORS errors

**Check:**
1. Backend is deployed with latest code
2. `DEBUG=True` in Render environment variables
3. Clear browser cache
4. Try in incognito mode

**Quick Fix:**
Ensure `DEBUG=True` on Render - this allows all origins.

### Issue: Email verification links point to localhost

**Solution:**
Set `FRONTEND_URL=https://growfund-dashboard.onrender.com` in Render environment variables.

### Issue: 404 on API endpoints

**Check:**
- Frontend is calling correct URL: `https://growfun-backend.onrender.com/api/...`
- Not calling: `https://growfund-dashboard.onrender.com/api/...`

### Issue: Admin endpoints return 403

**Check:**
- User has `is_staff=True` or `is_superuser=True`
- JWT token is valid and included in Authorization header

## Production Deployment (When Ready)

When you're ready to go to production:

### 1. Set DEBUG=False on Render

```env
DEBUG=False
```

### 2. Set Specific Allowed Hosts

```env
ALLOWED_HOSTS=growfun-backend.onrender.com
```

### 3. Use Production Database

Ensure you're using PostgreSQL, not SQLite:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Use Production Email Service

Consider using SendGrid instead of Gmail:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

### 5. Use Production Korapay Keys

```env
KORAPAY_SECRET_KEY=sk_live_your_live_key
KORAPAY_PUBLIC_KEY=pk_live_your_live_key
```

### 6. Security Checklist

- [ ] DEBUG=False
- [ ] Strong SECRET_KEY
- [ ] HTTPS only
- [ ] Specific ALLOWED_HOSTS
- [ ] Production database
- [ ] Production payment keys
- [ ] Email service configured
- [ ] Error logging set up
- [ ] Backups configured

## API Endpoints Quick Reference

### Authentication
```
POST   https://growfun-backend.onrender.com/api/auth/register/
POST   https://growfun-backend.onrender.com/api/auth/login/
GET    https://growfun-backend.onrender.com/api/auth/verify-email/?token=...
POST   https://growfun-backend.onrender.com/api/auth/resend-verification/
```

### Admin - Deposits
```
GET    https://growfun-backend.onrender.com/api/transactions/admin/deposits/
POST   https://growfun-backend.onrender.com/api/transactions/admin/deposits/{id}/approve/
POST   https://growfun-backend.onrender.com/api/transactions/admin/deposits/{id}/reject/
```

### Admin - Withdrawals
```
GET    https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/
POST   https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/{id}/process/
POST   https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/{id}/complete/
POST   https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/{id}/reject/
```

### Admin - Stats
```
GET    https://growfun-backend.onrender.com/api/transactions/admin/stats/
```

## Support

If you encounter issues:
1. Check Render logs (both frontend and backend)
2. Check browser console for errors
3. Verify environment variables are set
4. Test API endpoints with Postman/cURL first
5. Ensure both services are deployed and running

## You're All Set! 🚀

Your backend now properly supports:
- ✅ Your Render frontend (https://growfund-dashboard.onrender.com)
- ✅ Localhost development (http://localhost:3000)
- ✅ Ngrok URLs (when DEBUG=True)
- ✅ Email verification with correct URLs
- ✅ Admin approval system
- ✅ Complete authentication flow

Deploy and test! 🎉
