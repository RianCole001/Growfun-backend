# Stripe Testing on Localhost with Ngrok

## ✅ The Solution: Use Ngrok for HTTPS

Stripe requires HTTPS, but localhost is HTTP. Solution: Use ngrok to create an HTTPS tunnel to your localhost.

---

## 🚀 Quick Setup (10 Minutes)

### Step 1: Start Your Services

**Terminal 1 - Backend:**
```bash
cd backend-growfund
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

### Step 2: Create Ngrok Tunnels

**Terminal 3 - Backend Tunnel:**
```bash
ngrok http 8000
```

You'll see:
```
Forwarding    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000
```

**Terminal 4 - Frontend Tunnel:**
```bash
ngrok http 3000
```

You'll see:
```
Forwarding    https://yyyy-yyyy-yyyy.ngrok-free.app -> http://localhost:3000
```

### Step 3: Update Configuration

**Backend - settings.py:**
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'xxxx-xxxx-xxxx.ngrok-free.app',  # Add your ngrok backend URL
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://yyyy-yyyy-yyyy.ngrok-free.app',  # Add your ngrok frontend URL
]
```

**Frontend - .env:**
```
REACT_APP_API_URL=https://xxxx-xxxx-xxxx.ngrok-free.app
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key
```

### Step 4: Restart Services

```bash
# Restart backend (Ctrl+C then restart)
python manage.py runserver 0.0.0.0:8000

# Restart frontend (Ctrl+C then restart)
npm start
```

### Step 5: Test Stripe

1. Open: `https://yyyy-yyyy-yyyy.ngrok-free.app`
2. Go to Deposit section
3. Enter amount: $50
4. Click "Continue to Payment"
5. Enter test card: 4242 4242 4242 4242
6. Expiry: 12/25, CVC: 123
7. Click "Deposit $50"
8. Should work! ✅

---

## 🔄 Why This Works

```
Stripe (requires HTTPS)
    ↓
Frontend (ngrok HTTPS tunnel)
    ↓
Localhost (HTTP)
    ↓
Stripe Elements (works with HTTPS)
    ↓
Backend (ngrok HTTPS tunnel)
    ↓
Localhost (HTTP)
```

---

## 📋 Complete Checklist

- [ ] Start backend on port 8000
- [ ] Start frontend on port 3000
- [ ] Create ngrok backend tunnel (port 8000)
- [ ] Create ngrok frontend tunnel (port 3000)
- [ ] Update settings.py with ngrok URLs
- [ ] Update .env with ngrok URLs
- [ ] Restart backend
- [ ] Restart frontend
- [ ] Open ngrok frontend URL in browser
- [ ] Test with sandbox card

---

## 🧪 Test Cards

```
✅ Success
Card: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123

❌ Decline
Card: 4000 0000 0000 0002
Expiry: 12/25
CVC: 123
```

---

## 🔐 Important Notes

### Ngrok URLs Change on Restart
- Every time you restart ngrok, you get a new URL
- Update settings.py and .env with new URL
- Restart backend and frontend

### Stripe Test Mode
- Use `pk_test_` and `sk_test_` keys
- Test cards work only in test mode
- No real charges

### HTTPS Required
- Stripe requires HTTPS
- Ngrok provides HTTPS tunnel
- Localhost HTTP won't work

---

## 🚀 Full Workflow

```
1. Start Backend (port 8000)
   ↓
2. Start Frontend (port 3000)
   ↓
3. Create Ngrok Backend Tunnel
   ↓
4. Create Ngrok Frontend Tunnel
   ↓
5. Update settings.py with ngrok URLs
   ↓
6. Update .env with ngrok URLs
   ↓
7. Restart Backend
   ↓
8. Restart Frontend
   ↓
9. Open ngrok frontend URL
   ↓
10. Test Stripe payment
```

---

## 📊 Configuration Example

### Before (Localhost - Won't Work)
```
Frontend: http://localhost:3000
Backend: http://localhost:8000
API URL: http://localhost:8000/api
Stripe: ❌ Requires HTTPS
```

### After (Ngrok - Works!)
```
Frontend: https://yyyy-yyyy-yyyy.ngrok-free.app
Backend: https://xxxx-xxxx-xxxx.ngrok-free.app
API URL: https://xxxx-xxxx-xxxx.ngrok-free.app/api
Stripe: ✅ HTTPS tunnel
```

---

## 🆘 Troubleshooting

### Issue: "Stripe requires HTTPS"
**Solution:** Use ngrok to create HTTPS tunnel

### Issue: "CORS error"
**Solution:** Update CORS_ALLOWED_ORIGINS with ngrok frontend URL

### Issue: "API not responding"
**Solution:** Update .env with ngrok backend URL

### Issue: "Payment not processing"
**Solution:** Check ngrok URLs are correct, restart services

---

## 💡 Pro Tips

1. **Keep Ngrok Running** - Don't close ngrok terminals
2. **Monitor Traffic** - Check http://localhost:4040
3. **Update URLs** - When ngrok restarts, update config
4. **Test First** - Always test with sandbox cards
5. **Check Logs** - Monitor backend logs for errors

---

## 📝 Quick Reference

```bash
# Start backend
python manage.py runserver 0.0.0.0:8000

# Start frontend
npm start

# Create backend tunnel
ngrok http 8000

# Create frontend tunnel
ngrok http 3000

# Monitor traffic
http://localhost:4040
```

---

## ✨ You're Ready!

Now you can test Stripe on localhost using ngrok! 🎉

**Steps:**
1. Start services
2. Create ngrok tunnels
3. Update configuration
4. Restart services
5. Test with sandbox card

---

## 🎯 Next Steps

1. Follow the Quick Setup above
2. Test with sandbox card
3. Verify payment works
4. Check transaction in Stripe dashboard
5. Deploy to production when ready

---

## 📞 Resources

- **Ngrok Docs**: https://ngrok.com/docs
- **Stripe Docs**: https://stripe.com/docs
- **Stripe Testing**: https://stripe.com/docs/testing
