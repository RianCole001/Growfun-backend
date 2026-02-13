# Admin Panel 403 Error - Debugging Guide

## Quick Fix

Run this script to fix admin permissions:

```bash
cd backend-growfund
py fix_admin.py
```

This will:
1. Check if admin user exists
2. Create admin if missing
3. Fix permissions if needed
4. Show all users in database

## Step-by-Step Debugging

### Step 1: Check Admin User Exists

```bash
cd backend-growfund
py manage.py shell
```

Then in the Python shell:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Check if admin exists
admin = User.objects.filter(email='admin@growfund.com').first()
if admin:
    print(f"Admin found: {admin.email}")
    print(f"  is_staff: {admin.is_staff}")
    print(f"  is_superuser: {admin.is_superuser}")
    print(f"  is_verified: {admin.is_verified}")
else:
    print("Admin user not found!")

# List all users
print("\nAll users:")
for user in User.objects.all():
    print(f"  {user.email} - staff: {user.is_staff}, superuser: {user.is_superuser}")
```

### Step 2: Fix Admin Permissions

If admin exists but doesn't have permissions:

```python
admin = User.objects.get(email='admin@growfund.com')
admin.is_staff = True
admin.is_superuser = True
admin.is_verified = True
admin.save()
print("Admin permissions updated!")
```

If admin doesn't exist, create it:

```python
User.objects.create_superuser(
    email='admin@growfund.com',
    password='Admin123!',
    first_name='Admin',
    last_name='User'
)
print("Admin created!")
```

### Step 3: Test Admin Login

1. Restart Django server:
   ```bash
   py manage.py runserver
   ```

2. Go to `http://localhost:3000/admin`

3. Login with:
   - Email: `admin@growfund.com`
   - Password: `Admin123!`

4. Check browser console for error messages

### Step 4: Check API Response

Open browser DevTools (F12) and check the Network tab:

1. Go to Admin panel
2. Login
3. Look for request to `http://localhost:8000/api/auth/admin/users/`
4. Check the response:
   - If 403: Admin doesn't have permissions
   - If 401: Token is invalid
   - If 200: Should show users

### Step 5: Verify Token

In browser console:

```javascript
// Check if token is stored
console.log(localStorage.getItem('access_token'));
console.log(localStorage.getItem('admin_user'));

// Parse admin user data
const adminUser = JSON.parse(localStorage.getItem('admin_user'));
console.log('Admin user:', adminUser);
console.log('is_staff:', adminUser.is_staff);
console.log('is_superuser:', adminUser.is_superuser);
```

## Common Issues and Solutions

### Issue 1: Admin User Not Found
**Error**: "Admin user not found!"

**Solution**:
```bash
cd backend-growfund
py manage.py create_admin
```

### Issue 2: Admin Exists But No Permissions
**Error**: 403 Forbidden with message "Admin access required"

**Solution**:
```bash
cd backend-growfund
py fix_admin.py
```

### Issue 3: Token Invalid
**Error**: 401 Unauthorized

**Solution**:
1. Clear browser localStorage: `localStorage.clear()`
2. Logout and login again
3. Check if backend is running

### Issue 4: CORS Error
**Error**: "Access to XMLHttpRequest blocked by CORS policy"

**Solution**:
1. Check Django settings has CORS configured
2. Verify `http://localhost:3000` is in `CORS_ALLOWED_ORIGINS`
3. Restart Django server

### Issue 5: No Users Showing
**Error**: Admin panel loads but shows "No users found"

**Solution**:
1. Register a test user through frontend
2. Verify user was created:
   ```bash
   py manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.count()
   ```
3. Refresh admin panel

## Testing Checklist

- [ ] Admin user exists in database
- [ ] Admin has `is_staff = True`
- [ ] Admin has `is_superuser = True`
- [ ] Admin has `is_verified = True`
- [ ] Django server is running
- [ ] Frontend can login with admin credentials
- [ ] Token is stored in localStorage
- [ ] Token includes `is_staff` and `is_superuser` fields
- [ ] API endpoint returns 200 (not 403)
- [ ] Users list displays in admin panel

## Manual API Testing

### Test with cURL

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@growfund.com","password":"Admin123!"}'

# Response should include tokens and user data with is_staff: true

# 2. Get users (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/admin/users/ \
  -H "Authorization: Bearer TOKEN"

# Should return list of users
```

### Test with Postman

1. Create POST request to `http://localhost:8000/api/auth/login/`
2. Body (JSON):
   ```json
   {
     "email": "admin@growfund.com",
     "password": "Admin123!"
   }
   ```
3. Copy the `access` token from response
4. Create GET request to `http://localhost:8000/api/auth/admin/users/`
5. Add header: `Authorization: Bearer {token}`
6. Send request - should return users list

## Still Having Issues?

1. Check Django logs for errors:
   ```bash
   # Terminal where Django is running
   # Look for error messages
   ```

2. Check browser console for errors:
   - Press F12
   - Go to Console tab
   - Look for red error messages

3. Check Network tab:
   - Press F12
   - Go to Network tab
   - Reload page
   - Look for failed requests (red)
   - Click on failed request to see response

4. Run the fix script:
   ```bash
   cd backend-growfund
   py fix_admin.py
   ```

5. Restart both servers:
   ```bash
   # Terminal 1: Backend
   cd backend-growfund
   py manage.py runserver

   # Terminal 2: Frontend
   cd Growfund-Dashboard/trading-dashboard
   npm start
   ```
