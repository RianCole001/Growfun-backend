# 🧪 Quick API Testing Guide

## Test All Endpoints Before Frontend Integration

Use these commands to test all endpoints and verify responses match frontend expectations.

---

## 🔐 Step 1: Get Tokens

### Login as User
```bash
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Save the `access` token as `USER_TOKEN`

### Login as Admin
```bash
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin001@gmail.com",
    "password": "YOUR_ADMIN_PASSWORD"
  }'
```

Save the `access` token as `ADMIN_TOKEN`

---

## 📊 Step 2: Test Dashboard

```bash
curl -X GET "http://localhost:8000/api/auth/dashboard/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Has `balance` field
- [ ] Has `crypto` object with portfolio data
- [ ] Has `notifications.unread_count`
- [ ] Has `recent_activity` array
- [ ] All numbers are in correct format

---

## 🔔 Step 3: Test Notifications

### Get Notifications List
```bash
curl -X GET "http://localhost:8000/api/notifications/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Has `data` array
- [ ] Has `pagination` object
- [ ] Each notification has `id`, `title`, `message`, `type`, `read`, `created_at`

### Get Notification Stats
```bash
curl -X GET "http://localhost:8000/api/notifications/stats/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Has `total_notifications`
- [ ] Has `unread_notifications`
- [ ] Has `read_notifications`

### Create Test Notifications
```bash
curl -X POST "http://localhost:8000/api/notifications/create-welcome/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Creates 4 welcome notifications
- [ ] Returns notification data

### Mark as Read
```bash
curl -X POST "http://localhost:8000/api/notifications/1/read/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Returns success message

---

## 💰 Step 4: Test Crypto Endpoints

### Get Public Prices
```bash
curl -X GET "http://localhost:8000/api/investments/crypto/prices/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Has `data` object with coins
- [ ] Each coin has `price`, `change24h`, `change7d`, `change30d`
- [ ] Shows 4 coins (EXACOIN, BTC, ETH, USDT)

### Buy Crypto
```bash
curl -X POST "http://localhost:8000/api/investments/crypto/buy/" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coin": "EXACOIN",
    "amount": 100.00
  }'
```

**Check Response:**
- [ ] Has `investment` object
- [ ] Has `transaction` object
- [ ] Has `new_balance`
- [ ] Has `message`

### Get Portfolio
```bash
curl -X GET "http://localhost:8000/api/investments/crypto/portfolio/" \
  -H "Authorization: Bearer USER_TOKEN"
```

**Check Response:**
- [ ] Has `investments` array
- [ ] Has `summary` object
- [ ] Each investment has all required fields

### Sell Crypto
```bash
curl -X POST "http://localhost:8000/api/investments/crypto/sell/" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investment_id": 1,
    "coin": "EXACOIN",
    "quantity": 1.0
  }'
```

**Check Response:**
- [ ] Has `transaction` object
- [ ] Has `new_balance`
- [ ] Has `profit_loss`
- [ ] Has `message`

---

## 🔧 Step 5: Test Admin Endpoints

### Get All Crypto Prices (Admin)
```bash
curl -X GET "http://localhost:8000/api/investments/admin/crypto-prices/" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Check Response:**
- [ ] Has `data` object with all coins
- [ ] Each coin has `buy_price`, `sell_price`, `spread`, `spread_percentage`

### Update Crypto Price (Admin)
```bash
curl -X PUT "http://localhost:8000/api/investments/admin/crypto-prices/update/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coin": "EXACOIN",
    "buy_price": 70.00,
    "sell_price": 67.00,
    "change_24h": 5.00
  }'
```

**Check Response:**
- [ ] Returns success message
- [ ] Shows updated price data

### Send Notification to User (Admin)
```bash
curl -X POST "http://localhost:8000/api/notifications/admin/send/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "This is a test from admin",
    "type": "info",
    "user_id": 1
  }'
```

**Check Response:**
- [ ] Returns success message
- [ ] Shows notification data

### Send Notification to All Users (Admin)
```bash
curl -X POST "http://localhost:8000/api/notifications/admin/send/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Platform Update",
    "message": "New features available!",
    "type": "success",
    "send_to_all": true
  }'
```

**Check Response:**
- [ ] Returns success message
- [ ] Shows count of users notified

### Get Admin Dashboard
```bash
curl -X GET "http://localhost:8000/api/auth/admin/dashboard/" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Check Response:**
- [ ] Has user statistics
- [ ] Has transaction statistics
- [ ] Has investment statistics

---

## 📋 Response Format Checklist

For each endpoint, verify:

### Success Response
```json
{
  "data": {...},
  "success": true
}
```

### Error Response
```json
{
  "error": "Error message",
  "success": false
}
```

### With Pagination
```json
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 100,
    "has_next": true,
    "has_previous": false
  },
  "success": true
}
```

---

## 🎯 Common Issues to Check

### 1. CORS Errors
If you see CORS errors:
- Check `settings.py` has correct frontend URL
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend domain

### 2. Authentication Errors
If you get 401 Unauthorized:
- Check token is valid
- Verify `Authorization: Bearer TOKEN` header format
- Try refreshing token

### 3. 404 Not Found
If endpoint not found:
- Check URL path is correct
- Verify endpoint is in `urls.py`
- Check for trailing slashes

### 4. 500 Server Error
If you get 500 errors:
- Check server logs
- Verify database migrations are applied
- Check for missing dependencies

---

## 🔍 Debugging Tips

### View Response Headers
```bash
curl -i -X GET "http://localhost:8000/api/auth/dashboard/" \
  -H "Authorization: Bearer USER_TOKEN"
```

### Pretty Print JSON
```bash
curl -X GET "http://localhost:8000/api/auth/dashboard/" \
  -H "Authorization: Bearer USER_TOKEN" | python -m json.tool
```

### Save Response to File
```bash
curl -X GET "http://localhost:8000/api/auth/dashboard/" \
  -H "Authorization: Bearer USER_TOKEN" > response.json
```

---

## ✅ Final Checklist

Before committing, verify:

- [ ] All endpoints return 200 status
- [ ] Response formats match frontend expectations
- [ ] Field names are correct
- [ ] Number formats are correct
- [ ] Date formats are correct
- [ ] Pagination works
- [ ] Authentication works
- [ ] Admin endpoints require admin token
- [ ] Error messages are clear
- [ ] CORS is configured correctly

---

## 🚀 Ready to Deploy?

Once all tests pass:

1. ✅ All endpoints tested
2. ✅ Responses match frontend expectations
3. ✅ No errors in logs
4. ✅ CORS configured correctly
5. ✅ Authentication works

**Then commit and push!**

```bash
git add .
git commit -m "feat: Enhanced dashboard and notification system"
git push origin main
```

---

**Test everything locally first, then deploy to production!** 🎉
