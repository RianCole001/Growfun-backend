# Admin Panel Not Showing Users - Debugging Guide

## Problem
You have 7 users registered, but the admin panel shows no users.

## Root Causes (Check in Order)

### 1. Admin User Not Created or Doesn't Have Permissions

**Check:**
```bash
cd backend-growfund
py verify_admin.py
```

This will show:
- If admin users exist
- If they have `is_staff` and `is_superuser` permissions
- All users in the database

**If admins don't exist or lack permissions:**
```bash
py manage.py shell
```

Then paste:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create/Fix Admin 1
admin1, created = User.objects.get_or_create(
    email='admin001@gmail.com',
    defaults={
        'first_name': 'Admin',
        'last_name': 'One',
        'is_staff': True,
        'is_superuser': True,
        'is_verified': True
    }
)
if not created:
    admin1.is_staff = True
    admin1.is_superuser = True
    admin1.is_verified = True
    admin1.save()
admin1.set_password('Buffers316!')
admin1.save()
print("✓ Admin 1 ready")

# Create/Fix Admin 2
admin2, created = User.objects.get_or_create(
    email='admin@growfund.com',
    defaults={
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True,
        'is_verified': True
    }
)
if not created:
    admin2.is_staff = True
    admin2.is_superuser = True
    admin2.is_verified = True
    admin2.save()
admin2.set_password('Admin123!')
admin2.save()
print("✓ Admin 2 ready")

# Verify
print("\nAll users:")
for user in User.objects.all():
    print(f"  {user.email} - staff: {user.is_staff}, superuser: {user.is_superuser}")
```

Exit shell:
```python
exit()
```

### 2. Admin Not Logged In Correctly

**Check:**
1. Go to `http://localhost:3000/admin`
2. You should see login form
3. Login with:
   - Email: `admin001@gmail.com`
   - Password: `Buffers316!`
4. After login, check browser DevTools (F12):
   - Go to Application → LocalStorage
   - Look for `admin_access_token`
   - Should have a long JWT token

**If token doesn't exist:**
- Restart Django: `py manage.py runserver`
- Try logging in again
- Check browser console for errors (F12 → Console)

### 3. API Endpoint Not Working

**Test the endpoint manually:**

Open browser console (F12) and run:
```javascript
// Get the admin token
const token = localStorage.getItem('admin_access_token');
console.log('Token:', token);

// Make API call
fetch('http://localhost:8000/api/auth/admin/users/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => console.log('Users:', data))
.catch(e => console.error('Error:', e));
```

**Expected response:**
```json
{
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      ...
    }
  ],
  "count": 7
}
```

**If you get 403 Forbidden:**
- Admin doesn't have `is_staff` or `is_superuser` permission
- Run `verify_admin.py` to fix

**If you get 401 Unauthorized:**
- Token is invalid or expired
- Logout and login again

### 4. Django Backend Not Running

**Check:**
```bash
# In the terminal where Django is running, you should see:
Starting development server at http://127.0.0.1:8000/
```

**If not running:**
```bash
cd backend-growfund
py manage.py runserver
```

### 5. Frontend Not Fetching Data

**Check browser console (F12 → Console):**
- Look for red error messages
- Should see network requests to `http://localhost:8000/api/auth/admin/users/`

**If no requests:**
- Admin panel might not be calling the API
- Try refreshing the page
- Check if you're actually logged in as admin

## Step-by-Step Fix

### Step 1: Verify Admin Users Exist
```bash
cd backend-growfund
py verify_admin.py
```

### Step 2: Restart Django
```bash
# Stop Django (Ctrl+C)
# Then restart:
py manage.py runserver
```

### Step 3: Clear Browser Cache
1. Press `Ctrl+Shift+Delete`
2. Select "All time"
3. Check "Cookies and other site data"
4. Click "Clear data"

### Step 4: Logout and Login Again
1. Go to `http://localhost:3000/admin`
2. If logged in, click logout
3. Login with: `admin001@gmail.com` / `Buffers316!`

### Step 5: Check Admin Panel
1. Should see "User Management" page
2. Should see list of 7 users
3. Should see search and filter options

## Troubleshooting Checklist

- [ ] Admin users exist in database
- [ ] Admin users have `is_staff = True`
- [ ] Admin users have `is_superuser = True`
- [ ] Admin users have `is_verified = True`
- [ ] Django server is running
- [ ] Frontend is running
- [ ] Admin is logged in
- [ ] `admin_access_token` exists in localStorage
- [ ] API endpoint returns users (test in console)
- [ ] Browser console shows no errors
- [ ] Network tab shows successful request to `/api/auth/admin/users/`

## Common Issues and Solutions

### Issue: "Admin access required" error
**Solution**: Run `verify_admin.py` to fix permissions

### Issue: 403 Forbidden when calling API
**Solution**: Admin doesn't have staff/superuser permissions

### Issue: 401 Unauthorized when calling API
**Solution**: Token is invalid, logout and login again

### Issue: No users showing but API returns data
**Solution**: Refresh the page or check browser console for errors

### Issue: API returns empty list
**Solution**: Users might not be created, register a test user

## Quick Commands

```bash
# Verify admin setup
cd backend-growfund
py verify_admin.py

# Create admin users
py manage.py create_admin

# Check database
py manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.count()  # Should show 7+
>>> User.objects.filter(is_staff=True).count()  # Should show 2

# Restart Django
py manage.py runserver
```

## Still Not Working?

1. Check Django logs for errors
2. Check browser console (F12) for errors
3. Test API endpoint manually in browser console
4. Verify admin token exists in localStorage
5. Make sure both servers are running (backend + frontend)
