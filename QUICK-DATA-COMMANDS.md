# Quick Data Management Commands

## Reset and Regenerate Data (Most Common)

```bash
cd backend-growfund

# Delete all data except users
python manage.py reset_data --confirm

# Generate fresh test data
python manage.py create_test_data

# Verify the data
python verify_test_data.py
```

## Test Credentials

### Test Users
- **user1@example.com** / testpass123 (Balance: $300)
- **user2@example.com** / testpass123 (Balance: $400)
- **user3@example.com** / testpass123 (Balance: $500)

### Admin User
- **admin@growfund.com** / admin123

## What Gets Created

- ✅ 3 test users (verified accounts)
- ✅ 6 deposits ($1000, $500, $2000)
- ✅ 2 capital plans (Basic $500, Advance $1500)
- ✅ 2 crypto trades (Gold, USDT)
- ✅ 1 withdrawal request (pending)
- ✅ 6 notifications

## Admin Endpoints

All working and require authentication:

- `/api/admin/investments/` - View all investments
- `/api/admin/deposits/` - View all deposits
- `/api/admin/transactions/` - View all transactions
- `/api/admin/withdrawals/` - View pending withdrawals

## Quick Verification

```bash
# Check what data exists
python verify_test_data.py

# Test admin endpoints
python test_admin_with_new_data.py
```

## Safety Notes

- ⚠️ `reset_data` requires `--confirm` flag
- ✅ User accounts are always preserved
- ✅ User balances are reset to $0
- ✅ Commands are safe to run multiple times
