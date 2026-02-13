# Ngrok Complete Setup - Share Your GrowFund Project

## 📚 Documentation Created

I've created 4 comprehensive guides for using ngrok:

1. **NGROK-QUICK-START.md** - Get started in 5 minutes
2. **NGROK-SETUP-GUIDE.md** - Complete detailed guide
3. **NGROK-CONFIG-TEMPLATE.md** - Configuration templates
4. **NGROK-TROUBLESHOOTING.md** - Fix common issues

---

## ⚡ Quick Start (5 Minutes)

### 1. Install Ngrok
```bash
# Windows
choco install ngrok

# Mac
brew install ngrok

# Linux
snap install ngrok
```

### 2. Get Auth Token
- Go to https://ngrok.com
- Sign up (free)
- Copy auth token
- Run: `ngrok config add-authtoken YOUR_TOKEN`

### 3. Start Services
```bash
# Terminal 1 - Backend
cd backend-growfund
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - Frontend
cd Growfund-Dashboard/trading-dashboard
npm start
```

### 4. Share with Ngrok
```bash
# Terminal 3 - Backend
ngrok http 8000

# Terminal 4 - Frontend
ngrok http 3000
```

### 5. Update Configuration
**Backend (settings.py):**
```python
ALLOWED_HOSTS = ['localhost', 'xxxx-xxxx.ngrok.io']
CORS_ALLOWED_ORIGINS = ['https://yyyy-yyyy.ngrok.io']
```

**Frontend (.env):**
```
REACT_APP_API_URL=https://xxxx-xxxx.ngrok.io
```

### 6. Share URLs
- Frontend: `https://yyyy-yyyy.ngrok.io`
- Backend: `https://xxxx-xxxx.ngrok.io`

---

## 🎯 What You Get

### Public URLs
- Anyone can access your project
- No need for deployment
- Perfect for demos and testing
- Share with team members

### Monitoring
- View all requests at http://localhost:4040
- See request/response details
- Debug API calls
- Monitor performance

### Security
- HTTPS by default
- Temporary URLs (change on restart)
- Can add basic auth
- IP whitelist (Pro feature)

---

## 📊 Architecture

```
Your Computer
├── Backend (Django) - Port 8000
│   └── Ngrok Tunnel → https://xxxx-xxxx.ngrok.io
├── Frontend (React) - Port 3000
│   └── Ngrok Tunnel → https://yyyy-yyyy.ngrok.io
└── Ngrok Monitor - Port 4040
    └── http://localhost:4040

Others' Computers
├── Browser → https://yyyy-yyyy.ngrok.io (Frontend)
└── API Calls → https://xxxx-xxxx.ngrok.io (Backend)
```

---

## 🔄 Complete Workflow

### Step 1: Install & Setup (5 min)
```bash
# Install ngrok
brew install ngrok  # or choco/snap

# Get auth token from https://ngrok.com
ngrok config add-authtoken YOUR_TOKEN
```

### Step 2: Start Backend (2 min)
```bash
cd backend-growfund
python manage.py runserver 0.0.0.0:8000
```

### Step 3: Start Frontend (2 min)
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

### Step 4: Create Ngrok Tunnels (2 min)
```bash
# Terminal 3
ngrok http 8000

# Terminal 4
ngrok http 3000
```

### Step 5: Update Configuration (3 min)
- Update settings.py with ngrok URLs
- Update .env with API URL
- Restart Django

### Step 6: Test & Share (2 min)
- Test at http://localhost:4040
- Share URLs with others
- Monitor traffic

**Total Time: ~15 minutes**

---

## 🔐 Security Considerations

### ✅ Safe to Do
- Share with trusted team members
- Use for internal testing
- Demo to clients
- Development and staging

### ⚠️ Be Careful
- Don't share URLs publicly
- Don't expose sensitive data
- Use authentication
- Monitor traffic regularly

### 🔒 Pro Features (Paid)
- IP whitelist
- Custom domains
- Basic authentication
- Advanced security

---

## 📱 Testing Scenarios

### Desktop Testing
```bash
# Open in browser
https://yyyy-yyyy.ngrok.io
```

### Mobile Testing
```bash
# Get frontend URL
# Open on mobile browser
# Test all features
```

