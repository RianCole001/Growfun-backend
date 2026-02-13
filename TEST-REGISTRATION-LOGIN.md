# GrowFund Platform - Test Registration & Login Flow

## Complete Step-by-Step Testing Guide

This guide walks you through testing the complete authentication flow from registration to dashboard access.

---

## Prerequisites

✅ Django backend running on http://localhost:8000
✅ React frontend running on http://localhost:3000
✅ Both servers compiled without errors

---

## Test Scenario 1: Demo User (Fastest)

### Time: 30 seconds

1. **Open Frontend**
   - Go to http://localhost:3000
   - You should see the login gate

2. **Click Demo User Button**
   - Look for green button "Continue as Demo User"
   - Click it

3. **Instant Access**
   - Dashboard loads immediately
   - No authentication needed
   - Full access to all features

4. **Verify Demo Access**
   - Check localStorage: `localStorage.getItem('user')`
   - Should show demo user data
   - Profile shows "Demo User"

---

## Test Scenario 2: Full Registration Flow

### Time: 2-3 minutes

### Step 1: Navigate to Registration

1. Open http://localhost:3000
2. Click "Go to Login Page" button
3. On login page, click "Register" link
4. You should see registration form

### Step 2: Fill Registration Form

Fill in the following:
```
Email:           testuser@example.com
Password:        TestPass123!
Confirm Password: TestPass123!
First Name:      John
Last Name:       Doe
```

**Important:**
- Password must be at least 8 characters
- Must contain uppercase, lowercase, number, special character
- Email must be valid format

### Step 3: Submit Registration

1. Click "Register" button
2. Wait for response (should be ~1-2 seconds)
3. You should see success message: "Registration successful"

**What happens in backend:**
- User created in database
- Verification token generated
- Verification email sent to console
- User redirected to verification page

### Step 4: Verify Email

1. **Get Verification Token**
   - Look at Django console output
   - Find email content with verification token
   - Example token: `550e8400-e29b-41d4-a716-446655440000`

2. **Copy Token**
   - Select and copy the token from console
   - Or look for verification link in email output

3. **Paste Token on Verification Page**
   - On verification page, paste token in input field
   - Click "Verify Email" button

4. **Verify Success**
   - Should see: "Email verified successfully"
   - Redirected to login page

**What happens in backend:**
- User marked as verified
- Verification token cleared
- User can now login

### Step 5: Login

1. **Enter Credentials**
   - Email: `testuser@example.com`
   - Password: `TestPass123!`

2. **Click Login**
   - Wait for response (~1-2 seconds)
   - Should see: "Login successful"

3. **Check Tokens**
   - Open DevTools (F12)
   - Go to Application → Local Storage
   - Verify these keys exist:
     - `access_token` - JWT token
     - `refresh_token` - Refresh token
     - `user` - User data JSON

**What happens in backend:**
- Credentials validated
- JWT tokens generated
- User data returned
- last_login_at updated

### Step 6: Access Dashboard

1. **Dashboard Loads**
   - Should see main dashboard
   - Profile shows "John Doe"
   - Balance shows $0.00

2. **Verify Authentication**
   - Click Profile icon
   - Should show user details
   - Click Settings
   - Should load settings page

3. **Test Protected Routes**
   - Try accessing different pages
   - All should load without redirect
   - Logout button should be visible

### Step 7: Logout

1. **Click Logout**
   - Find logout button (usually in profile menu)
   - Click it

2. **Verify Redirect**
   - Should redirect to login gate
   - localStorage should be cleared
   - Tokens should be removed

---

## Test Scenario 3: API Testing

### Time: 1 minute

### Using Postman

#### 1. Register User

```
Method: POST
URL: http://localhost:8000/api/auth/register/
Headers:
  Content-Type: application/json

Body:
{
  "email": "apitest@example.com",
  "password": "ApiTest123!",
  "password2": "ApiTest123!",
  "first_name": "API",
  "last_name": "Test"
}
```

