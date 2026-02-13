# Restart All Servers

## ✅ CORS Issue Fixed!

I've updated the Django settings to include your ngrok frontend URL:
- Added `https://fc75-105-160-17-43.ngrok-free.app` to CORS_ALLOWED_ORIGINS
- Added ngrok URL to ALLOWED_HOSTS

---

## 🚀 Restart Instructions

### Step 1: Stop All Services
```bash
# Stop all running services
# Press Ctrl+C in each terminal
```

### Step 2: Restart Backend

**Terminal 1:**
```bash
cd backend-growfund
python manage.py runserver 0.0.0.0:8000
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 3: Restart Frontend

**Terminal 2:**
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

You should see:
```
Compiled successfully!
```

### Step 4: Verify Ngrok Tunnels

**Terminal 3 & 4:**
```bash
# Keep your existing ngrok tunnels running
# They should still be active
```

---

## ✅ Verification

1. **Backend**: http://localhost:8000/api/
2. **Frontend**: http://localhost:3000
3. **Ngrok Frontend**: https://fc75-105-160-17-43.ngrok-free.app
4. **Monitor**: http://localhost:4040

---

## 🔧 What Was Fixed

### Before
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
]
```

### After
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'https://fc75-105-160-17-43.ngrok-free.app',  # ✅ Added
]
```

---

## 🧪 Test Login

1. Open: https://fc75-105-160-17-43.ngrok-free.app
2. Try to login with:
   - Email: admin001@gmail.com
   - Password: Buffers316!
3. Should work now! ✅

---

## 📝 Notes

- The ngrok URL is temporary and changes on restart
- If you restart ngrok, update settings.py with the new URL
- Keep monitoring at http://localhost:4040

---

## 🎯 Quick Restart Script

Create `restart-all.sh`:

```bash
#!/bin/bash

echo "🛑 Stopping all services..."
pkill -f "python manage.py runserver"
pkill -f "npm start"

sleep 2

echo "🚀 Starting backend..."
cd backend-growfund
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

sleep 3

echo "🚀 Starting frontend..."
cd ../Growfund-Dashboard/trading-dashboard
npm start &
FRONTEND_PID=$!

echo "✅ All services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Ngrok Frontend: https://fc75-105-160-17-43.ngrok-free.app"
echo "Monitor: http://localhost:4040"
```

Run it:
```bash
chmod +x restart-all.sh
./restart-all.sh
```

---

## ✨ You're Ready!

All servers are configured and ready to restart. The CORS error should be fixed! 🎉
