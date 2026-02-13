# GrowFund Platform - Quick Start Guide

## ✅ Everything is Ready!

Both servers are running and ready for testing.

---

## Access Points

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:3000 | ✅ Running |
| **Backend API** | http://localhost:8000/api | ✅ Running |
| **Admin Panel** | http://localhost:8000/admin | ✅ Ready |

---

## Test Accounts

### Demo User (Instant Access)
- Click "Continue as Demo User" on login page
- No credentials needed
- Full dashboard access

### Test User (Full Auth Flow)
- Email: `testuser@example.com`
- Password: `TestPass123!`
- Register → Verify Email → Login

### Admin Account
- Email: `admin@growfund.com`
- Password: `Admin123!`
- Access: http://localhost:8000/admin

---

## Quick Test Steps

### 1. Test Demo User (30 seconds)
```
1. Open http://localhost:3000
2. Click "Continue as Demo User"
3. Explore dashboard
```

### 2. Test Full Registration (2 minutes)
```
1. Open http://localhost:3000
2. Click "Go to Login Page"
3. Click "Register"
4. Fill form with:
   - Email: testuser@example.com
   - Password: TestPass123!
   - First Name: John
   - Last Name: Doe
5. Click Register
6. Copy token from Django console
7. Paste token on verification page
8. Login with credentials
```

### 3. Test API Directly (1 minute)
```
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "admin@growfund.com",
  "password": "Admin123!"
}
```

---

## What's Working

### ✅ Authentication
- User registration
- Email verification
- Login with JWT tokens
- Password reset
- Token refresh
- Protected routes

### ✅ User Management
- Profile management
- Settings customization
- Balance tracking
- Referral codes

### ✅ Frontend
- Dashboard
- Profile page
- Settings page
- Notifications
- Crypto trading
- Deposits/Withdrawals
- Admin portal

### ✅ Backend
- 12 API endpoints
- JWT authentication
- Email verification
- Admin panel
- SQLite database

---

## Troubleshooting

### Frontend not loading?
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

### Backend not responding?
```bash
cd backend-growfund
venv\Scripts\Activate.ps1
py manage.py runserver
```

### CORS errors?
- Ensure both servers are running
- Check http://localhost:8000 is accessible

### Token issues?
- Clear browser localStorage
- Login again

---

## Next Steps

After testing authentication:

1. **Test API Endpoints** - See TESTING-GUIDE.md
2. **Create Investment APIs** - Buy/sell crypto
3. **Create Transaction APIs** - Deposits/withdrawals
4. **Create Referral APIs** - Referral tracking
5. **Create Notification APIs** - Real-time updates

---

## Documentation

- **TESTING-GUIDE.md** - Comprehensive testing with API examples
- **SETUP-COMPLETE.md** - Full setup details
- **backend-growfund/BACKEND-SUMMARY.md** - Backend documentation
- **Growfund-Dashboard/trading-dashboard/README.md** - Frontend documentation

---

## Key URLs

```
Frontend:        http://localhost:3000
Backend API:     http://localhost:8000/api
Admin Panel:     http://localhost:8000/admin
Django Shell:    py manage.py shell
```

---

## Commands Reference

### Start Servers
```bash
# Terminal 1 - Backend
cd backend-growfund
venv\Scripts\Activate.ps1
py manage.py runserver

# Terminal 2 - Frontend
cd Growfund-Dashboard/trading-dashboard
npm start
```

### Stop Servers
```
Ctrl+C in each terminal
```

### Database
```bash
cd backend-growfund
venv\Scripts\Activate.ps1
py manage.py shell
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login
- `POST /api/auth/verify-email/` - Verify email
- `POST /api/auth/forgot-password/` - Forgot password
- `POST /api/auth/reset-password/` - Reset password
- `GET /api/auth/me/` - Current user
- `GET /api/auth/profile/` - Get profile
- `PUT /api/auth/profile/` - Update profile
- `GET /api/auth/settings/` - Get settings
- `PUT /api/auth/settings/` - Update settings
- `POST /api/auth/change-password/` - Change password
- `GET /api/auth/balance/` - Get balance

---

## Browser DevTools

### Check Tokens
1. Open DevTools (F12)
2. Go to Application → Local Storage
3. Look for:
   - `access_token` - JWT token
   - `refresh_token` - Refresh token
   - `user` - User data

### Check Network
1. Open DevTools (F12)
2. Go to Network tab
3. Make API calls
4. Check request/response headers and body

### Check Console
1. Open DevTools (F12)
2. Go to Console tab
3. Check for errors or logs

---

## Email Verification

When user registers, Django console shows verification email:

```
Content-Type: text/plain; charset="utf-8"
Subject: Verify your email
From: noreply@growfund.com
To: testuser@example.com

Click the link below to verify your email:
http://localhost:3000/verify?token=550e8400-e29b-41d4-a716-446655440000
```

Copy the token and use it on the verification page.

---

## Success Indicators

✅ Frontend loads at http://localhost:3000
✅ Backend API responds at http://localhost:8000/api
✅ Admin panel accessible at http://localhost:8000/admin
✅ Can register new user
✅ Can verify email
✅ Can login with JWT tokens
✅ Tokens stored in localStorage
✅ Protected routes work
✅ Profile and settings pages load

---

**Ready to test! Open http://localhost:3000 now.**

