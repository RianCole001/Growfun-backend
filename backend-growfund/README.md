# GrowFund Backend API

Django REST API for the GrowFund investment platform.

## Features

- User authentication (JWT)
- User registration & email verification
- Password reset
- Investment management (Crypto, Real Estate, Capital Plans)
- Deposits & Withdrawals
- Transaction history
- Referral system
- Admin dashboard APIs
- Real-time crypto prices
- Notifications

## Tech Stack

- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Celery (background tasks)
- Redis (caching & message broker)

## Setup

### 1. Create Virtual Environment

```bash
cd backend-growfund
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb growfund_db

# Or use SQLite for development (edit settings.py)
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

API will be available at `http://localhost:8000/api/`

### 8. Run Celery (Optional - for background tasks)

```bash
# In a new terminal
celery -A growfund worker -l info

# Celery beat for scheduled tasks
celery -A growfund beat -l info
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/verify-email/` - Verify email
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password
- `GET /api/auth/me/` - Get current user

### Users
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile
- `GET /api/users/balance/` - Get user balance

### Investments
- `GET /api/investments/` - List user investments
- `POST /api/investments/` - Create investment
- `GET /api/investments/{id}/` - Get investment details
- `DELETE /api/investments/{id}/` - Delete investment

### Crypto
- `GET /api/crypto/prices/` - Get crypto prices
- `GET /api/crypto/market-data/` - Get market data
- `POST /api/crypto/invest/` - Invest in crypto
- `POST /api/crypto/sell/` - Sell crypto

### Deposits
- `GET /api/deposits/` - List deposits
- `POST /api/deposits/` - Create deposit
- `GET /api/deposits/{id}/` - Get deposit details

### Withdrawals
- `GET /api/withdrawals/` - List withdrawals
- `POST /api/withdrawals/` - Create withdrawal
- `GET /api/withdrawals/{id}/` - Get withdrawal details

### Transactions
- `GET /api/transactions/` - List transactions
- `GET /api/transactions/{id}/` - Get transaction details

### Referrals
- `GET /api/referrals/` - Get referral data
- `POST /api/referrals/claim/` - Claim referral bonus

### Admin
- `GET /api/admin/users/` - List all users
- `GET /api/admin/investments/` - List all investments
- `GET /api/admin/deposits/` - List all deposits
- `PUT /api/admin/deposits/{id}/approve/` - Approve deposit
- `GET /api/admin/withdrawals/` - List all withdrawals
- `PUT /api/admin/withdrawals/{id}/approve/` - Approve withdrawal
- `GET /api/admin/stats/` - Get platform statistics

## Testing

```bash
python manage.py test
```

## Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## License

Proprietary - GrowFund Platform
