# GrowFund Platform - Testing Guide

## Quick Start

### Prerequisites
- Python 3.10+ installed
- Node.js 16+ installed
- Both servers running (see below)

### Starting the Servers

#### 1. Django Backend (Port 8000)

```bash
cd backend-growfund
venv\Scripts\Activate.ps1  # On Windows PowerShell
# or
venv\Scripts\activate.bat  # On Windows CMD

py manage.py runserver
```

Server will be available at: `http://localhost:8000`

#### 2. React Frontend (Port 3000)

```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

Server will be available at: `http://localhost:3000`

---

## Testing the Authentication Flow

### Step 1: Register a New User

1. Open `http://localhost:3000` in your browser
2. Click "Go to Login Page" (or wait for the login gate)
3. Click "Register" link
4. Fill in the registration form:
   - Email: `testuser@example.com`
   - Password: `TestPass123!`
   - Confirm Password: `TestPass123!`
   - First Name: `John`
   - Last Name: `Doe`
5. Click "Register"

**Expected Result:**
- Success message appears
- Redirected to email verification page
- Check Django console for verification token (email backend is console)

### Step 2: Verify Email

1. Copy the verification token from Django console output
2. On the verification page, paste the token
3. Click "Verify Email"

**Expected Result:**
- Success message
- Redirected to login page

### Step 3: Login

1. On login page, enter:
   - Email: `testuser@example.com`
   - Password: `TestPass123!`
2. Click "Login"

**Expected Result:**
- Success message
- Redirected to dashboard
- JWT tokens stored in localStorage
- User data displayed in profile

### Step 4: Verify Tokens in Browser

1. Open browser DevTools (F12)
2. Go to Application → Local Storage
3. Check for:
   - `access_token` - JWT token for API requests
   - `refresh_token` - Token for refreshing access
   - `user` - User data JSON

---

## Testing API Endpoints Directly

### Using Postman or cURL

#### 1. Register User

```bash
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "message": "User registered successfully. Please verify your email.",
  "data": {
    "user": {
      "id": 2,
      "email": "newuser@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "verification_token": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### 2. Verify Email

```bash
POST http://localhost:8000/api/auth/verify-email/
Content-Type: application/json

{
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "message": "Email verified successfully",
  "data": {
    "user": {
      "id": 2,
      "email": "newuser@example.com",
      "is_verified": true
    }
  }
}
```

#### 3. Login

```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "data": {
    "user": {
      "id": 2,
      "email": "newuser@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "balance": "0.00"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

#### 4. Get Current User (Protected Route)

```bash
GET http://localhost:8000/api/auth/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response:**
```json
{
  "message": "User retrieved successfully",
  "data": {
    "id": 2,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "balance": "0.00",
    "is_verified": true
  }
}
```

#### 5. Get User Profile

```bash
GET http://localhost:8000/api/auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### 6. Update User Profile

```bash
PUT http://localhost:8000/api/auth/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "phone": "+1234567890",
  "location": "New York",
  "occupation": "Software Engineer",
  "company": "Tech Corp",
  "bio": "Passionate about investing"
}
```

#### 7. Get User Settings

```bash
GET http://localhost:8000/api/auth/settings/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### 8. Update User Settings

```bash
PUT http://localhost:8000/api/auth/settings/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "theme": "dark",
  "currency": "USD",
  "language": "en",
  "email_notifications": true,
  "two_factor_enabled": false
}
```

#### 9. Change Password

```bash
POST http://localhost:8000/api/auth/change-password/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "old_password": "SecurePass123!",
  "new_password": "NewPass456!",
  "new_password2": "NewPass456!"
}
```

#### 10. Forgot Password

```bash
POST http://localhost:8000/api/auth/forgot-password/
Content-Type: application/json

{
  "email": "newuser@example.com"
}
```

**Response includes reset token in console output**

#### 11. Reset Password

```bash
POST http://localhost:8000/api/auth/reset-password/
Content-Type: application/json

{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "password": "FinalPass789!",
  "password2": "FinalPass789!"
}
```

#### 12. Get User Balance

```bash
GET http://localhost:8000/api/auth/balance/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Testing Admin Panel

### Access Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Login with:
   - Email: `admin@growfund.com`
   - Password: `Admin123!`

### Admin Features

