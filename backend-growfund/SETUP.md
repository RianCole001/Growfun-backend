# GrowFund Backend Setup Guide

## Step-by-Step Installation

### Step 1: Prerequisites

Make sure you have installed:
- Python 3.10 or higher
- PostgreSQL (or use SQLite for development)
- Redis (for Celery tasks)

### Step 2: Create Virtual Environment

```bash
cd backend-growfund
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

```bash
# Copy example env file
copy .env.example .env

# Edit .env file with your settings
# For quick start, you can use SQLite (no PostgreSQL needed)
```

**Quick Start .env (SQLite)**:
```env
SECRET_KEY=your-secret-key-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Use SQLite (no PostgreSQL needed)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Email (console backend for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

FRONTEND_URL=http://localhost:3000
```

### Step 5: Create Database Tables

```bash
python manage.py makemigrations accounts
python manage.py makemigrations investments
python manage.py makemigrations transactions
python manage.py makemigrations referrals
python manage.py makemigrations notifications

python manage.py migrate
```

### Step 6: Create Superuser (Admin)

```bash
python manage.py createsuperuser
# Enter email: admin@growfund.com
# Enter password: (your secure password)
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Server will start at: `http://localhost:8000`

### Step 8: Test API

Open browser or Postman:
- Admin Panel: `http://localhost:8000/admin/`
- API Root: `http://localhost:8000/api/`

### Step 9: Run Celery (Optional - for emails)

In a new terminal:

```bash
# Activate venv first
venv\Scripts\activate

# Start Celery worker
celery -A growfund worker -l info --pool=solo

# In another terminal, start Celery beat (for scheduled tasks)
celery -A growfund beat -l info
```

Note: For Windows, use `--pool=solo` flag

---

## Testing the API

### 1. Register a User

```bash
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "user@example.com",
  "verification_token": "abc-123-def-456"
}
```

### 2. Verify Email

```bash
POST http://localhost:8000/api/auth/verify-email/
Content-Type: application/json

{
  "token": "abc-123-def-456"
}
```

### 3. Login

```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Response:
```json
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "balance": "0.00"
  }
}
```

### 4. Get Current User (Protected Route)

```bash
GET http://localhost:8000/api/auth/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Database errors

**Solution**: Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: CORS errors from React

**Solution**: Check `CORS_ALLOWED_ORIGINS` in `settings.py` includes your React URL

### Issue: Celery not working on Windows

**Solution**: Use `--pool=solo` flag:
```bash
celery -A growfund worker -l info --pool=solo
```

---

## Next Steps

1. ✅ User authentication is complete
2. Create investment models and APIs
3. Create transaction models and APIs
4. Create referral system
5. Create admin APIs
6. Connect to React frontend

---

## Project Structure

```
backend-growfund/
├── growfund/              # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── accounts/              # User authentication
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── admin.py
│   └── tasks.py
├── investments/           # Investment management (next)
├── transactions/          # Transactions (next)
├── referrals/            # Referral system (next)
├── notifications/        # Notifications (next)
├── manage.py
├── requirements.txt
└── .env
```

---

## API Documentation

Full API documentation will be available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

(To be added in next steps)
