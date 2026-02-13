# Ngrok Configuration Templates

## 📝 Backend Settings Update

**File: `backend-growfund/growfund/settings.py`**

Add/Update these sections:

```python
# ALLOWED HOSTS - Add your ngrok URL
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '8000-your-ngrok-url.ngrok.io',  # Replace with your ngrok backend URL
]

# CORS Configuration - Add your ngrok frontend URL
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://3000-your-ngrok-url.ngrok.io',  # Replace with your ngrok frontend URL
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'https://3000-your-ngrok-url.ngrok.io',
]
```

---

## 🔧 Frontend .env Update

**File: `Growfund-Dashboard/trading-dashboard/.env`**

```
REACT_APP_API_URL=https://8000-your-ngrok-url.ngrok.io
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_id
```

---

## 🌐 Ngrok Configuration File

**File: `~/.ngrok2/ngrok.yml`** (or `C:\Users\YourUser\.ngrok2\ngrok.yml` on Windows)

```yaml
authtoken: YOUR_AUTH_TOKEN_HERE

tunnels:
  backend:
    proto: http
    addr: 8000
    bind_tls: true
    
  frontend:
    proto: http
    addr: 3000
    bind_tls: true
```

Then run:
```bash
ngrok start backend frontend
```

---

## 📋 Environment Variables

Create `.env.ngrok` for easy switching:

```bash
# Backend URLs
BACKEND_LOCAL=http://localhost:8000
BACKEND_NGROK=https://xxxx-xxxx-xxxx.ngrok.io

# Frontend URLs
FRONTEND_LOCAL=http://localhost:3000
FRONTEND_NGROK=https://yyyy-yyyy-yyyy.ngrok.io

# API URLs
API_LOCAL=http://localhost:8000/api
API_NGROK=https://xxxx-xxxx-xxxx.ngrok.io/api
```

---

## 🔄 Switching Between Local and Ngrok

### Script: `switch-to-ngrok.sh`

```bash
#!/bin/bash

# Update Django settings
echo "Updating Django settings for ngrok..."
BACKEND_URL=$1
FRONTEND_URL=$2

# Update settings.py
sed -i "s|'localhost'|'localhost', '$BACKEND_URL'|g" backend-growfund/growfund/settings.py
sed -i "s|'http://localhost:3000'|'http://localhost:3000', 'https://$FRONTEND_URL'|g" backend-growfund/growfund/settings.py

# Update frontend .env
echo "Updating React .env..."
echo "REACT_APP_API_URL=https://$BACKEND_URL" > Growfund-Dashboard/trading-dashboard/.env

echo "✅ Configuration updated!"
echo "Backend: https://$BACKEND_URL"
echo "Frontend: https://$FRONTEND_URL"
```

Usage:
```bash
chmod +x switch-to-ngrok.sh
./switch-to-ngrok.sh xxxx-xxxx-xxxx yyyy-yyyy-yyyy
```

---

## 🔐 Security Configuration

### Ngrok with IP Whitelist (Pro Feature)

```bash
ngrok http 8000 --ip-restriction=YOUR_IP_ADDRESS
```

### Ngrok with Basic Auth

```bash
ngrok http 8000 --basic-auth="username:password"
```

---

## 📊 Ngrok Configuration File (Advanced)

**File: `~/.ngrok2/ngrok.yml`**

```yaml
# Authentication
authtoken: YOUR_AUTH_TOKEN

# Logging
log_level: info
log_format: json
log_file: /var/log/ngrok.log

# Web interface
web_addr: 127.0.0.1:4040

# Tunnels
tunnels:
  backend:
    proto: http
    addr: 8000
    bind_tls: true
    inspect: true
    
  frontend:
    proto: http
    addr: 3000
    bind_tls: true
    inspect: true

# Region (optional)
region: us
```

---

## 🚀 Docker Compose with Ngrok

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend-growfund
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,backend
    command: python manage.py runserver 0.0.0.0:8000

  frontend:
    build: ./Growfund-Dashboard/trading-dashboard
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000
    depends_on:
      - backend

  ngrok:
    image: ngrok/ngrok:latest
    ports:
      - "4040:4040"
    environment:
      - NGROK_AUTHTOKEN=YOUR_AUTH_TOKEN
    command: ngrok start --all --config /etc/ngrok.yml
    volumes:
      - ./ngrok.yml:/etc/ngrok.yml
    depends_on:
      - backend
      - frontend
```

---

## 📱 Mobile Testing Setup

### Update settings.py for Mobile

```python
# Allow mobile devices
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'your-ngrok-url.ngrok.io',
    '*',  # Only for development!
]

# CORS for mobile
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-ngrok-url.ngrok.io',
    'http://*',  # Only for development!
]
```

### Test on Mobile

1. Get frontend ngrok URL
2. Open on mobile browser
3. Test all features
4. Check console for errors

---

## 🔍 Debugging Configuration

### Enable Verbose Logging

```bash
ngrok http 8000 --log=stdout --log-level=debug
```

### Monitor All Traffic

```bash
# View ngrok logs
tail -f ~/.ngrok2/ngrok.log

# Monitor at web interface
http://localhost:4040
```

---

## ✅ Configuration Checklist

- [ ] Install ngrok
- [ ] Get auth token
- [ ] Configure auth token
- [ ] Update ALLOWED_HOSTS
- [ ] Update CORS_ALLOWED_ORIGINS
- [ ] Update frontend .env
- [ ] Test backend URL
- [ ] Test frontend URL
- [ ] Monitor at http://localhost:4040
- [ ] Share URLs with team

---

## 🎯 Common Configurations

### Development (Local Only)
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
```

### Staging (Ngrok)
```python
ALLOWED_HOSTS = ['localhost', 'xxxx-xxxx.ngrok.io']
CORS_ALLOWED_ORIGINS = ['https://yyyy-yyyy.ngrok.io']
```

### Production (Real Domain)
```python
ALLOWED_HOSTS = ['growfund.com', 'www.growfund.com']
CORS_ALLOWED_ORIGINS = ['https://growfund.com']
```

---

## 🚀 You're Ready!

Use these templates to configure ngrok for your project!
