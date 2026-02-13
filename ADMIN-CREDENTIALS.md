# Admin Panel Credentials

## Two Admin Accounts Created

The system now has two separate admin accounts for security and redundancy.

### Admin Account 1
- **Email**: admin001@gmail.com
- **Password**: Buffers316!
- **Role**: Superuser + Staff
- **Permissions**: Full admin access

### Admin Account 2
- **Email**: admin@growfund.com
- **Password**: Admin123!
- **Role**: Superuser + Staff
- **Permissions**: Full admin access

## How to Setup

### Quick Setup (Recommended)
```bash
cd backend-growfund
py fix_admin.py
```

### Using Django Management Command
```bash
cd backend-growfund
py manage.py create_admin
```

## How to Login

1. Navigate to: `http://localhost:3000/admin`
2. Enter either admin email and password
3. Click "Sign In"
4. You'll see the user management dashboard

## What Admin Can Do

- View all registered users
- See user details (email, name, balance, investments)
- Filter users by status (active, pending, suspended)
- Search users by name or email
- View user join dates and last login times
- See verification status

## Security

- Both accounts have full admin privileges
- Passwords are hashed in the database
- JWT tokens are used for API authentication
- Admin access is restricted to users with `is_staff` or `is_superuser` permissions
- Tokens expire after 60 minutes (configurable)

## Troubleshooting

If you can't login:

1. Run the setup script:
   ```bash
   py fix_admin.py
   ```

2. Check if admin users exist:
   ```bash
   py manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> User.objects.filter(email__in=['admin001@gmail.com', 'admin@growfund.com']).count()
   ```

3. Verify permissions:
   ```bash
   >>> for email in ['admin001@gmail.com', 'admin@growfund.com']:
   ...     u = User.objects.get(email=email)
   ...     print(f"{email}: staff={u.is_staff}, superuser={u.is_superuser}")
   ```

## Files Modified

- `backend-growfund/accounts/management/commands/create_admin.py` - Creates both admins
- `backend-growfund/fix_admin.py` - Quick setup script
- `Growfund-Dashboard/trading-dashboard/src/AdminApp.js` - Shows both credentials
