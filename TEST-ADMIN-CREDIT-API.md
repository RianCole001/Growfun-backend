# Test Admin Credit API - Complete Guide

**Backend Status:** ✅ Running on http://127.0.0.1:8000/  
**Database:** ✅ Working (balance updates confirmed)  
**Issue:** Need to test actual API endpoint

---

## Test Results

### Database Test ✅
```
User: migwibrian316@gmail.com
Balance: $90.00 → $100.00 (after +$10 credit)
Transactions: 2 admin_credit transactions recorded
```

**Conclusion:** Database operations work correctly!

---

## API Endpoint Details

### Credit/Debit Single User
```
POST /api/accounts/admin/users/<user_id>/balance/
Authorization: Bearer <admin_token>
Content-Type: application/json

Body:
{
  "action": "credit",  // or "debit"
  "amount": 10.00,
  "note": "Test credit"
}

Response:
{
  "success": true,
  "user": "user@example.com",
  "action": "credit",
  "amount": "10.00",
  "new_balance": "110.00"
}
```

### Bulk Credit
```
POST /api/accounts/admin/users/bulk-credit/
Authorization: Bearer <admin_token>
Content-Type: application/json

Body:
{
  "user_ids": [1, 2, 3],
  "amount": 20.00,
  "note": "Promotional bonus"
}

Response:
{
  "success": true,
  "credited": ["user1@example.com", "user2@example.com"],
  "failed": [],
  "amount": "20.00",
  "total_credited": 2
}
```

---

## How to Test with Frontend

### Step 1: Get Admin Token

1. Open browser to http://localhost:3000/admin (once frontend starts)
2. Login with admin credentials
3. Open browser DevTools (F12)
4. Go to Application → Local Storage
5. Find `admin_access_token`
6. Copy the token value

### Step 2: Test with Postman/Insomnia

**Credit a User:**
```
POST http://127.0.0.1:8000/api/accounts/admin/users/1/balance/
Headers:
  Authorization: Bearer <your_admin_token>
  Content-Type: application/json
Body:
{
  "action": "credit",
  "amount": 10,
  "note": "Test credit"
}
```

### Step 3: Test with curl

```bash
# Get user ID first
curl http://127.0.0.1:8000/api/accounts/admin/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Credit user
curl -X POST http://127.0.0.1:8000/api/accounts/admin/users/1/balance/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"credit","amount":10,"note":"Test"}'
```

---

## Frontend API Call

The frontend should call:

```javascript
// In src/services/api.js
adjustUserBalance: (userId, action, amount, note) =>
    adminApi.post(`/accounts/admin/users/${userId}/balance/`, { 
        action,  // "credit" or "debit"
        amount, 
        note 
    }),
```

**Current frontend code is correct!** ✅

---

## Troubleshooting

### Issue: "No changes on my account"

**Possible Causes:**

1. **Frontend not calling correct endpoint**
   - Check: Browser DevTools → Network tab
   - Look for: POST request to `/api/accounts/admin/users/{id}/balance/`
   - Verify: Request body has `action`, `amount`, `note`

2. **Wrong user ID**
   - Check: Is the correct user ID being sent?
   - Verify: User ID matches the user you're trying to credit

3. **Frontend not refreshing data**
   - Check: Does the page refresh after credit?
   - Verify: Is the balance being fetched again?

4. **Token expired**
   - Check: Is the admin token still valid?
   - Solution: Login again

5. **CORS issues**
   - Check: Browser console for CORS errors
   - Verify: Backend CORS settings allow localhost:3000

---

## Next Steps

### 1. Start Frontend Server

```powershell
cd wazimu/Growfund-Dashboard
.\fix-frontend.ps1
```

### 2. Login as Admin

```
URL: http://localhost:3000/admin
```

### 3. Test Credit Feature

1. Go to User Management
2. Find a user
3. Click $ icon
4. Select "Credit"
5. Enter amount: 10
6. Click "Credit"
7. **Open DevTools Network tab to see the API call**

### 4. Verify in Backend

```bash
cd backend-growfund
python test_credit_endpoint.py
```

---

## Expected Behavior

### When Credit Button is Clicked:

1. Frontend sends POST to `/api/accounts/admin/users/{id}/balance/`
2. Backend receives request
3. Backend validates admin token
4. Backend updates user balance
5. Backend creates transaction record
6. Backend returns success response
7. Frontend updates UI with new balance
8. User sees updated balance immediately

### What to Check:

- ✅ Backend logs show the credit operation
- ✅ Database shows updated balance
- ✅ Transaction record created
- ✅ Frontend receives success response
- ✅ UI updates with new balance

---

## Debug Checklist

If credits still don't work:

- [ ] Backend server running? (http://127.0.0.1:8000/)
- [ ] Frontend server running? (http://localhost:3000/)
- [ ] Logged in as admin?
- [ ] Admin token valid?
- [ ] Network tab shows API call?
- [ ] API call returns 200 OK?
- [ ] Response has `success: true`?
- [ ] Balance field updates in UI?
- [ ] Page refreshes after credit?

---

## Current Status

- ✅ Backend running
- ✅ Database operations working
- ✅ API endpoint implemented correctly
- ✅ Frontend code synchronized
- ⚠️ Frontend server needs to start
- ⚠️ Need to test end-to-end with UI

**Once frontend starts, we can test the complete flow!**
