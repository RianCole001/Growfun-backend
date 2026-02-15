# Frontend-Backend Connection Guide

## What Was Fixed

✅ Enabled `APPEND_SLASH = True` - Now `/admin` redirects to `/admin/`
✅ Added `http://127.0.0.1:3000` and `http://127.0.0.1:3001` to CORS
✅ Added Render backend URL to CSRF trusted origins
✅ Configured CORS to allow credentials

## Backend URLs

### Production (Render)
```
https://growfun-backend.onrender.com
```

### Admin Panel
```
https://growfun-backend.onrender.com/admin/
```
Note: Must include trailing slash or it will redirect

### API Base URL
```
https://growfun-backend.onrender.com/api/
```

## Frontend Configuration

### React App (.env or config file)

```env
REACT_APP_API_URL=https://growfun-backend.onrender.com/api
```

Or for local development:
```env
REACT_APP_API_URL=http://localhost:8000/api
```

### Example API Calls

#### Login
```javascript
const response = await fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include', // Important for cookies
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
const accessToken = data.access;
```

#### Authenticated Request
```javascript
const response = await fetch('https://growfun-backend.onrender.com/api/investments/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  credentials: 'include'
});

const investments = await response.json();
```

## Available API Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update profile
- `POST /api/token/refresh/` - Refresh JWT token

### Investments (`/api/investments/`)
- `GET /api/investments/` - List investments
- `POST /api/investments/` - Create investment
- `GET /api/investments/{id}/` - Get investment details
- `GET /api/investments/plans/` - Get investment plans

### Transactions (`/api/transactions/`)
- `GET /api/transactions/` - List transactions
- `POST /api/transactions/korapay/deposit/` - Deposit via Korapay
- `POST /api/transactions/korapay/withdrawal/bank/` - Withdraw to bank
- `POST /api/transactions/korapay/withdrawal/mobile/` - Withdraw to mobile money
- `POST /api/transactions/korapay/verify/` - Verify transaction
- `GET /api/transactions/korapay/banks/` - Get supported banks

### Referrals (`/api/referrals/`)
- `GET /api/referrals/` - Get referral info

### Notifications (`/api/notifications/`)
- `GET /api/notifications/` - List notifications

## Testing Connection

### From Browser Console
```javascript
// Test if backend is accessible
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'OPTIONS'
})
.then(response => console.log('CORS OK:', response.status))
.catch(error => console.error('CORS Error:', error));
```

### From React App
```javascript
// In your React component
useEffect(() => {
  fetch('https://growfun-backend.onrender.com/api/investments/')
    .then(res => res.json())
    .then(data => console.log('Backend connected:', data))
    .catch(err => console.error('Connection error:', err));
}, []);
```

## Common Issues & Solutions

### Issue: CORS Error
**Error:** "Access to fetch has been blocked by CORS policy"

**Solution:** 
- Make sure your frontend URL is in `CORS_ALLOWED_ORIGINS`
- Include `credentials: 'include'` in fetch requests
- Backend changes have been applied, redeploy to Render

### Issue: 404 on /admin
**Error:** "Page not found (404)"

**Solution:** 
- Use `/admin/` with trailing slash
- Or let Django redirect automatically (now enabled)

### Issue: 401 Unauthorized
**Error:** "Authentication credentials were not provided"

**Solution:**
```javascript
// Make sure to include Authorization header
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

### Issue: Token Expired
**Error:** "Token is invalid or expired"

**Solution:**
```javascript
// Refresh the token
const refreshToken = localStorage.getItem('refreshToken');
const response = await fetch('https://growfun-backend.onrender.com/api/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
});
const { access } = await response.json();
localStorage.setItem('accessToken', access);
```

## Deployment Checklist

### Backend (Render)
- [ ] Deploy updated settings.py
- [ ] Set environment variables in Render dashboard
- [ ] Verify ALLOWED_HOSTS includes your domain
- [ ] Check logs for any errors

### Frontend (localhost:3000)
- [ ] Update API URL to point to Render backend
- [ ] Test login/register
- [ ] Test authenticated requests
- [ ] Check browser console for CORS errors

## Local Development

### Run Backend Locally
```bash
cd backend-growfund
python manage.py runserver
```
Backend will be at: `http://localhost:8000`

### Run Frontend Locally
```bash
cd frontend
npm start
```
Frontend will be at: `http://localhost:3000`

### Update Frontend API URL
```env
# For local backend
REACT_APP_API_URL=http://localhost:8000/api

# For production backend
REACT_APP_API_URL=https://growfun-backend.onrender.com/api
```

## Next Steps

1. Redeploy your backend to Render with the updated settings
2. Update your React app's API URL configuration
3. Test the connection from localhost:3000
4. Check browser console for any errors

## Support

If you encounter issues:
1. Check browser console for errors
2. Check Render logs for backend errors
3. Verify CORS settings are correct
4. Test with curl or Postman first