### API Testing
```bash
# Test with curl
curl https://xxxx-xxxx.ngrok.io/api/

# Test with Postman
# Import collection
# Update base URL to ngrok URL
```

### Team Testing
```bash
# Share frontend URL with team
# They can test in their browsers
# No installation needed
```

---

## 🛠️ Advanced Usage

### Custom Subdomain (Pro)
```bash
ngrok http 8000 --subdomain=growfund-backend
# URL: https://growfund-backend.ngrok.io
```

### Basic Authentication
```bash
ngrok http 8000 --basic-auth="user:pass"
```

### Multiple Tunnels
```bash
# Create ngrok.yml
# Configure multiple tunnels
ngrok start --all
```

### Custom Region
```bash
ngrok http 8000 --region=eu
# Faster for European users
```

---

## 📊 Monitoring & Debugging

### Web Interface
```bash
# Open in browser
http://localhost:4040

# View:
# - All HTTP requests
# - Request/response details
# - Headers and body
# - Performance metrics
```

### Command Line
```bash
# View logs
tail -f ~/.ngrok2/ngrok.log

# Verbose logging
ngrok http 8000 --log=stdout --log-level=debug
```

### Test Endpoint
```bash
# Test backend
curl https://xxxx-xxxx.ngrok.io/api/

# Test with auth
curl -H "Authorization: Bearer TOKEN" \
  https://xxxx-xxxx.ngrok.io/api/
```

---

## 🚀 Deployment Checklist

- [ ] Install ngrok
- [ ] Create ngrok account
- [ ] Get auth token
- [ ] Configure auth token
- [ ] Start Django backend
- [ ] Start React frontend
- [ ] Create backend tunnel
- [ ] Create frontend tunnel
- [ ] Update settings.py
- [ ] Update .env
- [ ] Test backend URL
- [ ] Test frontend URL
- [ ] Monitor at http://localhost:4040
- [ ] Share URLs with team
- [ ] Test on mobile
- [ ] Test API endpoints

---

## 💡 Pro Tips

1. **Keep URLs Private**
   - Don't share publicly
   - URLs change on restart
   - Anyone with URL can access

2. **Monitor Traffic**
   - Check http://localhost:4040 regularly
   - Look for suspicious requests
   - Monitor performance

3. **Use Meaningful Names**
   - Document which URL is which
   - Share clear instructions
   - Update team when URLs change

4. **Test Thoroughly**
   - Test all features
   - Test on different devices
   - Test with different users

5. **Keep Services Running**
   - Don't close terminals
   - Monitor for crashes
   - Restart if needed

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "ngrok: command not found" | Reinstall ngrok |
| "Invalid auth token" | Get new token from ngrok.com |
| "Address already in use" | Kill process on port or use different port |
| CORS errors | Update CORS_ALLOWED_ORIGINS in settings.py |
| "Connection refused" | Check backend is running |
| Slow connection | Check internet speed, use closest region |
| SSL errors | Normal, ngrok handles this |

See **NGROK-TROUBLESHOOTING.md** for detailed solutions.

---

## 📞 Support Resources

- **Ngrok Docs**: https://ngrok.com/docs
- **Ngrok Dashboard**: https://ngrok.com/app
- **Django Docs**: https://docs.djangoproject.com
- **React Docs**: https://react.dev

---

## 🎯 Next Steps

1. Read **NGROK-QUICK-START.md** (5 min)
2. Install ngrok
3. Get auth token
4. Start services
5. Create tunnels
6. Update configuration
7. Test and share!

---

## ✨ You're All Set!

Your GrowFund project is now ready to share with anyone via ngrok!

**Key Points:**
- ✅ Easy to set up (15 minutes)
- ✅ Free to use
- ✅ Secure HTTPS tunnels
- ✅ Perfect for demos
- ✅ Great for team collaboration
- ✅ Monitor all traffic
- ✅ No deployment needed

**Share your project now!** 🚀

---

## 📄 Documentation Files

1. **NGROK-QUICK-START.md** - 5 minute setup
2. **NGROK-SETUP-GUIDE.md** - Detailed guide
3. **NGROK-CONFIG-TEMPLATE.md** - Configuration templates
4. **NGROK-TROUBLESHOOTING.md** - Fix issues
5. **NGROK-COMPLETE-SETUP.md** - This file

All files are in your workspace root directory.
