# Fix: Invalid Credentials Error

## The Issue
You're getting "Invalid credentials" when trying to login to the admin panel.

## The Root Cause
The admin users haven't been created in the database yet.

## The Fix (Follow These Steps Exactly)

### Step 1: Open Command Prompt/Terminal

Navigate to the backend folder:
```bash
cd backend-growfund
```

### Step 2: Open Django Shell

```bash
py manage.py shell
```

You should see:
```
Python 3.x.x ...
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>>
```

### Step 3: Create Admin Users

Copy and paste this ENTIRE block into the shell:

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create Admin 1
try:
    admin1 = User.objects.get(email='admin001@gmail.com')
    admin1.is_staff = True
    admin1.is_superuser = True
    admin1.is_verified = True
    admin1.set_password('Buffers316!')
    admin1.save()
    print("✓ Admin 1 updated")
except User.DoesNotExist:
    admin1 = User.objects.create_superuser(
        email='admin001@gmail.com',
        password='Buffers316!',
        first_name='Admin',
        last_name='One'
    )
    print("✓ Admin 1 created")

# Create Admin 2
try:
    admin2 = User.objects.get(email='admin@growfund.com')
    admin2.is_staff = True
    admin2.is_superuser = True
    admin2.is_verified = True
    admin2.set_password('Admin123!')
    admin2.save()
    print("✓ Admin 2 updated")
except User.DoesNotExist:
    admin2 = User.objects.create_superuser(
        email='admin@growfund.com',
        password='Admin123!',
        first_name='Admin',
        last_name='User'
    )
    print("✓ Admin 2 created")

print("\n✓ Admin users ready!")
print("Admin 1: admin001@gmail.com / Buffers316!")
print("Admin 2: admin@growfund.com / Admin123!")
```

### Step 4: Exit Django Shell

Type:
```python
exit()
```

### Step 5: Restart Django Server

```bash
py manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 6: Go to Admin Panel

Open browser and go to:
```
http://localhost:3000/admin
```

### Step 7: Login

Use either credential:

**Option 1:**
- Email: `admin001@gmail.com`
- Password: `Buffers316!`

**Option 2:**
- Email: `admin@growfund.com`
- Password: `Admin123!`

Click "Sign In"

## Expected Result

You should see:
- ✓ Admin dashboard loads
- ✓ User management page shows
- ✓ List of registered users displays

## If Still Not Working

### Verify Admins Were Created

```bash
py manage.py shell
```

Then type:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Check if admins exist
for email in ['admin001@gmail.com', 'admin@growfund.com']:
    try:
        user = User.objects.get(email=email)
        print(f"✓ {email} exists")
        print(f"  is_staff: {user.is_staff}")
        print(f"  is_superuser: {user.is_superuser}")
        print(f"  is_verified: {user.is_verified}")
    except:
        print(f"✗ {email} NOT FOUND")
```

If you see "NOT FOUND", run Step 3 again.

### Check Backend is Running

Make sure you see this in the terminal:
```
Starting development server at http://127.0.0.1:8000/
```

If not, run:
```bash
py manage.py runserver
```

### Check Frontend is Running

Make sure you can access:
```
http://localhost:3000
```

If not, in another terminal run:
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

### Clear Browser Cache

1. Press `Ctrl+Shift+Delete`
2. Select "All time"
3. Check "Cookies and other site data"
4. Click "Clear data"
5. Go back to `http://localhost:3000/admin`

## Admin Credentials Summary

| Admin | Email | Password |
|-------|-------|----------|
| Admin 1 | admin001@gmail.com | Buffers316! |
| Admin 2 | admin@growfund.com | Admin123! |

Both accounts have full admin access.

## Need Help?

1. Make sure you followed ALL steps above
2. Make sure both servers are running (backend + frontend)
3. Make sure you're using the EXACT email and password
4. Check browser console for errors (F12)
5. Try a different browser