- View all registered users
- View user profiles and settings
- Search and filter users
- Edit user information
- View user balance and referral codes

---

## Testing Token Refresh

### Automatic Token Refresh

The React app automatically refreshes tokens when they expire:

1. Access token lifetime: 60 minutes (default)
2. When token expires, the app automatically requests a new one
3. If refresh fails, user is logged out

### Manual Token Refresh (API)

```bash
POST http://localhost:8000/api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Testing Error Scenarios

### 1. Invalid Email Format

```bash
POST http://localhost:8000/api/auth/register/
{
  "email": "invalid-email",
  "password": "Pass123!",
  "password2": "Pass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Expected:** 400 Bad Request with validation error

### 2. Password Too Short

```bash
POST http://localhost:8000/api/auth/register/
{
  "email": "test@example.com",
  "password": "123",
  "password2": "123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Expected:** 400 Bad Request with password validation error

### 3. Duplicate Email

Register twice with same email

**Expected:** 400 Bad Request - "User with this email already exists"

### 4. Invalid Credentials

```bash
POST http://localhost:8000/api/auth/login/
{
  "email": "test@example.com",
  "password": "WrongPassword123!"
}
```

**Expected:** 401 Unauthorized - "Invalid credentials"

### 5. Unverified Email Login

Register but don't verify email, then try to login

**Expected:** 403 Forbidden - "Email not verified"

### 6. Missing Authorization Header

```bash
GET http://localhost:8000/api/auth/me/
```

**Expected:** 401 Unauthorized - "Authentication credentials were not provided"

### 7. Invalid Token

```bash
GET http://localhost:8000/api/auth/me/
Authorization: Bearer invalid-token-here
```

**Expected:** 401 Unauthorized - "Token is invalid or expired"

---

## Testing with React Frontend

### Demo User Login

1. Open `http://localhost:3000`
2. Click "Continue as Demo User" (green button)
3. Instant access to dashboard without authentication

### Full Authentication Flow

1. Click "Go to Login Page"
2. Click "Register"
3. Fill registration form
4. Verify email (copy token from Django console)
5. Login with credentials
6. Access dashboard features

### Testing Protected Routes

1. Login successfully
2. Try accessing `/app` - should work
3. Logout
4. Try accessing `/app` - should redirect to login

---

## Checking Django Console Output

### Email Verification Token

When user registers, Django console shows:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Verify your email
From: noreply@growfund.com
To: testuser@example.com
Date: Wed, 11 Feb 2026 01:55:43 -0000
Message-ID: <...>

Click the link below to verify your email:
http://localhost:3000/verify?token=550e8400-e29b-41d4-a716-446655440000
```

### Password Reset Token

Similar format with reset link

---

## Database Inspection

### View Database with Django Shell

```bash
py manage.py shell
```

```python
from accounts.models import User, UserSettings

# View all users
users = User.objects.all()
for user in users:
    print(f"{user.email} - Verified: {user.is_verified}")

# View specific user
user = User.objects.get(email='testuser@example.com')
print(user.get_full_name())
print(user.balance)
print(user.referral_code)

# View user settings
settings = user.settings
print(settings.theme)
print(settings.email_notifications)
```

---

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
cd backend-growfund
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "CORS error" in React console

**Solution:**
- Ensure Django server is running on port 8000
- Check CORS_ALLOWED_ORIGINS in settings.py includes `http://localhost:3000`

### Issue: "Token is invalid or expired"

**Solution:**
- Clear localStorage and login again
- Check token expiration time in settings.py

### Issue: Email not being sent

**Solution:**
- Email backend is set to console for testing
- Check Django console output for email content
- To use real email, update EMAIL_BACKEND in .env

### Issue: "User with this email already exists"

**Solution:**
- Use a different email address
- Or delete user from admin panel and try again

---

## Next Steps

After successful testing:

1. **Create Investment APIs** - Buy/sell crypto and real estate
2. **Create Transaction APIs** - Deposits and withdrawals
3. **Create Referral APIs** - Referral tracking and bonuses
4. **Create Notification APIs** - Real-time notifications
5. **Create Admin APIs** - Deposit/withdrawal approvals

---

## Support

For issues:
1. Check Django console for error messages
2. Check React console (F12) for frontend errors
3. Review API response in Network tab
4. Check database with Django shell

