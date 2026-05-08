# Create Admin User - Quick Guide

## 🚨 Issue Fixed

The `create_admin` command was trying to use a `username` field that doesn't exist in your User model. Your model uses `email` as the unique identifier.

**Status**: ✅ FIXED

---

## 🚀 Quick Solutions (Choose One)

### Option 1: Create Tabby Admin (Fastest) ⚡

Run this script to instantly create your Tabby admin:

```bash
cd backend-growfund
python create_tabby_admin.py
```

**Default Credentials**:
- Email: `Tabby@gmail.com`
- Password: `Tabby123!`

**Note**: Edit `create_tabby_admin.py` to change the password before running.

---

### Option 2: Use Existing Admins

Two admin accounts already exist:

**Admin 1**:
- Email: `admin001@gmail.com`
- Password: `Buffers316!`

**Admin 2**:
- Email: `admin@growfund.com`
- Password: `Admin123!`

To verify/fix them:
```bash
cd backend-growfund
python fix_admin.py
```

---

### Option 3: Use Fixed create_admin Command

The command has been fixed. Now use it like this:

```bash
cd backend-growfund
python manage.py create_admin
```

**It will ask for**:
- Admin email (e.g., `Tabby@gmail.com`)
- First name (optional, default: "Admin")
- Last name (optional, default: "User")
- Password (hidden input)
- Password confirmation

**No more username prompt!** ✅

---

### Option 4: Django Shell (Manual)

```bash
cd backend-growfund
python manage.py shell
```

Then run:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create admin
admin = User.objects.create_superuser(
    email='Tabby@gmail.com',
    password='Tabby123!',
    first_name='Tabby',
    last_name='Admin'
)

print(f"Created: {admin.email}")
print(f"Staff: {admin.is_staff}")
print(f"Superuser: {admin.is_superuser}")
```

---

## 🔍 What Was Wrong?

### Before (Broken):
```python
# ❌ This failed because User model has no username field
if User.objects.filter(username=username).exists():
    ...

admin_user = User.objects.create_user(
    username=username,  # ❌ Field doesn't exist
    email=email,
    ...
)
```

### After (Fixed):
```python
# ✅ Only check email (the actual unique field)
if User.objects.filter(email=email).exists():
    ...

admin_user = User.objects.create_user(
    email=email,  # ✅ Correct field
    password=password,
    ...
)
```

---

## 📋 Your User Model Fields

Your custom User model has these fields:
- ✅ `email` (unique identifier, replaces username)
- ✅ `first_name`
- ✅ `last_name`
- ✅ `password`
- ✅ `is_staff`
- ✅ `is_superuser`
- ✅ `is_verified`
- ✅ `balance`
- ❌ `username` (explicitly set to None)

---

## ✅ Verification Steps

After creating admin, verify it works:

### 1. Check in Database
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Find your admin
admin = User.objects.get(email='Tabby@gmail.com')
print(f"Email: {admin.email}")
print(f"Staff: {admin.is_staff}")
print(f"Superuser: {admin.is_superuser}")
print(f"Verified: {admin.is_verified}")
```

### 2. Test Login API
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Tabby@gmail.com",
    "password": "Tabby123!"
  }'
```

Should return JWT tokens.

### 3. Test Admin Access
```bash
# Get token from login response, then:
curl -X GET http://localhost:8000/api/auth/admin/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Should return list of users.

---

## 🎯 Recommended Approach

**For you right now**:

1. Run the quick script:
   ```bash
   cd backend-growfund
   python create_tabby_admin.py
   ```

2. Login with:
   - Email: `Tabby@gmail.com`
   - Password: `Tabby123!`

3. Done! ✅

---

## 🔒 Security Notes

- Change default passwords in production
- Use strong passwords (min 8 characters)
- Passwords are hashed in database
- JWT tokens expire after 60 minutes
- Admin access requires `is_staff=True` or `is_superuser=True`

---

## 📝 Files Modified

1. ✅ `backend-growfund/accounts/management/commands/create_admin.py` - Fixed to remove username
2. ✅ `backend-growfund/create_tabby_admin.py` - New quick script for Tabby
3. ✅ `backend-growfund/fix_admin.py` - Already correct (no changes needed)

---

## 🐛 Troubleshooting

**Error: "User with email already exists"**
- User already created, just login with existing credentials
- Or run `python fix_admin.py` to reset permissions

**Error: "Cannot resolve keyword 'username'"**
- You're using old code that references username
- Use the fixed version from this guide

**Error: "No module named django"**
- Activate virtual environment first
- Or install Django: `pip install django`

**Can't login to admin panel**
- Verify user exists: `python manage.py shell` → check User.objects.all()
- Verify is_staff=True: Check user permissions
- Check password: Reset with `user.set_password('newpass')` then `user.save()`

---

## 🎉 Success Indicators

You'll know it worked when:
✅ Script prints "Admin user created successfully!"
✅ Login API returns JWT tokens
✅ Admin endpoints return data (not 403 Forbidden)
✅ Frontend admin panel loads user list

---

**Quick Start**: Run `python create_tabby_admin.py` now! 🚀
