# Backend Testing & Verification Guide

## Quick Test Commands

### 1. Create Test User (if needed)
```bash
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()
user = User.objects.create_user(
    email='testadmin@example.com',
    password='testpass123',
    first_name='Test',
    last_name='Admin',
    is_staff=True,
    is_superuser=True,
    is_verified=True
)
print(f"Admin user created: {user.email}")

# Create regular user
user2 = User.objects.create_user(
    email='testuser@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User',
    is_verified=True,
    balance=Decimal('0.00')
)
print(f"Regular user created: {user2.email}")
```

### 2. Get Admin Token
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testadmin@example.com",
    "password": "testpass123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "testadmin@example.com",
    "is_staff": true
  }
}
```

### 3. Get User Token
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

### 4. Test Admin Credit Endpoint
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/2/balance/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "credit",
    "amount": 100.00,
    "note": "Test promotional bonus"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "email": "testuser@example.com",
    "new_balance": 100.00,
    "transaction": {
      "id": 1,
      "type": "admin_credit",
      "amount": 100.00,
      "status": "completed",
      "created_at": "2026-04-26T10:30:00Z"
    }
  }
}
```

### 5. Verify User Balance Updated
```bash
curl http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer <user_token>"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "email": "testuser@example.com",
    "balance": 100.00,
    "first_name": "Test",
    "last_name": "User"
  }
}
```

### 6. Check Transaction History
```bash
curl http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer <user_token>"
```

**Expected Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "transaction_type": "admin_credit",
      "amount": "100.00",
      "fee": "0.00",
      "net_amount": "100.00",
      "status": "completed",
      "reference": "...",
      "description": "Test promotional bonus",
      "created_at": "2026-04-26T10:30:00Z",
      "completed_at": "2026-04-26T10:30:00Z"
    }
  ]
}
```

### 7. Test Transaction Summary
```bash
curl http://localhost:8000/api/transactions/summary/ \
  -H "Authorization: Bearer <user_token>"
```

**Expected Response:**
```json
{
  "data": {
    "total_deposits": "100.00",
    "total_withdrawals": "0.00",
    "pending_deposits": 0,
    "pending_withdrawals": 0,
    "current_balance": "100.00",
    "recent_transactions": [
      {
        "id": 1,
        "transaction_type": "admin_credit",
        "amount": "100.00",
        "status": "completed",
        "created_at": "2026-04-26T10:30:00Z"
      }
    ]
  }
}
```

### 8. Test Bulk Credit
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/bulk-credit/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [2, 3],
    "amount": 50.00,
    "note": "Monthly bonus"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "credited": ["testuser@example.com", "user3@example.com"],
  "failed": [],
  "total_credited": 2,
  "total_amount": 100.00
}
```

### 9. Test Admin Debit
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/2/balance/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "debit",
    "amount": 25.00,
    "note": "Adjustment"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "email": "testuser@example.com",
    "new_balance": 75.00,
    "transaction": {
      "id": 2,
      "type": "admin_debit",
      "amount": 25.00,
      "status": "completed"
    }
  }
}
```

---

## Admin Panel Testing

### 1. Access Admin Panel
Navigate to: `http://localhost:8000/admin/`

Login with admin credentials:
- Email: testadmin@example.com
- Password: testpass123

### 2. View Transactions
1. Go to: `Transactions > Transactions`
2. You should see the admin_credit and admin_debit transactions
3. Filter by "Admin Credit" in the transaction type dropdown

### 3. Edit Transaction
1. Click on an admin_credit transaction
2. Change the amount (e.g., 100 → 150)
3. Click Save
4. Verify user balance increased by $50

### 4. Verify Balance Update
1. Go to: `Accounts > Users`
2. Click on the test user
3. Check the balance field - should reflect the changes

---

## Database Verification

### Check Transactions Table
```bash
python manage.py shell
```

```python
from transactions.models import Transaction
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='testuser@example.com')

# Get all transactions
transactions = Transaction.objects.filter(user=user)
print(f"Total transactions: {transactions.count()}")

for t in transactions:
    print(f"  - {t.transaction_type}: ${t.amount} ({t.status})")
    print(f"    Description: {t.description}")
    print(f"    Created: {t.created_at}")
    print()

# Check user balance
print(f"User balance: ${user.balance}")
```

---

## Error Handling Tests

### 1. Test Insufficient Permissions
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/2/balance/ \
  -H "Authorization: Bearer <regular_user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "credit",
    "amount": 100
  }'
```

**Expected Response:**
```json
{
  "error": "Admin access required",
  "status": 403
}
```

### 2. Test Invalid Amount
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/2/balance/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "credit",
    "amount": -100
  }'
```

**Expected Response:**
```json
{
  "error": "Amount must be greater than 0",
  "status": 400
}
```

### 3. Test Invalid User
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/99999/balance/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "credit",
    "amount": 100
  }'
```

**Expected Response:**
```json
{
  "error": "User not found",
  "status": 404
}
```

### 4. Test Insufficient Balance for Debit
```bash
curl -X POST http://localhost:8000/api/accounts/admin/users/2/balance/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "debit",
    "amount": 1000
  }'
```

**Expected Response:**
```json
{
  "error": "Insufficient balance",
  "status": 400
}
```

---

## Performance Testing

### Test with Multiple Credits
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/accounts/admin/users/2/balance/ \
    -H "Authorization: Bearer <admin_token>" \
    -H "Content-Type: application/json" \
    -d "{
      \"action\": \"credit\",
      \"amount\": 10.00,
      \"note\": \"Credit $i\"
    }"
  echo "Credit $i completed"
done
```

Then verify:
```bash
curl http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer <user_token>"
```

Should show 10 transactions with total balance of $100.

---

## Checklist

- [ ] Admin can credit user balance
- [ ] Transaction record created automatically
- [ ] User balance updated correctly
- [ ] Transaction visible in user's history
- [ ] Admin can debit user balance
- [ ] Bulk credit works for multiple users
- [ ] Transaction can be edited in admin panel
- [ ] Balance adjusts when transaction amount edited
- [ ] Transaction summary includes admin credits
- [ ] Error handling works correctly
- [ ] Permission checks working
- [ ] Database transactions are atomic
- [ ] Timestamps are correct
- [ ] Descriptions are saved and editable

---

## Troubleshooting

### Issue: "Admin access required" error
**Solution:** Make sure you're using an admin token, not a regular user token

### Issue: Transaction not appearing in history
**Solution:** 
1. Check if transaction status is 'completed'
2. Verify user ID matches
3. Check database directly: `Transaction.objects.filter(user=user)`

### Issue: Balance not updating
**Solution:**
1. Verify transaction was created
2. Check user.balance field in database
3. Ensure save() was called on user object

### Issue: Edit not working in admin panel
**Solution:**
1. Make sure you're editing an admin_credit or admin_debit transaction
2. Check that you have admin permissions
3. Verify the transaction is not read-only

---

## Live Testing Scenario

1. **Create test users** (admin + regular user)
2. **Get tokens** for both users
3. **Admin credits user** $100
4. **Verify balance** updated to $100
5. **Check transaction history** shows admin_credit
6. **Edit transaction** in admin panel to $150
7. **Verify balance** updated to $150
8. **User sees transaction** in their history
9. **Bulk credit** multiple users
10. **Verify all** transactions recorded correctly

All tests should pass! ✅
