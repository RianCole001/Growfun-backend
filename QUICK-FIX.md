# Quick Fix for Admin 403 Error

## The Problem
You're getting a 403 Forbidden error when trying to access the admin users list.

## The Solution (3 Steps)

### Step 1: Create Admin Users
```bash
cd backend-growfund
py fix_admin.py
```

This script will:
- Create both admin users if missing
- Fix permissions if needed
- Show all users in database

### Step 2: Restart Django
```bash
cd backend-growfund
py manage.py runserver
```

### Step 3: Test Admin Panel
1. Go to `http://localhost:3000/admin`
2. Login with either:
   - **Admin 1**: admin001@gmail.com / Buffers316!
   - **Admin 2**: admin@growfund.com / Admin123!
3. You should now see the users list

## Admin Credentials

| Admin | Email | Password |
|-------|-------|----------|
| Admin 1 | admin001@gmail.com | Buffers316! |
| Admin 2 | admin@growfund.com | Admin123! |

## If Still Not Working

Run this to check what's wrong:

```bash
cd backend-growfund
py manage.py shell
```

Then paste this:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Check both admins
for email in ['admin001@gmail.com', 'admin@growfund.com']:
    admin = User.objects.get(email=email)
    print(f"{email}:")
    print(f"  is_staff: {admin.is_staff}")
    print(f"  is_superuser: {admin.is_superuser}")
    print(f"  is_verified: {admin.is_verified}")
```

If any are `False`, run:

```python
for email in ['admin001@gmail.com', 'admin@growfund.com']:
    admin = User.objects.get(email=email)
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_verified = True
    admin.save()
print("Fixed!")
```

Then exit shell (Ctrl+D) and restart Django.

## What Changed

- Backend now creates 2 admin users
- Admin endpoint checks permissions
- Frontend shows both admin credentials
- Created `fix_admin.py` script to easily set up admins

## Files Modified

**Backend:**
- `accounts/management/commands/create_admin.py` - Creates 2 admins
- `accounts/views.py` - Updated admin endpoint
- `accounts/serializers.py` - Added is_staff/is_superuser fields
- `fix_admin.py` - Quick fix script

**Frontend:**
- `AdminApp.js` - Shows both admin credentials
- `AdminUsers.js` - Shows error messages
