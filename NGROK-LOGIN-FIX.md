# Ngrok Login/Register Not Working - Fix Guide

## 🔍 Problem

Pages display but login/register don't work on ngrok because:
1. Frontend `.env` doesn't have correct ngrok backend URL
2. Frontend is still calling `localhost:8000` instead of ngrok URL
3. CORS errors blocking API calls

---

## ✅ Solution

### Step 1: Check Your Ngrok URLs

**Terminal 3 (Backend Ngrok):**
```bash
ngrok http 8000
```

You should see:
```
Forwarding    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

**Copy this URL:** `https://xxxx-xxxx-xxxx.ngrok-free.app`

**Terminal 4 (Frontend Ngrok):**
```bash
ngrok http 3000
```

You should see:
```
Forwarding    https://yyyy-yyyy-yyyy.ngrok-free.app -> http://localhost:3000
```

**Copy this URL:** `https://yyyy-yyyy-yyyy.ngrok-free.app`

---

### Step 2: Update Frontend .env

**File:** `Growfund-Dashboard/trading-dashboard/.env`

```bash
# IMPORTANT: Use HTTPS ngrok URL, not localhost!
REACT_APP_API_URL=https://xxxx-xxxx-xxxx.ngrok-free.app
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_id
```

**Replace `xxxx-xxxx-xxxx` with YOUR actual ngrok backend URL!**

---

### Step 3: Update Backend settings.py

**File:** `backend-growfund/growfund/settings.py`

```python
# Update ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'xxxx-xxxx-xxxx.ngrok-free.app',  # Your ngrok backend URL
]

# Update CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://yyyy-yyyy-yyyy.ngrok-free.app',  # Your ngrok frontend URL
]
```

**Replace with YOUR actual ngrok URLs!**

---

### Step 4: Restart Frontend

```bash
# Terminal 2 - Stop frontend
Ctrl+C

# Restart frontend
npm start
```

Wait for:
```
Compiled successfully!
```

---

### Step 5: Restart Backend

```bash
# Terminal 1 - Stop backend
Ctrl+C

# Restart backend
python manage.py runserver 0.0.0.0:8000
```

Wait for:
```
Starting development server at http://127.0.0.1:8000/
```

---

### Step 6: Test Login

1. Open: `https://yyyy-yyyy-yyyy.ngrok-free.app`
2. Click "Login"
3. Enter:
   - Email: `admin001@gmail.com`
   - Password: `Buffers316!`
4. Click "Login"
5. Should work now! ✅

---

## 🔧 Troubleshooting

### Issue: Still getting CORS error

**Solution:**
1. Check `.env` has correct ngrok backend URL
2. Check `settings.py` has correct ngrok frontend URL
3. Restart both backend and frontend
4. Clear browser cache (Ctrl+Shift+Delete)
5. Hard refresh (Ctrl+Shift+R)

### Issue: "Cannot POST /api/auth/login/"

**Solution:**
1. Check backend is running
2. Check ngrok backend tunnel is running
3. Check `.env` has correct URL
4. Check URL doesn't have `/api` at the end (it's added automatically)

### Issue: Pages load but buttons don't work

**Solution:**
1. Open browser console (F12)
2. Check for error messages
3. Look for CORS errors
4. Check network tab to see API calls
5. Verify URLs in network requests

---

## 📋 Complete Checklist

- [ ] Get ngrok backend URL (Terminal 3)
- [ ] Get ngrok frontend URL (Terminal 4)
- [ ] Update `.env` with ngrok backend URL
- [ ] Update `settings.py` ALLOWED_HOSTS
- [ ] Update `settings.py` CORS_ALLOWED_ORIGINS
- [ ] Restart frontend
- [ ] Restart backend
- [ ] Clear browser cache
- [ ] Hard refresh browser
- [ ] Test login

---

## 🔄 Example Configuration

### Your Ngrok URLs (Example)
```
Backend: https://a1b2-c3d4-e5f6.ngrok-free.app
Frontend: https://x9y8-z7w6-v5u4.ngrok-free.app
```

### Frontend .env
```
REACT_APP_API_URL=https://a1b2-c3d4-e5f6.ngrok-free.app
```

### Backend settings.py
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'a1b2-c3d4-e5f6.ngrok-free.app',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://x9y8-z7w6-v5u4.ngrok-free.app',
]
```

---

## 🧪 Test API Directly

Open browser console (F12) and run:

```javascript
// Test if API is accessible
fetch('https://YOUR-NGROK-BACKEND-URL/api/auth/me/', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
.then(r => r.json())
.then(d => console.log(d))
.catch(e => console.error(e))
```

Should return user data or 401 error (if not authenticated).

---

## 📊 Debug Checklist

1. **Check .env file exists**
   ```bash
   ls Growfund-Dashboard/trading-dashboard/.env
   ```

2. **Check .env has correct URL**
   ```bash
   cat Growfund-Dashboard/trading-dashboard/.env
   ```

3. **Check settings.py has correct URLs**
   ```bash
   grep -A 5 "ALLOWED_HOSTS" backend-growfund/growfund/settings.py
   grep -A 5 "CORS_ALLOWED_ORIGINS" backend-growfund/growfund/settings.py
   ```

4. **Check ngrok is running**
   - Terminal 3 should show ngrok backend tunnel
   - Terminal 4 should show ngrok frontend tunnel

5. **Check services are running**
   - Terminal 1 should show Django running
   - Terminal 2 should show React running

---

## 🎯 Quick Fix Summary

1. Get your ngrok URLs
2. Update `.env` with ngrok backend URL
3. Update `settings.py` with ngrok URLs
4. Restart frontend and backend
5. Clear browser cache
6. Test login

---

## ✨ You're Ready!

Login/register should now work on ngrok! 🎉

If still having issues, check the troubleshooting section above.
