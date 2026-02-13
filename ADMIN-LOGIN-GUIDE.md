# Admin Login Guide

## Current Admin Credentials

You have TWO admin accounts to choose from:

### Admin Account 1 (Primary)
```
Email:    admin001@gmail.com
Password: Buffers316!
```

### Admin Account 2 (Backup)
```
Email:    admin@growfund.com
Password: Admin123!
```

## How to Login

### Step 1: Make Sure Backend is Running
```bash
cd backend-growfund
py manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 2: Make Sure Frontend is Running
In another terminal:
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

You should see the app open at `http://localhost:3000`

### Step 3: Go to Admin Panel
Navigate to: `http://localhost:3000/admin`

### Step 4: Enter Credentials

**Option A - Use Admin 1:**
1. Email field: `admin001@gmail.com`
2. Password field: `Buffers316!`
3. Click "Sign In"

**Option B - Use Admin 2:**
1. Email field: `admin@growfund.com`
2. Password field: `Admin123!`
3. Click "Sign In"

### Step 5: You Should See
- User Management Dashboard
- List of all registered users
- Search and filter options

## If You Get "Invalid Credentials"

### Check 1: Admin Users Exist
```bash
cd backend-growfund
py manage.py shell
```

Then type:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(email__in=['admin001@gmail.com', 'admin@growfund.com']).count())
```

If it shows `0`, the admins don't exist. Create them:

```python
# Create Admin 1
User.objects.create_superuser(
    email='admin001@gmail.com',
    password='Buffers316!',
    first_name='Admin',
    last_name='One'
)

# Create Admin 2
User.objects.create_superuser(
    email='admin@growfund.com',
    password='Admin123!',
    first_name='Admin',
    last_name='User'
)

print("✓ Admins created!")
```

Then exit:
```python
exit()
```

### Check 2: Restart Django
```bash
# Stop Django (Ctrl+C in the terminal where it's running)
# Then restart it:
py manage.py runserver
```

### Check 3: Clear Browser Cache
1. Press `Ctrl+Shift+Delete` (or Cmd+Shift+Delete on Mac)
2. Select "All time"
3. Check "Cookies and other site data"
4. Click "Clear data"
5. Refresh the page

### Check 4: Check Browser Console
1. Press `F12` to open Developer Tools
2. Go to "Console" tab
3. Look for red error messages
4. Take a screenshot and share the error

## Quick Reference

| What | Where |
|------|-------|
| Admin Panel | http://localhost:3000/admin |
| Backend API | http://localhost:8000/api |
| Django Admin | http://localhost:8000/admin |
| Email 1 | admin001@gmail.com |
| Password 1 | Buffers316! |
| Email 2 | admin@growfund.com |
| Password 2 | Admin123! |

## Still Not Working?

1. Make sure BOTH servers are running (backend + frontend)
2. Make sure you're using the EXACT email and password (case-sensitive)
3. Make sure admin users were created in database
4. Clear browser cache and cookies
5. Try a different browser
6. Check browser console for errors (F12)
