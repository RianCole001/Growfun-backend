# Ngrok Setup Guide - Share Your GrowFund Project

## 🚀 What is Ngrok?

Ngrok creates a secure tunnel to your local machine, allowing you to share your project with others via a public URL.

---

## 📥 Step 1: Install Ngrok

### Windows
```bash
# Download from https://ngrok.com/download
# Or use Chocolatey
choco install ngrok
```

### Mac
```bash
brew install ngrok
```

### Linux
```bash
# Download from https://ngrok.com/download
# Or use snap
snap install ngrok
```

---

## 🔑 Step 2: Create Ngrok Account & Get Auth Token

1. Go to https://ngrok.com
2. Sign up for free account
3. Go to Dashboard → Auth Token
4. Copy your auth token
5. Run in terminal:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

---

## 🌐 Step 3: Share Backend (Django)

### Start Django Server
```bash
cd backend-growfund
python manage.py runserver 0.0.0.0:8000
```

### In New Terminal - Share Port 8000
```bash
ngrok http 8000
```

You'll see:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        us (United States)
Forwarding                    https://xxxx-xx-xxx-xxx-xx.ngrok.io -> http://localhost:8000
```

**Your Backend URL:** `https://xxxx-xx-xxx-xxx-xx.ngrok.io`

---

## 🎨 Step 4: Share Frontend (React)

### Start React Server
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

### In New Terminal - Share Port 3000
```bash
ngrok http 3000
```

You'll see:
```
Forwarding                    https://yyyy-yy-yyy-yyy-yy.ngrok.io -> http://localhost:3000
```

**Your Frontend URL:** `https://yyyy-yy-yyy-yyy-yy.ngrok.io`

---

## ⚙️ Step 5: Update Configuration

### Update Frontend .env
```bash
cd Growfund-Dashboard/trading-dashboard
```

Edit `.env`:
```
REACT_APP_API_URL=https://xxxx-xx-xxx-xxx-xx.ngrok.io
```

### Update Backend settings.py
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'xxxx-xx-xxx-xxx-xx.ngrok.io',  # Add your ngrok URL
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://yyyy-yy-yyy-yyy-yy.ngrok.io',  # Add your frontend ngrok URL
]
```

---

## 🔗 Step 6: Share URLs with Others

Send these URLs to people you want to share with:

**Frontend:** `https://yyyy-yy-yyy-yyy-yy.ngrok.io`
**Backend API:** `https://xxxx-xx-xxx-xxx-xx.ngrok.io/api`

---

## 📊 Step 7: Monitor Traffic

Ngrok provides a web interface to monitor requests:

```
http://localhost:4040
```

Visit this in your browser to see:
- All HTTP requests
- Request/response details
- Headers and body
- Performance metrics

---

## 🔒 Security Tips

1. **Don't share URLs publicly** - They're temporary and anyone can access
2. **Use authentication** - Require login for sensitive features
3. **Enable IP whitelist** (Pro feature) - Restrict access to specific IPs
4. **Monitor traffic** - Check http://localhost:4040 regularly
5. **Rotate URLs** - Ngrok URLs change when you restart

---

## 🛠️ Advanced: Custom Domain (Pro)

With Ngrok Pro, use custom domain:

```bash
ngrok http 8000 --domain=your-custom-domain.ngrok.io
```

---

## 📝 Complete Setup Script

Create `start-ngrok.sh`:

```bash
#!/bin/bash

# Start Backend
echo "Starting Django backend..."
cd backend-growfund
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo "Starting React frontend..."
cd ../Growfund-Dashboard/trading-dashboard
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Share Backend
echo "Sharing backend with ngrok..."
ngrok http 8000 --log=stdout &
NGROK_BACKEND_PID=$!

# Wait a bit
sleep 3

# Share Frontend in new terminal
echo "Sharing frontend with ngrok..."
ngrok http 3000 --log=stdout &
NGROK_FRONTEND_PID=$!

echo "All services running!"
echo "Monitor at: http://localhost:4040"
```

Run it:
```bash
chmod +x start-ngrok.sh
./start-ngrok.sh
```

---

## 🐛 Troubleshooting

### Issue: "ngrok: command not found"
```bash
# Reinstall ngrok
brew install ngrok  # Mac
choco install ngrok  # Windows
```

### Issue: "Invalid auth token"
```bash
# Get new token from https://ngrok.com/app/auth
ngrok config add-authtoken YOUR_NEW_TOKEN
```

### Issue: "Address already in use"
```bash
# Kill process on port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: CORS errors
- Update CORS_ALLOWED_ORIGINS in settings.py
- Add ngrok frontend URL
- Restart Django

### Issue: API not responding
- Check ngrok is running
- Check Django is running
- Check firewall settings
- Monitor at http://localhost:4040

---

## 📱 Test on Mobile

1. Get your frontend ngrok URL
2. Open on mobile browser
3. Test all features
4. Check console for errors

---

## 🎯 Quick Commands

```bash
# Share backend
ngrok http 8000

# Share frontend
ngrok http 3000

# Share with custom name
ngrok http 8000 --subdomain=growfund-backend

# Monitor traffic
http://localhost:4040

# Stop ngrok
Ctrl+C

# View ngrok config
ngrok config check
```

---

## 📊 Ngrok Plans

### Free
- 1 simultaneous tunnel
- 40 connections/minute
- 2 hour session limit
- Random URLs

### Pro ($5/month)
- 3 simultaneous tunnels
- Custom domains
- IP whitelist
- 30 day session limit

### Business ($20/month)
- 10 simultaneous tunnels
- Team management
- Advanced security
- Priority support

---

## ✅ Checklist

- [ ] Install ngrok
- [ ] Create ngrok account
- [ ] Get auth token
- [ ] Configure auth token
- [ ] Start Django backend
- [ ] Start React frontend
- [ ] Share backend with ngrok
- [ ] Share frontend with ngrok
- [ ] Update .env files
- [ ] Update settings.py
- [ ] Test URLs
- [ ] Share with others
- [ ] Monitor at http://localhost:4040

---

## 🚀 You're Ready!

Your GrowFund project is now shareable with anyone via ngrok URLs!
