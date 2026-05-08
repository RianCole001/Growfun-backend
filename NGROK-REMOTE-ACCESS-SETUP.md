# GrowFund - Remote Access Setup with ngrok

## Overview
This guide explains how to share your GrowFund application with remote users using ngrok tunnels.

## Your ngrok URLs
- **Frontend**: https://fdc9-129-222-147-116.ngrok-free.app → http://localhost:3000
- **Backend**: https://abd5-129-222-147-116.ngrok-free.app → http://localhost:8000

---

## ✅ Configuration Complete

### 1. Backend Configuration (Django)
**File**: `backend-growfund/growfund/settings.py`

✅ **ALLOWED_HOSTS**: Updated to include ngrok domain
```python
ALLOWED_HOSTS = ['*']  # Already allows all hosts
# Explicitly added: 'abd5-129-222-147-116.ngrok-free.app'
```

✅ **CORS Settings**: Already configured to allow all origins
```python
CORS_ALLOW_ALL_ORIGINS = True
```

### 2. Frontend Configuration (React)
**File**: `wazimu/Growfund-Dashboard/.env`

✅ **API URL**: Updated to use ngrok backend
```env
REACT_APP_API_URL=https://abd5-129-222-147-116.ngrok-free.app/api
REACT_APP_WS_URL=wss://abd5-129-222-147-116.ngrok-free.app
```

---

## 🚀 How to Share with Remote Users

### Step 1: Restart React App (REQUIRED)
The React app needs to be restarted to pick up the new `.env` configuration:

```bash
# Stop the current React app (Ctrl+C in the terminal)
# Then restart it:
cd wazimu/Growfund-Dashboard
npm start
```

**Important**: The React app must be restarted for environment variable changes to take effect!

### Step 2: Share the Frontend URL
Give your remote user this URL:
```
https://fdc9-129-222-147-116.ngrok-free.app
```

### Step 3: User Access
The remote user can now:
1. Open the URL in their browser
2. Register a new account or login
3. Use all features (deposits, investments, trading, etc.)
4. Admin users can access: `https://fdc9-129-222-147-116.ngrok-free.app/admin`

---

## 🔧 Troubleshooting

### Issue: "ngrok warning" banner appears
**Solution**: This is normal for free ngrok accounts. Users can click "Visit Site" to continue.

### Issue: API calls fail with CORS errors
**Solution**: 
1. Verify Django is running on port 8000
2. Check that ngrok backend tunnel is active
3. Ensure `.env` file has the correct backend URL
4. Restart React app after changing `.env`

### Issue: "Invalid Host header" error
**Solution**: Already fixed - ngrok domain added to `ALLOWED_HOSTS`

### Issue: Changes not reflecting
**Solution**: 
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Restart React app to reload `.env` variables

---

## 📋 Verification Checklist

Before sharing with users, verify:

- [ ] Django server is running on port 8000
- [ ] React app is running on port 3000
- [ ] Both ngrok tunnels are active
- [ ] React app was restarted after `.env` changes
- [ ] Frontend URL opens in browser
- [ ] Can login/register through the frontend
- [ ] API calls work (check browser console for errors)

---

## 🔍 Testing the Setup

### Test 1: Check Backend API
Open in browser:
```
https://abd5-129-222-147-116.ngrok-free.app/api/
```
Should see Django REST Framework API root.

### Test 2: Check Frontend
Open in browser:
```
https://fdc9-129-222-147-116.ngrok-free.app
```
Should see GrowFund landing page.

### Test 3: Test Login
1. Go to frontend URL
2. Click "Login" or "Get Started"
3. Try logging in with existing credentials
4. Check browser console for any API errors

---

## 🔐 Security Notes

### For Development/Demo Use Only
- ngrok free tier URLs are temporary and change when you restart ngrok
- Anyone with the URL can access your application
- Don't use for production or sensitive data

### Recommended for Production
- Use a proper domain name
- Set up SSL certificates
- Configure proper CORS origins (not `CORS_ALLOW_ALL_ORIGINS = True`)
- Use environment-specific settings
- Enable rate limiting and security headers

---

## 📱 Mobile Access

The ngrok URLs work on mobile devices too:
1. Share the frontend URL via SMS/WhatsApp/Email
2. User opens on their phone browser
3. Full responsive design works on mobile

---

## 🔄 When ngrok URLs Change

If you restart ngrok and get new URLs, update:

1. **Frontend `.env`**:
   ```env
   REACT_APP_API_URL=https://NEW-BACKEND-URL.ngrok-free.app/api
   ```

2. **Django settings.py** (if not using `*`):
   ```python
   ALLOWED_HOSTS.append('NEW-BACKEND-URL.ngrok-free.app')
   ```

3. **Restart React app** (required!)

---

## 💡 Tips for Demo/Testing

### Create Test Accounts
```bash
cd backend-growfund
python manage.py create_test_data
```

### Create Admin Account
```bash
python manage.py create_admin
```

### Monitor Requests
Watch Django console to see incoming API requests in real-time.

### Share Credentials
For demo purposes, you can share test credentials:
- **User**: demo@growfund.test / Demo1234!
- **Admin**: admin@growfund.com / (your admin password)

---

## 🎯 Quick Start Commands

```bash
# Terminal 1: Start Django
cd backend-growfund
python manage.py runserver

# Terminal 2: Start React (MUST RESTART after .env changes!)
cd wazimu/Growfund-Dashboard
npm start

# Terminal 3: Start ngrok for backend
ngrok http 8000

# Terminal 4: Start ngrok for frontend
ngrok http 3000
```

---

## 📞 Support

If remote users encounter issues:
1. Check Django console for backend errors
2. Check browser console (F12) for frontend errors
3. Verify ngrok tunnels are still active
4. Ensure both servers (Django + React) are running
5. Try clearing browser cache and hard refresh

---

## ✅ Current Status

- ✅ Backend configured for ngrok
- ✅ Frontend `.env` updated with ngrok backend URL
- ✅ CORS enabled for all origins
- ✅ ALLOWED_HOSTS includes ngrok domain
- ⚠️ **ACTION REQUIRED**: Restart React app to apply changes

---

## 🚀 Next Step

**RESTART YOUR REACT APP NOW:**
```bash
# In the terminal running React, press Ctrl+C to stop
# Then run:
npm start
```

After restart, share this URL with your remote user:
```
https://fdc9-129-222-147-116.ngrok-free.app
```

They can now access your GrowFund application from anywhere! 🎉
