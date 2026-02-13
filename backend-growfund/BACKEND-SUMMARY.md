# GrowFund Backend - Phase 1 Complete ✅

## What's Been Created

### 1. Project Structure ✅
- Django 4.2 project with REST Framework
- PostgreSQL/SQLite database support
- JWT authentication
- Celery for background tasks
- CORS configuration for React frontend

### 2. User Authentication System ✅

#### Models
- **User Model** (Custom)
  - Email-based authentication (no username)
  - Profile fields (phone, avatar, location, occupation, etc.)
  - Balance tracking
  - Email verification
  - Password reset tokens
  - Referral system integration
  - Timestamps

- **UserSettings Model**
  - Theme, currency, language, timezone
  - Notification preferences
  - Security settings (2FA, login alerts)
  - Privacy settings

#### API Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (returns JWT tokens)
- `POST /api/auth/verify-email/` - Email verification
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password
- `GET /api/auth/me/` - Get current user
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/settings/` - Get user settings
- `PUT /api/auth/settings/` - Update user settings
- `POST /api/auth/change-password/` - Change password
- `GET /api/auth/balance/` - Get user balance

#### Features
- Email verification with tokens
- Password reset with expiring tokens
- JWT access & refresh tokens
- Profile management
- Settings management
- Referral code generation
- Admin panel integration

#### Background Tasks (Celery)
- Send verification emails
- Send password reset emails
- Send welcome emails

---

## Quick Start

### Option 1: Automated Setup (Windows)

```bash
cd backend-growfund
quickstart.bat
```

This will:
1. Create virtual environment
2. Install dependencies
3. Create .env file
4. Run migrations
5. Create superuser

### Option 2: Manual Setup

```bash
cd backend-growfund

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

---

## Testing the API

### 1. Register User
```bash
POST http://localhost:8000/api/auth/register/
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 2. Verify Email
```bash
POST http://localhost:8000/api/auth/verify-email/
{
  "token": "<verification_token_from_response>"
}
```

### 3. Login
```bash
POST http://localhost:8000/api/auth/login/
{
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

### 4. Access Protected Route
```bash
GET http://localhost:8000/api/auth/me/
Authorization: Bearer <access_token>
```

---

## Database Schema

### User Table
- id (PK)
- email (unique)
- password (hashed)
- first_name, last_name
- phone, avatar
- location, occupation, company, website, bio
- balance (decimal)
- is_verified (boolean)
- verification_token (UUID)
- reset_token (UUID)
- referral_code (unique)
- referred_by (FK to User)
- created_at, updated_at, last_login_at

### UserSettings Table
- id (PK)
- user (FK to User, OneToOne)
- theme, currency, language, timezone
- email_notifications, push_notifications, etc.
- two_factor_enabled, login_alerts, session_timeout
- profile_visible, portfolio_visible, activity_sharing
- created_at, updated_at

---

## Next Steps (Phase 2)

### 1. Investments App
- Investment model (crypto, real estate, capital plans)
- Buy/sell endpoints
- Portfolio tracking
- Price integration (CoinGecko API)

### 2. Transactions App
- Transaction model
- Deposit endpoints
- Withdrawal endpoints
- Transaction history
- Admin approval system

### 3. Referrals App
- Referral tracking
- Bonus calculation
- Referral stats

### 4. Notifications App
- Notification model
- Real-time notifications
- Email notifications
- Push notifications

### 5. Admin APIs
- User management
- Investment monitoring
- Deposit/withdrawal approvals
- Platform statistics

---

## File Structure

```
backend-growfund/
├── growfund/                    # Main project
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL config
│   ├── wsgi.py                 # WSGI config
│   └── celery.py               # Celery config
│
├── accounts/                    # ✅ User authentication
│   ├── models.py               # User, UserSettings models
│   ├── serializers.py          # API serializers
│   ├── views.py                # API views
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Admin configuration
│   ├── tasks.py                # Celery tasks
│   └── apps.py                 # App config
│
├── investments/                 # 🔜 Next
│   └── ...
│
├── transactions/                # 🔜 Next
│   └── ...
│
├── referrals/                   # 🔜 Next
│   └── ...
│
├── notifications/               # 🔜 Next
│   └── ...
│
├── manage.py                    # Django management
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── README.md                    # Documentation
├── SETUP.md                     # Setup guide
└── quickstart.bat               # Quick setup script
```

---

## Technologies Used

- **Django 4.2** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database (or SQLite for dev)
- **JWT** - Authentication tokens
- **Celery** - Background tasks
- **Redis** - Message broker & cache
- **Python Decouple** - Environment variables

---

## Security Features

- Password hashing (Django's PBKDF2)
- JWT token authentication
- Email verification required
- Password reset with expiring tokens
- CORS protection
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection

---

## Admin Panel

Access at: `http://localhost:8000/admin/`

Features:
- User management
- View/edit user profiles
- View user settings
- Search and filter users
- Bulk actions

---

## Environment Variables

Key variables in `.env`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Allowed hosts
- `DB_*` - Database configuration
- `EMAIL_*` - Email configuration
- `FRONTEND_URL` - React app URL
- `JWT_*` - JWT token lifetimes

---

## API Response Format

### Success Response
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": { ... }
}
```

### Validation Error
```json
{
  "field_name": ["Error message"]
}
```

---

## Status

✅ **Phase 1 Complete**: User Authentication System
- Registration with email verification
- Login with JWT tokens
- Password reset
- Profile management
- Settings management
- Admin panel

🔜 **Phase 2 Next**: Investment & Transaction Systems

---

## Support

For issues or questions:
1. Check SETUP.md for installation help
2. Check README.md for API documentation
3. Review Django logs for errors

---

## License

Proprietary - GrowFund Platform
