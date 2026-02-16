# Complete API Endpoints Testing Guide

## Base URLs

- **Backend:** https://growfun-backend.onrender.com
- **API Base:** https://growfun-backend.onrender.com/api
- **Admin Panel:** https://growfun-backend.onrender.com/admin/

⚠️ **Important:** Django admin requires trailing slash: `/admin/` not `/admin`

## Quick Test - Is Backend Running?

Open in browser:
```
https://growfun-backend.onrender.com/admin/
```

You should see Django admin login page.

## All Available Endpoints

### 1. Django Admin Panel

```
URL: https://growfun-backend.onrender.com/admin/
Method: GET (Browser)
Auth: Django session (login required)
```

**Test:**
1. Go to: https://growfun-backend.onrender.com/admin/
2. Login with: admin001@gmail.com / Buffers316!
3. You should see admin dashboard

### 2. Authentication Endpoints

#### Register
```
POST https://growfun-backend.onrender.com/api/auth/register/

Body:
{
  "email": "test@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

#### Login
```
POST https://growfun-backend.onrender.com/api/auth/login/

Body:
{
  "email": "admin001@gmail.com",
  "password": "Buffers316!"
}

Response:
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "email": "admin001@gmail.com",
    "first_name": "Admin",
    "is_staff": true
  }
}
```

#### Verify Email
```
GET https://growfun-backend.onrender.com/api/auth/verify-email/?token=YOUR_TOKEN

Response:
{
  "success": true,
  "message": "Email verified successfully! You can now login.",
  "redirect": "/login"
}
```

#### Resend Verification
```
POST https://growfun-backend.onrender.com/api/auth/resend-verification/

Body:
{
  "email": "user@example.com"
}
```

#### Get Current User
```
GET https://growfun-backend.onrender.com/api/auth/me/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### Get Profile
```
GET https://growfun-backend.onrender.com/api/auth/profile/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 3. Admin - User Management

#### List All Users
```
GET https://growfun-backend.onrender.com/api/auth/admin/users/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Response:
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "balance": "1000.00",
    "is_verified": true,
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

#### Get User Details
```
GET https://growfun-backend.onrender.com/api/auth/admin/users/1/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN
```

#### Update User
```
PUT https://growfun-backend.onrender.com/api/auth/admin/users/1/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Body:
{
  "first_name": "Updated",
  "balance": "2000.00"
}
```

#### Delete User
```
DELETE https://growfun-backend.onrender.com/api/auth/admin/users/1/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN
```

### 4. Admin - Deposit Management

#### List All Deposits
```
GET https://growfun-backend.onrender.com/api/transactions/admin/deposits/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Query Params (optional):
?status=pending
?search=user@example.com

Response:
{
  "success": true,
  "deposits": [
    {
      "id": 1,
      "user": {
        "id": 5,
        "email": "user@example.com",
        "first_name": "John"
      },
      "amount": "1000.00",
      "status": "pending",
      "reference": "DEP-ABC123",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "stats": {
    "total": 50,
    "pending": 10,
    "pending_amount": 10000.00
  }
}
```

#### Approve Deposit
```
POST https://growfun-backend.onrender.com/api/transactions/admin/deposits/1/approve/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Response:
{
  "success": true,
  "message": "Deposit of 1000.00 approved for user@example.com",
  "transaction": {...}
}
```

#### Reject Deposit
```
POST https://growfun-backend.onrender.com/api/transactions/admin/deposits/1/reject/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Body:
{
  "reason": "Invalid payment proof"
}

Response:
{
  "success": true,
  "message": "Deposit rejected for user@example.com",
  "transaction": {...}
}
```

### 5. Admin - Withdrawal Management

