# 🎁 Referral System - Quick Start

## 5-Minute Setup

### Step 1: Apply Migration
```bash
cd backend-growfund
venv\Scripts\activate
py manage.py migrate accounts
```

### Step 2: Start Servers
```bash
# Terminal 1
py manage.py runserver

# Terminal 2
cd Growfund-Dashboard/trading-dashboard
npm start
```

### Step 3: Test It

1. **Login** to http://localhost:3000
2. **Go to Earn** component
3. **Copy referral code** (e.g., ABC12345)
4. **Open new browser/incognito**
5. **Visit**: http://localhost:3000/register?ref=ABC12345
6. **See green bonus banner** showing $5 reward
7. **Register** with new account
8. **Login as first user**
9. **Check Earn component** - see new referral
10. **Check balance** - increased by $5

---

## 🎯 How It Works

### User A (Referrer)
1. Gets automatic referral code on registration
2. Shares link: `http://localhost:3000/register?ref=CODE`
3. Gets $5 when User B registers with code
4. Tracks earnings in Earn component

### User B (Referred)
1. Clicks referral link
2. Sees $5 bonus banner on registration
3. Registers normally
4. User A gets $5 instantly

---

## 📊 Key Features

- ✅ Automatic referral code generation
- ✅ $5 reward per referral
- ✅ Instant reward claiming
- ✅ Real-time earnings tracking
- ✅ Referral status monitoring
- ✅ Reward tier system (5, 10, 25, 50 referrals)
- ✅ Copy-to-clipboard functionality
- ✅ Complete audit trail

---

## 🔗 API Endpoints

### Get Stats
```bash
curl -X GET http://localhost:8000/api/auth/referral-stats/ \
  -H "Authorization: Bearer TOKEN"
```

### Get Referrals
```bash
curl -X GET http://localhost:8000/api/auth/referrals/ \
  -H "Authorization: Bearer TOKEN"
```

### Register with Code
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "referral_code": "ABC12345"
  }'
```

---

## 📱 UI Components

### RegisterPage
- Referral code auto-filled from URL
- Green bonus banner
- Shows $5 reward
- Standard registration form

### Earn Component
- Referral code display
- Copy button
- Referral link
- Real-time stats
- Referral list
- Reward tiers

---

## ✅ Verification Checklist

- [ ] Migrations applied
- [ ] Backend running
- [ ] Frontend running
- [ ] Can see referral code in Earn
- [ ] Can copy referral code
- [ ] Can register with referral code
- [ ] See bonus banner on registration
- [ ] Reward credited to referrer
- [ ] Referral appears in Earn list
- [ ] Stats update in real-time

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Code not recognized | Verify code is 8 chars, user exists |
| Reward not showing | Refresh page, check API response |
| Can't see referrals | Login first, check browser console |
| Registration fails | Verify code is valid, check logs |

---

## 📚 Full Documentation

See: `REFERRAL-SYSTEM-GUIDE.md`

---

## 🎉 You're Ready!

Everything is set up and ready to use. Start earning referral rewards! 💰
