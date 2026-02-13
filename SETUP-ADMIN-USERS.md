# How to Setup Admin Users

## The Problem
You're getting "invalid credentials" when trying to login to the admin panel because the admin users haven't been created in the database yet.

## Solution: Create Admin Users

### Method 1: Using Django Shell (Recommended)

**Step 1: Open Django Shell**
```bash
cd backend-growfund
py manage.py shell
```

**Step 2: Paste this code:**
```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create Admin 1
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
if created:
    admin1.set_password('Buffers316!')
    admin1.save()
    print("✓ Admin 1 created: admin001@gmail.com / Buffers316!")
else:
    # Update existing admin
    admin1.is_staff = True
    admin1.is_superuser = True
    admin1.is_verified = True
    admin1.set_password('Buffers316!')
    admin1.save()
    print("✓ Admin 1 updated: admin001@gmail.com / Buffers316!")

# Create Admin 2
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
if created:
    admin2.set_password('Admin123!')
    admin2.save()
    print("✓ Admin 2 created: admin@growfund.com / Admin123!")
else:
    # Update existing admin
    admin2.is_staff = True
    admin2.is_superuser = True
    admin2.is_verified = True
    admin2.set_password('Admin123!')
    admin2.save()
    print("✓ Admin 2 updated: admin@growfund.com / Admin123!")

# Verify
print("\n--- Verification ---")
for email in ['admin001@gmail.com', 'admin@growfund.com']:
    user = User.objects.get(email=email)
    print(f"{email}:")
    print(f"  is_staff: {user.is_staff}")
    print(f"  is_superuser: {user.is_superuser}")
    print(f"  is_verified: {user.is_verified}")
```

**Step 3: Exit shell**
```
exit()
```

### Method 2: Using Management Command

```bash
cd backend-growfund
py manage.py create_admin
```

### Method 3: Using Python Script

```bash
cd backend-growfund
py manage.py shell < setup_admins.py
```

## After Setup

### Step 1: Restart Django
```bash
cd backend-growfund
py manage.py runserver
```

### Step 2: Go to Admin Panel
```
http://localhost:3000/admin
```

### Step 3: Login with Either Credential

**Option 1:**
- Email: `admin001@gmail.com`
- Password: `Buffers316!`

**Option 2:**
- Email: `admin@growfund.com`
- Password: `Admin123!`

## Verify Admin Users Were Created

```bash
cd backend-growfund
py manage.py shell
```

Then run:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Check if admins exist
print("Total users:", User.objects.count())
print("\nAdmin users:")
for user in User.objects.filter(is_staff=True):
    print(f"  {user.email} - superuser: {user.is_superuser}, verified: {user.is_verified}")
```

## If Still Getting Invalid Credentials

1. Make sure you're using the exact email and password:
   - `admin001@gmail.com` / `Buffers316!`
   - `admin@growfund.com` / `Admin123!`

2. Check that Django is running:
   ```bash
   py manage.py runserver
   ```

3. Check browser console for error messages (F12)

4. Try clearing browser cache:
   - Press Ctrl+Shift+Delete
   - Clear all data
   - Refresh page

5. Verify admin was created:
   ```bash
   py manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.filter(email='admin001@gmail.com').exists()
   # Should return True
   ```

## Admin Credentials Reference

| Admin | Email | Password |
|-------|-------|----------|
| Admin 1 | admin001@gmail.com | Buffers316! |
| Admin 2 | admin@growfund.com | Admin123! |

Both have:
- ✓ Staff permissions
- ✓ Superuser permissions
- ✓ Email verified
- ✓ Full admin access