#### List All Withdrawals
```
GET https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Query Params (optional):
?status=pending
?search=user@example.com

Response:
{
  "success": true,
  "withdrawals": [
    {
      "id": 2,
      "user": {
        "id": 5,
        "email": "user@example.com"
      },
      "amount": "500.00",
      "fee": "10.00",
      "net_amount": "490.00",
      "status": "pending",
      "reference": "WTH-XYZ789",
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "stats": {
    "total": 30,
    "pending": 8,
    "processing": 3,
    "pending_amount": 4000.00
  }
}
```

#### Process Withdrawal
```
POST https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/2/process/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Response:
{
  "success": true,
  "message": "Withdrawal marked as processing for user@example.com"
}
```

#### Complete Withdrawal
```
POST https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/2/complete/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Response:
{
  "success": true,
  "message": "Withdrawal of 500.00 completed for user@example.com"
}
```

#### Reject Withdrawal
```
POST https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/2/reject/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Body:
{
  "reason": "Insufficient verification"
}

Response:
{
  "success": true,
  "message": "Withdrawal rejected and refunded for user@example.com"
}
```

### 6. Admin - Statistics

#### Get Dashboard Stats
```
GET https://growfun-backend.onrender.com/api/transactions/admin/stats/

Headers:
Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN

Response:
{
  "success": true,
  "deposits": {
    "total_count": 50,
    "pending_count": 10,
    "total_amount": 50000.00,
    "pending_amount": 10000.00
  },
  "withdrawals": {
    "total_count": 30,
    "pending_count": 8,
    "processing_count": 3,
    "total_amount": 15000.00
  },
  "recent_transactions": [...]
}
```

### 7. User Transactions

#### List User Transactions
```
GET https://growfun-backend.onrender.com/api/transactions/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Response:
[
  {
    "id": 1,
    "transaction_type": "deposit",
    "amount": "1000.00",
    "status": "completed",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### 8. Investments

#### List Investment Plans
```
GET https://growfun-backend.onrender.com/api/investments/plans/

Response:
[
  {
    "id": 1,
    "name": "Bitcoin Investment",
    "min_amount": "100.00",
    "max_amount": "10000.00",
    "roi_percentage": "15.00",
    "duration_days": 30
  }
]
```

#### List User Investments
```
GET https://growfun-backend.onrender.com/api/investments/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### Create Investment
```
POST https://growfun-backend.onrender.com/api/investments/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Body:
{
  "plan_id": 1,
  "amount": "1000.00"
}
```

### 9. Korapay Endpoints

#### Deposit via Korapay
```
POST https://growfun-backend.onrender.com/api/transactions/korapay/deposit/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Body:
{
  "amount": 1000,
  "phone_number": "+2348012345678",
  "payment_method": "mobile_money"
}
```

#### Get Supported Banks
```
GET https://growfun-backend.onrender.com/api/transactions/korapay/banks/?country=NG

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### Withdraw to Bank
```
POST https://growfun-backend.onrender.com/api/transactions/korapay/withdrawal/bank/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Body:
{
  "amount": 500,
  "account_number": "0123456789",
  "bank_code": "058",
  "account_name": "John Doe"
}
```

### 10. Referrals

#### Get Referral Stats
```
GET https://growfun-backend.onrender.com/api/auth/referral-stats/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN

Response:
{
  "referral_code": "ABC12345",
  "referral_link": "https://growfund-dashboard.onrender.com/register?ref=ABC12345",
  "total_referrals": 5,
  "total_earned": 250.00
}
```

## Testing with cURL

### Test Login
```bash
curl -X POST https://growfun-backend.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin001@gmail.com",
    "password": "Buffers316!"
  }'
```

### Test Admin Deposits (with token)
```bash
curl -X GET https://growfun-backend.onrender.com/api/transactions/admin/deposits/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Approve Deposit
```bash
curl -X POST https://growfun-backend.onrender.com/api/transactions/admin/deposits/1/approve/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Testing with JavaScript (Browser Console)

### 1. Login and Get Token
```javascript
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    email: 'admin001@gmail.com',
    password: 'Buffers316!'
  })
})
.then(res => res.json())
.then(data => {
  console.log('Login response:', data);
  localStorage.setItem('accessToken', data.tokens.access);
  localStorage.setItem('refreshToken', data.tokens.refresh);
});
```

### 2. Test Admin Deposits
```javascript
const token = localStorage.getItem('accessToken');

