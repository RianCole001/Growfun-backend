# Ngrok Troubleshooting Guide

## 🔴 Common Issues & Solutions

### Issue 1: "ngrok: command not found"

**Problem:** Ngrok is not installed or not in PATH

**Solutions:**

Windows (Chocolatey):
```bash
choco install ngrok
```

Mac (Homebrew):
```bash
brew install ngrok
```

Linux (Snap):
```bash
snap install ngrok
```

Verify installation:
```bash
ngrok version
```

---

### Issue 2: "Invalid auth token"

**Problem:** Auth token is wrong or expired

**Solutions:**

1. Get new token from https://ngrok.com/app/auth
2. Configure it:
```bash
ngrok config add-authtoken YOUR_NEW_TOKEN
```

3. Verify configuration:
```bash
ngrok config check
```

4. Check config file:
```bash
# Mac/Linux
cat ~/.ngrok2/ngrok.yml

# Windows
type C:\Users\YourUser\.ngrok2\ngrok.yml
```

---

### Issue 3: "Address already in use"

**Problem:** Port 8000 or 3000 is already in use

**Solutions:**

Windows:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID 1234 /F
```

Mac/Linux:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
lsof -ti:8000 | xargs kill -9
```

Or use different ports:
```bash
# Django on different port
python manage.py runserver 0.0.0.0:8001

# Share different port
ngrok http 8001
```

---

### Issue 4: CORS Errors

**Problem:** Frontend can't access backend API

**Error:** "Access to XMLHttpRequest blocked by CORS policy"

**Solutions:**

1. Update `backend-growfund/growfund/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-ngrok-frontend-url.ngrok.io',
]
```

2. Restart Django:
```bash
python manage.py runserver 0.0.0.0:8000
```

3. Check ngrok frontend URL is correct in .env

4. Clear browser cache (Ctrl+Shift+Delete)

---

### Issue 5: "Tunnel not found"

**Problem:** Ngrok tunnel is not responding

**Solutions:**

1. Check ngrok is running:
```bash
# Should show active tunnels
ngrok http 8000
```

2. Check backend is running:
```bash
# Terminal should show "Starting development server"
python manage.py runserver 0.0.0.0:8000
```

3. Check firewall:
```bash
# Windows Firewall might be blocking
# Add exception for Python and Node
```

4. Restart ngrok:
```bash
# Stop (Ctrl+C)
# Start again
ngrok http 8000
```

---

### Issue 6: "Connection refused"

**Problem:** Can't connect to backend through ngrok URL

**Solutions:**

1. Verify backend is running:
```bash
curl http://localhost:8000/api/
```

2. Check ngrok URL is correct:
```bash
# Should show your tunnel URL
ngrok http 8000
```

3. Check ALLOWED_HOSTS:
```python
# In settings.py
ALLOWED_HOSTS = ['localhost', 'your-ngrok-url.ngrok.io']
```

4. Check firewall:
```bash
# Disable temporarily to test
# Windows: Settings → Firewall
# Mac: System Preferences → Security
```

---

### Issue 7: "Session limit exceeded"

**Problem:** Free ngrok session expired (2 hour limit)

**Solutions:**

1. Restart ngrok:
```bash
ngrok http 8000
```

2. Upgrade to Pro ($5/month):
- 30 day session limit
- Custom domains
- IP whitelist

3. Use ngrok config for auto-restart:
```bash
# Create script to restart ngrok
```

---

### Issue 8: "Invalid request"

**Problem:** API requests are failing

**Solutions:**

1. Check request headers:
```bash
# Monitor at http://localhost:4040
# Check request/response details
```

2. Verify API endpoint:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-ngrok-url.ngrok.io/api/
```

3. Check authentication:
```python
# Verify token is valid
# Check user is authenticated
```

4. Check request body:
```bash
# Ensure JSON is valid
# Check content-type header
```

---

### Issue 9: "SSL certificate error"

**Problem:** SSL/TLS certificate issues

**Solutions:**

1. Ngrok uses self-signed certificates (normal)

2. Disable SSL verification (development only):
```javascript
// React
fetch(url, {
  headers: { 'Content-Type': 'application/json' }
  // SSL verification is automatic
})
```

3. Check certificate:
```bash
# Ngrok handles this automatically
# No action needed
```

---

### Issue 10: "Slow connection"

**Problem:** Ngrok tunnel is slow

**Solutions:**

1. Check internet speed:
```bash
# Run speed test
# Should have good upload/download
```

2. Check ngrok region:
```bash
# Use closest region
ngrok http 8000 --region=us
```

3. Monitor traffic:
```bash
# Check http://localhost:4040
# Look for slow requests
```

4. Reduce payload size:
```python
# Optimize API responses
# Compress data
```

---

## 🔧 Debugging Tools

### Monitor Traffic
```bash
# Open in browser
http://localhost:4040
```

### View Logs
```bash
# Mac/Linux
tail -f ~/.ngrok2/ngrok.log

# Windows
Get-Content C:\Users\YourUser\.ngrok2\ngrok.log -Tail 20 -Wait
```

### Test Endpoint
```bash
# Test backend
curl https://your-ngrok-url.ngrok.io/api/

# Test with auth
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-ngrok-url.ngrok.io/api/
```

### Check Configuration
```bash
ngrok config check
```

---

## 📋 Debugging Checklist

- [ ] Ngrok is installed
- [ ] Auth token is valid
- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 3000
- [ ] Ngrok tunnels are active
- [ ] ALLOWED_HOSTS is updated
- [ ] CORS_ALLOWED_ORIGINS is updated
- [ ] Frontend .env is updated
- [ ] Browser cache is cleared
- [ ] Firewall is not blocking
- [ ] Internet connection is stable
- [ ] Ngrok URLs are correct

---

## 🆘 Still Having Issues?

### Check These Files

1. **Backend settings.py**
```python
# Check ALLOWED_HOSTS
# Check CORS_ALLOWED_ORIGINS
# Check DEBUG setting
```

2. **Frontend .env**
```
# Check REACT_APP_API_URL
# Check it matches ngrok backend URL
```

3. **Ngrok logs**
```bash
# Check for errors
# Monitor at http://localhost:4040
```

### Get Help

1. Check ngrok documentation: https://ngrok.com/docs
2. Check Django documentation: https://docs.djangoproject.com
3. Check React documentation: https://react.dev
4. Check error messages carefully
5. Search Stack Overflow

---

## 🚀 Quick Fix Script

Create `fix-ngrok.sh`:

```bash
#!/bin/bash

echo "🔧 Fixing ngrok issues..."

# Kill existing processes
echo "Stopping existing services..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Clear cache
echo "Clearing cache..."
rm -rf ~/.ngrok2/ngrok.log

# Restart services
echo "Starting services..."
cd backend-growfund
python manage.py runserver 0.0.0.0:8000 &

sleep 3

cd ../Growfund-Dashboard/trading-dashboard
npm start &

sleep 5

echo "✅ Services restarted!"
echo "Start ngrok in new terminal:"
echo "ngrok http 8000"
```

Run it:
```bash
chmod +x fix-ngrok.sh
./fix-ngrok.sh
```

---

## ✅ You're Ready!

Most issues are resolved by:
1. Restarting services
2. Updating configuration
3. Clearing cache
4. Checking firewall

Good luck! 🚀