**Expected Response (201):**
```json
{
  "message": "User registered successfully. Please verify your email.",
  "data": {
    "user": {
      "id": 3,
      "email": "apitest@example.com",
      "first_name": "API",
      "last_name": "Test"
    },
    "verification_token": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### 2. Verify Email

```
Method: POST
URL: http://localhost:8000/api/auth/verify-email/
Headers:
  Content-Type: application/json

Body:
{
  "token": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Expected Response (200):**
```json
{
  "message": "Email verified successfully",
  "data": {
    "user": {
      "id": 3,
      "email": "apitest@example.com",
      "is_verified": true
    }
  }
}
```

#### 3. Login

```
Method: POST
URL: http://localhost:8000/api/auth/login/
Headers:
  Content-Type: application/json

Body:
{
  "email": "apitest@example.com",
  "password": "ApiTest123!"
}
```

**Expected Response (200):**
```json
{
  "message": "Login successful",
  "data": {
    "user": {
      "id": 3,
      "email": "apitest@example.com",
      "first_name": "API",
      "last_name": "Test",
      "balance": "0.00",
      "is_verified": true
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

#### 4. Get Current User (Protected)

```
Method: GET
URL: http://localhost:8000/api/auth/me/
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  Content-Type: application/json
```

**Expected Response (200):**
```json
{
  "message": "User retrieved successfully",
  "data": {
    "id": 3,
    "email": "apitest@example.com",
    "first_name": "API",
    "last_name": "Test",
    "balance": "0.00",
    "is_verified": true
  }
}
```

#### 5. Update Profile

```
Method: PUT
URL: http://localhost:8000/api/auth/profile/
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  Content-Type: application/json

Body:
{
  "phone": "+1234567890",
  "location": "New York",
  "occupation": "Software Engineer",
  "company": "Tech Corp",
  "bio": "Testing the API"
}
```

**Expected Response (200):**
```json
{
  "message": "Profile updated successfully",
  "data": {
    "id": 3,
    "email": "apitest@example.com",
    "phone": "+1234567890",
    "location": "New York",
    "occupation": "Software Engineer",
    "company": "Tech Corp",
    "bio": "Testing the API"
  }
}
```

---

## Test Scenario 4: Error Handling

### Test Invalid Credentials

```
Method: POST
URL: http://localhost:8000/api/auth/login/
Body:
{
  "email": "testuser@example.com",
  "password": "WrongPassword123!"
}
```

**Expected Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

### Test Unverified Email

1. Register user but don't verify email
2. Try to login

**Expected Response (403):**
```json
{
  "error": "Email not verified. Please verify your email first."
}
```

### Test Duplicate Email

1. Register with `testuser@example.com`
2. Try to register again with same email

**Expected Response (400):**
```json
{
  "email": ["User with this email already exists"]
}
```

### Test Missing Authorization

```
Method: GET
URL: http://localhost:8000/api/auth/me/
(No Authorization header)
```

**Expected Response (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Test Invalid Token

```
Method: GET
URL: http://localhost:8000/api/auth/me/
Headers:
  Authorization: Bearer invalid-token-here
```

**Expected Response (401):**
```json
{
  "detail": "Token is invalid or expired"
}
```

---

## Test Scenario 5: Admin Panel

### Access Admin Panel

1. Go to http://localhost:8000/admin/
2. Login with:
   - Email: `admin@growfund.com`
   - Password: `Admin123!`

### Verify Admin Features

1. **Users Section**
   - Click "Users" in left sidebar
   - Should see all registered users
   - Can search by email
   - Can view user details

2. **User Settings Section**
   - Click "User Settings"
   - Should see settings for each user
   - Can view notification preferences
   - Can view security settings

3. **Search Users**
   - Use search box to find users
   - Filter by email
   - View user details

---

## Verification Checklist

### Registration
- [ ] Form validates email format
- [ ] Form validates password strength
- [ ] Success message appears
- [ ] Verification token generated
- [ ] Email sent to console
- [ ] User created in database

### Email Verification
- [ ] Token copied from console
- [ ] Token pasted on verification page
- [ ] Success message appears
- [ ] User marked as verified
- [ ] Redirected to login page

### Login
- [ ] Credentials accepted
- [ ] Success message appears
- [ ] Tokens generated
- [ ] Tokens stored in localStorage
- [ ] Redirected to dashboard

### Dashboard
- [ ] Dashboard loads
- [ ] User profile displays
- [ ] All pages accessible
- [ ] Protected routes work
- [ ] Logout works

### API
- [ ] Register endpoint works
- [ ] Verify email endpoint works
- [ ] Login endpoint works
- [ ] Protected endpoints work
- [ ] Error handling works

### Admin Panel
- [ ] Admin login works
- [ ] Users visible
- [ ] Can search users
- [ ] Can view user details
- [ ] Settings visible

---

## Common Issues & Solutions

### Issue: "Email already exists"
**Solution:** Use a different email address or delete user from admin panel

### Issue: "Invalid verification token"
**Solution:** Copy token again from Django console, make sure it's complete

### Issue: "Email not verified"
**Solution:** Complete email verification step before login

### Issue: "Invalid credentials"
**Solution:** Check email and password are correct, case-sensitive

### Issue: "CORS error"
**Solution:** Ensure Django running on port 8000, React on port 3000

### Issue: "Token is invalid or expired"
**Solution:** Clear localStorage and login again

### Issue: "Cannot read properties of undefined"
**Solution:** Check browser console for errors, refresh page

---

## Performance Expectations

| Operation | Expected Time |
|-----------|----------------|
| Register | 1-2 seconds |
| Verify Email | 1-2 seconds |
| Login | 1-2 seconds |
| Get User | 0.5-1 second |
| Update Profile | 1-2 seconds |
| Logout | Instant |

---

## Database Verification

### Check User Created

```bash
cd backend-growfund
venv\Scripts\Activate.ps1
py manage.py shell
```

```python
from accounts.models import User

# View all users
users = User.objects.all()
for user in users:
    print(f"{user.email} - Verified: {user.is_verified}")

# View specific user
user = User.objects.get(email='testuser@example.com')
print(f"Name: {user.get_full_name()}")
print(f"Balance: {user.balance}")
print(f"Referral Code: {user.referral_code}")
print(f"Created: {user.created_at}")
```

---

## Browser DevTools Inspection

### Check Tokens

1. Open DevTools (F12)
2. Go to Application tab
3. Click Local Storage
4. Click http://localhost:3000
5. Look for:
   - `access_token` - Should be JWT format
   - `refresh_token` - Should be JWT format
   - `user` - Should be JSON object

### Check Network Requests

1. Open DevTools (F12)
2. Go to Network tab
3. Make API call (login, register, etc.)
4. Click request in list
5. Check:
   - Request headers (Authorization, Content-Type)
   - Request body (email, password)
   - Response status (200, 201, 400, 401)
   - Response body (tokens, user data, errors)

### Check Console

1. Open DevTools (F12)
2. Go to Console tab
3. Check for:
   - Errors (red)
   - Warnings (yellow)
   - Logs (blue)

---

## Success Indicators

✅ Registration form submits successfully
✅ Verification token appears in Django console
✅ Email verification succeeds
✅ Login succeeds with correct credentials
✅ Tokens stored in localStorage
✅ Dashboard loads after login
✅ Protected routes accessible
✅ Logout clears tokens
✅ Admin panel accessible
✅ Users visible in admin panel

---

## Next Steps After Testing

1. **Test Investment APIs** - Create investment endpoints
2. **Test Transaction APIs** - Create deposit/withdrawal endpoints
3. **Test Referral APIs** - Create referral tracking
4. **Test Notification APIs** - Create notification system
5. **Test Admin APIs** - Create admin approval system

---

## Support

For detailed API documentation, see **TESTING-GUIDE.md**

For quick reference, see **QUICK-START.md**

For setup details, see **SETUP-COMPLETE.md**

