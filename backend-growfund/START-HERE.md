# 🚀 Quick Start Guide - Run in 5 Minutes!

## Step 1: Install Django (Run this in PowerShell)

```powershell
py -m pip install Django djangorestframework django-cors-headers djangorestframework-simplejwt python-decouple Pillow
```

Wait for installation to complete (may take 2-5 minutes).

## Step 2: Run Migrations

```powershell
py manage.py makemigrations
py manage.py migrate
```

## Step 3: Create Admin User

```powershell
py manage.py createsuperuser
```

Enter:
- Email: `admin@growfund.com`
- Password: (your choice, e.g., `Admin123!`)

## Step 4: Start Server

```powershell
py manage.py runserver
```

Server will start at: **http://localhost:8000**

## Step 5: Test API

Open browser or Postman:
- Admin Panel: http://localhost:8000/admin/
- API Root: http://localhost:8000/api/

---

## Test User Registration

### Using PowerShell (curl):
```powershell
curl -X POST http://localhost:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"Test123!\",\"password2\":\"Test123!\",\"first_name\":\"John\",\"last_name\":\"Doe\"}'
```

### Using Browser/Postman:
```
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Test123!",
  "password2": "Test123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

You'll get a response with a `verification_token`. Copy it!

### Verify Email:
```
POST http://localhost:8000/api/auth/verify-email/
Content-Type: application/json

{
  "token": "paste-token-here"
}
```

### Login:
```
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Test123!"
}
```

You'll get JWT tokens! Copy the `access` token.

### Get User Info (Protected Route):
```
GET http://localhost:8000/api/auth/me/
Authorization: Bearer paste-access-token-here
```

---

## Troubleshooting

### Error: "No module named 'django'"
**Solution**: Run Step 1 again to install Django

### Error: "No such table"
**Solution**: Run Step 2 again (migrations)

### Error: Port 8000 already in use
**Solution**: Use different port:
```powershell
py manage.py runserver 8001
```

---

## What's Working Now

✅ User Registration
✅ Email Verification
✅ Login (JWT tokens)
✅ Password Reset
✅ Profile Management
✅ Settings Management
✅ Admin Panel

---

## Next: Connect to React Frontend

Once backend is running, update React frontend:

1. Open `Growfund-Dashboard/trading-dashboard/src/services/api.js` (we'll create this)
2. Set API URL to `http://localhost:8000/api/`
3. Use JWT tokens for authenticated requests

---

## Need Help?

- Check `SETUP.md` for detailed instructions
- Check `BACKEND-SUMMARY.md` for complete overview
- Import `GrowFund-API.postman_collection.json` into Postman for easy testing
