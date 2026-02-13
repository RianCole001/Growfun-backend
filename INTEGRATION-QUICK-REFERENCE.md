# Backend Integration - Quick Reference

## 🎯 What's Connected

✅ **Authentication** - Login, register, verify email
✅ **Profile** - Load, edit, save to backend
✅ **Settings** - Load, change, save to backend
✅ **Password** - Change password with backend validation
✅ **Referral** - Load code and referral list from backend
✅ **Balance** - Fetch from backend
✅ **Tokens** - JWT with automatic refresh

---

## 🚀 Quick Test

### Test 1: Login (30 seconds)
```
1. Open http://localhost:3000
2. Click "Go to Login Page"
3. Login: admin@growfund.com / Admin123!
4. ✓ Dashboard loads with real data
```

### Test 2: Update Profile (1 minute)
```
1. Click "Profile" → "Edit"
2. Change phone: +1234567890
3. Click "Save Changes"
4. ✓ Toast: "Profile updated successfully"
5. Refresh page → ✓ Data persists
```

### Test 3: Change Settings (1 minute)
```
1. Click "Settings"
2. Change currency: EUR
3. ✓ Toast: "Settings updated successfully"
4. Refresh page → ✓ Data persists
```

### Test 4: Referral Code (30 seconds)
```
1. Click "Earn"
2. ✓ Referral code displays
3. Copy link → ✓ Toast: "Copied to clipboard"
```

---

## 📊 Data Flow

```
Frontend (localhost:3000)
    ↓
API Service (api.js)
    ↓
Backend (localhost:8000)
    ↓
Database (SQLite)
```

---

## 🔐 Servers

| Service | Port | Status |
|---------|------|--------|
| Frontend | 3000 | ✅ Running |
| Backend | 8000 | ✅ Running |
| Database | - | ✅ SQLite |

---

## 📱 Test Credentials

```
Email: admin@growfund.com
Password: Admin123!
```

---

## 🔧 Configuration

### Frontend API
```javascript
// src/services/api.js
const API_BASE_URL = 'http://localhost:8000/api';
```

### Backend CORS
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
```

---

## 📋 Connected Components

| Component | Feature | Status |
|-----------|---------|--------|
| AppNew.js | Fetch user data | ✅ |
| Profile.js | Load & save profile | ✅ |
| Settings.js | Load & save settings | ✅ |
| Earn.js | Load referral data | ✅ |
| LoginPage.js | Backend login | ✅ |
| RegisterPage.js | Backend register | ✅ |

---

## 🧪 Verification

- [ ] Login works
- [ ] Profile loads from backend
- [ ] Profile updates save
- [ ] Settings load from backend
- [ ] Settings updates save
- [ ] Password changes work
- [ ] Referral code displays
- [ ] Data persists after refresh
- [ ] No console errors
- [ ] Toast notifications show

---

## 🐛 Troubleshooting

### CORS Error
```
Solution: Ensure Django running on port 8000
```

### Token Invalid
```
Solution: localStorage.clear() then login again
```

### Profile Not Updating
```
Solution: Check browser console for errors
```

### Settings Not Saving
```
Solution: Verify token in localStorage
```

---

## 📚 Documentation

- **BACKEND-INTEGRATION-GUIDE.md** - Full details
- **TEST-BACKEND-INTEGRATION.md** - Testing procedures
- **INTEGRATION-COMPLETE.md** - Complete summary

---

## 🎉 Ready to Test!

Open http://localhost:3000 and login to see real backend data.