fetch('https://growfun-backend.onrender.com/api/transactions/admin/deposits/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log('Deposits:', data));
```

### 3. Test Approve Deposit
```javascript
const token = localStorage.getItem('accessToken');

fetch('https://growfun-backend.onrender.com/api/transactions/admin/deposits/1/approve/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log('Approval result:', data));
```

## Common Issues

### Issue: 404 on /admin
**Solution:** Use `/admin/` with trailing slash
- ❌ Wrong: https://growfun-backend.onrender.com/admin
- ✅ Correct: https://growfun-backend.onrender.com/admin/

### Issue: 401 Unauthorized
**Solution:** 
- Ensure you're logged in and have valid token
- Check token is included in Authorization header
- For admin endpoints, ensure user has `is_staff=True`

### Issue: 403 Forbidden on admin endpoints
**Solution:**
- User must have `is_staff=True` or `is_superuser=True`
- Check in Django admin: https://growfun-backend.onrender.com/admin/accounts/user/

### Issue: CORS Error
**Solution:**
- Ensure backend is deployed with latest code
- Check `DEBUG=True` in Render environment variables
- Clear browser cache

### Issue: Empty response or no data
**Solution:**
- Check if there's actual data in database
- Create test transactions via Django admin
- Check backend logs on Render

## Create Test Data

### Via Django Admin
1. Go to: https://growfun-backend.onrender.com/admin/
2. Login with admin credentials
3. Go to "Transactions"
4. Click "Add Transaction"
5. Fill in details and save

### Via API
```javascript
// Create test deposit
const token = localStorage.getItem('accessToken');

fetch('https://growfun-backend.onrender.com/api/transactions/korapay/deposit/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    amount: 1000,
    phone_number: '+2348012345678',
    payment_method: 'mobile_money'
  })
})
.then(res => res.json())
.then(data => console.log('Deposit created:', data));
```

## Verify All Endpoints Are Working

Run this test script in browser console:

```javascript
const API_BASE = 'https://growfun-backend.onrender.com/api';

// Test public endpoints
const publicTests = [
  { name: 'Investment Plans', url: `${API_BASE}/investments/plans/` },
];

// Test with authentication
const token = localStorage.getItem('accessToken');
const authTests = [
  { name: 'Current User', url: `${API_BASE}/auth/me/` },
  { name: 'User Transactions', url: `${API_BASE}/transactions/` },
  { name: 'Admin Deposits', url: `${API_BASE}/transactions/admin/deposits/` },
  { name: 'Admin Withdrawals', url: `${API_BASE}/transactions/admin/withdrawals/` },
  { name: 'Admin Stats', url: `${API_BASE}/transactions/admin/stats/` },
];

// Run tests
console.log('Testing public endpoints...');
publicTests.forEach(test => {
  fetch(test.url)
    .then(res => console.log(`✅ ${test.name}: ${res.status}`))
    .catch(err => console.error(`❌ ${test.name}:`, err));
});

if (token) {
  console.log('Testing authenticated endpoints...');
  authTests.forEach(test => {
    fetch(test.url, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => console.log(`✅ ${test.name}: ${res.status}`))
      .catch(err => console.error(`❌ ${test.name}:`, err));
  });
} else {
  console.log('⚠️ No token found. Login first to test authenticated endpoints.');
}
```

## Summary

All endpoints are configured and should be working. The main things to check:

1. ✅ Use `/admin/` with trailing slash
2. ✅ Include Authorization header for protected endpoints
3. ✅ Ensure admin user has `is_staff=True`
4. ✅ Backend is deployed with latest code
5. ✅ Environment variables are set on Render

If you're still getting 404s, check the exact URL you're accessing and ensure it matches the patterns above.
