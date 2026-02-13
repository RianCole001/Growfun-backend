# Check Ngrok Configuration - Diagnostic Guide

## 🔍 Quick Diagnostic

Run these commands to check your configuration:

### 1. Check Frontend .env

```bash
cd Growfund-Dashboard/trading-dashboard
cat .env
```

**Should show:**
```
REACT_APP_API_URL=https://xxxx-xxxx-xxxx.ngrok-free.app
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_...
```

**If missing or wrong:**
- Update the file with correct ngrok backend URL
- Restart frontend

### 2. Check Backend settings.py

```bash
cd backend-growfund
grep "ALLOWED_HOSTS" growfund/settings.py
grep "CORS_ALLOWED_ORIGINS" growfund/settings.py
```

**Should show:**
```python
ALLOWED_HOSTS = [..., 'xxxx-xxxx-xxxx.ngrok-free.app']
CORS_ALLOWED_ORIGINS = [..., 'https://yyyy-yyyy-yyyy.ngrok-free.app']
```

**If missing or wrong:**
- Update settings.py with correct ngrok URLs
- Restart backend

### 3. Check Ngrok Tunnels

**Terminal 3 (Backend):**
```bash
ngrok http 8000
```

**Should show:**
```
Forwarding    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

**Terminal 4 (Frontend):**
```bash
ngrok http 3000
```

**Should show:**
```
Forwarding    https://yyyy-yyyy-yyyy.ngrok-free.app -> http://localhost:3000
```

### 4. Check Services Running

**Backend:**
```bash
curl http://localhost:8000/api/
```

**Should return:** API response (not error)

**Frontend:**
```bash
curl http://localhost:3000
```

**Should return:** HTML page (not error)

---

## 🚨 Common Issues

### Issue 1: .env file doesn't exist

**Solution:**
```bash
cd Growfund-Dashboard/trading-dashboard
cat > .env << EOF
REACT_APP_API_URL=https://YOUR-NGROK-BACKEND-URL
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_id
EOF
```

Replace `YOUR-NGROK-BACKEND-URL` with your actual ngrok URL!

### Issue 2: .env has wrong URL

**Solution:**
```bash
# Edit .env
nano Growfund-Dashboard/trading-dashboard/.env

# Or use your editor to update REACT_APP_API_URL
```

### Issue 3: settings.py doesn't have ngrok URLs

**Solution:**
```bash
# Edit settings.py
nano backend-growfund/growfund/settings.py

# Find ALLOWED_HOSTS and add your ngrok URL
# Find CORS_ALLOWED_ORIGINS and add your ngrok URL
```

### Issue 4: Ngrok tunnels not running

**Solution:**
```bash
# Terminal 3
ngrok http 8000

# Terminal 4
ngrok http 3000
```

---

## 📋 Step-by-Step Fix

### Step 1: Get Your Ngrok URLs

**Terminal 3:**
```bash
ngrok http 8000
# Copy the HTTPS URL: https://xxxx-xxxx-xxxx.ngrok-free.app
```

**Terminal 4:**
```bash
ngrok http 3000
# Copy the HTTPS URL: https://yyyy-yyyy-yyyy.ngrok-free.app
```

### Step 2: Update Frontend .env

```bash
cd Growfund-Dashboard/trading-dashboard
```

Edit `.env` and set:
```
REACT_APP_API_URL=https://xxxx-xxxx-xxxx.ngrok-free.app
```

### Step 3: Update Backend settings.py

```bash
cd backend-growfund
```

Edit `growfund/settings.py` and update:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'xxxx-xxxx-xxxx.ngrok-free.app']
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'https://yyyy-yyyy-yyyy.ngrok-free.app']
```

### Step 4: Restart Services

**Terminal 1 (Backend):**
```bash
Ctrl+C
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 (Frontend):**
```bash
Ctrl+C
npm start
```

### Step 5: Test

1. Open: `https://yyyy-yyyy-yyyy.ngrok-free.app`
2. Try to login
3. Should work! ✅

---

## 🧪 Test API Call

Open browser console (F12) and run:

```javascript
// Test login endpoint
fetch('https://YOUR-NGROK-BACKEND-URL/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'admin001@gmail.com',
    password: 'Buffers316!'
  })
})
.then(r => r.json())
.then(d => console.log(d))
.catch(e => console.error(e))
```

**Should return:**
- Success: `{ access: "token...", refresh: "token..." }`
- Error: `{ detail: "Invalid credentials" }`

If you get CORS error, check settings.py CORS_ALLOWED_ORIGINS.

---

## ✅ Verification Checklist

- [ ] .env file exists
- [ ] .env has correct ngrok backend URL
- [ ] settings.py ALLOWED_HOSTS has ngrok URL
- [ ] settings.py CORS_ALLOWED_ORIGINS has ngrok frontend URL
- [ ] Backend is running
- [ ] Frontend is running
- [ ] Ngrok backend tunnel is running
- [ ] Ngrok frontend tunnel is running
- [ ] Browser cache cleared
- [ ] Login works ✅

---

## 🎯 If Still Not Working

1. **Check browser console** (F12) for errors
2. **Check network tab** to see API calls
3. **Check backend logs** for errors
4. **Check ngrok logs** at http://localhost:4040
5. **Verify all URLs** are correct
6. **Restart everything** (all 4 terminals)

---

## 📞 Need Help?

See **NGROK-LOGIN-FIX.md** for detailed troubleshooting.
