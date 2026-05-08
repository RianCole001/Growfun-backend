# Admin Login Credentials

## ✅ Django Server Restarted

Django server has been restarted and is running on port 8000.

---

## 🔐 Admin Account

**Email:** `admin@growfund.com`

**Password:** You need to know the password you set when creating this admin account.

---

## 🔄 Reset Admin Password

If you don't remember the password, run this command:

```bash
cd backend-growfund
python reset_admin_password.py
```

This will reset the password to: `Admin123!`

**Or manually reset via Django shell:**

```bash
cd backend-growfund
python manage.py shell
```

Then in the shell:
```python
from accounts.models import User
admin = User.objects.get(email='admin@growfund.com')
admin.set_password('YourNewPassword123!')
admin.save()
print("Password reset successfully!")
exit()
```

---

## 📍 Admin Panel Access

### Localhost (Local Development)
```
http://localhost:3000/admin
```

### ngrok (Remote Access)
```
https://fdc9-129-222-147-116.ngrok-free.app/admin
```

---

## 🆕 Create New Admin Account

If you want to create a new admin account:

```bash
cd backend-growfund
python manage.py create_admin
```

Follow the prompts to enter:
- Email
- First name
- Last name  
- Password

---

## 🔍 Check Existing Admin Accounts

```bash
cd backend-growfund
python manage.py shell -c "from accounts.models import User; [print(f'Email: {u.email}') for u in User.objects.filter(is_staff=True)]"
```

---

## ✅ Current Server Status

| Service | Status | Port | URL |
|---------|--------|------|-----|
| Django Backend | ✅ Running | 8000 | http://localhost:8000 |
| React Frontend | ✅ Running | 3000 | http://localhost:3000 |

---

## 🎯 Quick Test

1. Open: http://localhost:3000/admin
2. Enter email: `admin@growfund.com`
3. Enter your password
4. Should login to admin dashboard

---

## 💡 Tip

If you can't remember the password, the easiest way is to run:

```bash
cd backend-growfund
python manage.py changepassword admin@growfund.com
```

This will prompt you to enter a new password interactively.

---

**Last Updated:** Current session
**Django Server:** ✅ Restarted and running on port 8000
