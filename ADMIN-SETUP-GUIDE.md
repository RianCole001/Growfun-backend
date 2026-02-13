# Admin Panel Setup Guide

## Overview
The admin panel is now fully connected to the Django backend with two admin accounts. It displays all registered users from the database and requires admin authentication.

## Admin Credentials

| Admin | Email | Password |
|-------|-------|----------|
| Admin 1 | admin001@gmail.com | Buffers316! |
| Admin 2 | admin@growfund.com | Admin123! |

## Setup Steps

### 1. Create Admin Users (Backend)

Run the Django management command to create both admin superusers:

```bash
cd backend-growfund
py manage.py create_admin
```

Or use the quick fix script:

```bash
py fix_admin.py
```

This will create:
- **Admin 1**: admin001@gmail.com / Buffers316!
- **Admin 2**: admin@growfund.com / Admin123!

Both will have:
- Staff permissions
- Superuser permissions
- Email verified

If admin users already exist, the command will update their permissions to ensure they have staff/superuser access.

### 2. Start Backend Server

```bash
cd backend-growfund
py manage.py runserver
```

The backend will run on `http://localhost:8000`

### 3. Start Frontend Server

In a new terminal:

```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

The frontend will run on `http://localhost:3000`

### 4. Access Admin Panel

Navigate to: `http://localhost:3000/admin`

Login with either admin account:
- **Admin 1**: admin001@gmail.com / Buffers316!
- **Admin 2**: admin@growfund.com / Admin123!

## Features

### User Management
- View all registered users
- See user verification status
- Check user balances and investments
- Filter users by status (active, pending, suspended)
- Search users by name or email

### User Information Displayed
- User name and email
- Verification status (verified/pending)
- Account balance
- Total invested amount
- Join date
- Account status

## Backend API Endpoints

### Admin Users List
```
GET /api/auth/admin/users/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "balance": "1000.00",
      "is_verified": true,
      "is_staff": false,
      "is_superuser": false,
      "created_at": "2024-02-11T10:30:00Z",
      "last_login_at": "2024-02-11T15:45:00Z"
    }
  ],
  "count": 1
}
```

**Requirements:**
- User must be authenticated
- User must have `is_staff` or `is_superuser` permission

## Authentication Flow

1. Admin enters credentials on login page
2. Frontend sends login request to backend
3. Backend validates credentials and returns JWT tokens
4. Frontend checks if user has `is_staff` or `is_superuser` permission
5. If authorized, admin is logged in and can access user management
6. If not authorized, error message is shown

## Troubleshooting

### 403 Forbidden Error
**Problem**: Admin panel shows "Admin access required" error

**Solution**:
1. Ensure admin users were created with superuser permissions:
   ```bash
   py fix_admin.py
   ```
2. Verify the admin users in Django admin:
   ```bash
   py manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> for email in ['admin001@gmail.com', 'admin@growfund.com']:
   ...     admin = User.objects.get(email=email)
   ...     print(f"{email}: is_staff={admin.is_staff}, is_superuser={admin.is_superuser}")
   ```

### No Users Showing
**Problem**: Admin panel loads but shows no users

**Solution**:
1. Check if users exist in database:
   ```bash
   py manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.count()
   ```
2. Register a test user through the frontend
3. Refresh the admin panel

### CORS Error
**Problem**: Browser shows CORS error when accessing admin panel

**Solution**:
1. Verify CORS is configured in Django settings
2. Check that `http://localhost:3000` is in `CORS_ALLOWED_ORIGINS`
3. Restart Django server

## Testing

### Test Admin Login
1. Go to `http://localhost:3000/admin`
2. Enter credentials for either admin:
   - Admin 1: admin001@gmail.com / Buffers316!
   - Admin 2: admin@growfund.com / Admin123!
3. Click "Sign In"
4. Should see user management dashboard

### Test User Registration
1. Go to `http://localhost:3000/register`
2. Create a test account
3. Verify email (check console for verification token)
4. Login with test account
5. Go back to admin panel
6. New user should appear in the users list

## Security Notes

- Admin credentials are stored in backend database with hashed passwords
- JWT tokens are used for API authentication
- Tokens expire after configured time (default: 60 minutes)
- Refresh tokens are used to get new access tokens
- Only users with `is_staff` or `is_superuser` can access admin endpoints
- Two separate admin accounts for redundancy and security

## Next Steps

- Implement user actions (edit, delete, email)
- Add user statistics dashboard
- Implement investment management
- Add transaction management
- Implement withdrawal/deposit management
- Add admin activity logging
