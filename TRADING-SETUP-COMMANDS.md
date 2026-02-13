# Trading System - Setup Commands

## 🎯 One-Time Setup

### Step 1: Navigate to Backend
```bash
cd backend-growfund
```

### Step 2: Activate Virtual Environment
```bash
venv\Scripts\activate
```

### Step 3: Apply Migrations
```bash
py manage.py migrate investments
```

### Step 4: Verify Migrations
```bash
py manage.py showmigrations investments
```

Expected output:
```
investments
 [X] 0001_initial
```

### Step 5: Create Superuser (if needed)
```bash
py manage.py createsuperuser
```

---

## 🚀 Running the System

### Terminal 1: Start Backend
```bash
cd backend-growfund
venv\Scripts\activate
py manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Terminal 2: Start Frontend
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

Expected output:
```
Compiled successfully!
You can now view trading-dashboard in the browser.
  Local:            http://localhost:3000
```

---

## 🧪 Testing the API

### Get Your Access Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "password": "your_password"
  }'
```

Save the `access` token from response.

### Test 1: Create Gold Trade
```bash
curl -X POST http://localhost:8000/api/investments/trades/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "gold",
    "trade_type": "buy",
    "entry_price": 2050,
    "quantity": 0.5,
    "stop_loss": 2040,
    "take_profit": 2060,
    "timeframe": "1h"
  }'
```

### Test 2: Create USDT Trade
```bash
curl -X POST http://localhost:8000/api/investments/trades/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "usdt",
    "trade_type": "buy",
    "entry_price": 1.0,
    "quantity": 100,
    "stop_loss": 0.99,
    "take_profit": 1.01,
    "timeframe": "30m"
  }'
```

### Test 3: Get Open Trades
```bash
curl -X GET http://localhost:8000/api/investments/trades/open_trades/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 4: Get Trade History
```bash
curl -X GET http://localhost:8000/api/investments/trades/history/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 5: Close Trade (replace {trade_id})
```bash
curl -X POST http://localhost:8000/api/investments/trades/{trade_id}/close/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exit_price": 2055,
    "close_reason": "manual"
  }'
```

---

## 📊 Database Commands

### Check Migrations Status
```bash
py manage.py showmigrations investments
```

### Rollback Migrations (if needed)
```bash
py manage.py migrate investments zero
```

### Create Fresh Migrations
```bash
py manage.py makemigrations investments
py manage.py migrate investments
```

### Access Django Shell
```bash
py manage.py shell
```

Then in shell:
```python
from investments.models import Trade, TradeHistory
from django.contrib.auth import get_user_model

User = get_user_model()

# Get all trades
trades = Trade.objects.all()
print(f"Total trades: {trades.count()}")

# Get user's trades
user = User.objects.first()
user_trades = Trade.objects.filter(user=user)
print(f"User trades: {user_trades.count()}")

# Get open trades
open_trades = Trade.objects.filter(status='open')
print(f"Open trades: {open_trades.count()}")

# Exit shell
exit()
```

---

## 🔍 Debugging Commands

### Check Backend Logs
```bash
# Terminal running backend will show logs
# Look for errors or warnings
```

### Check Frontend Console
```
Press F12 in browser
Go to Console tab
Look for errors or warnings
```

### Test Database Connection
```bash
py manage.py dbshell
```

### Run Django System Check
```bash
py manage.py check
```

### Verify App Installation
```bash
py manage.py showmigrations
```

---

## 🧹 Cleanup Commands

### Delete All Trades (WARNING: Destructive)
```bash
py manage.py shell
```

Then in shell:
```python
from investments.models import Trade, TradeHistory

# Delete all trades
Trade.objects.all().delete()
TradeHistory.objects.all().delete()

print("All trades deleted")
exit()
```

### Clear Database Cache
```bash
py manage.py clear_cache
```

### Collect Static Files (for production)
```bash
py manage.py collectstatic --noinput
```

---

## 📦 Dependency Installation

### Install Backend Dependencies
```bash
cd backend-growfund
pip install -r requirements.txt
```

### Install Frontend Dependencies
```bash
cd Growfund-Dashboard/trading-dashboard
npm install
```

### Update Dependencies
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

---

## 🔐 Environment Setup

### Create .env file (if needed)
```bash
cd backend-growfund
```

Create `.env` file with:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 📱 Access Points

### Frontend
```
http://localhost:3000
```

### Backend API
```
http://localhost:8000/api/
```

### Django Admin
```
http://localhost:8000/admin/
```

### API Documentation (if available)
```
http://localhost:8000/api/docs/
```

---

## ✅ Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Migrations applied successfully
- [ ] Can login to frontend
- [ ] Can navigate to "Trade Now" page
- [ ] Can see Gold and USDT charts
- [ ] Can open a trade
- [ ] Can view open trades
- [ ] Can view trade history
- [ ] Can close a trade

---

## 🆘 Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'investments'"
**Fix:**
```bash
py manage.py migrate investments
```

### Issue: "No such table: investments_trade"
**Fix:**
```bash
py manage.py migrate investments
```

### Issue: "CORS error" in frontend
**Fix:** Backend CORS is already configured, ensure backend is running

### Issue: "401 Unauthorized" on API calls
**Fix:** Ensure you're using valid access token from login

### Issue: Charts not updating
**Fix:** Refresh page (F5) and check browser console

### Issue: "Port 8000 already in use"
**Fix:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
py manage.py runserver 8001
```

### Issue: "Port 3000 already in use"
**Fix:**
```bash
# Kill process or use different port
npm start -- --port 3001
```

---

## 📝 Quick Reference

### Most Used Commands

**Start Backend:**
```bash
cd backend-growfund && venv\Scripts\activate && py manage.py runserver
```

**Start Frontend:**
```bash
cd Growfund-Dashboard/trading-dashboard && npm start
```

**Apply Migrations:**
```bash
cd backend-growfund && py manage.py migrate investments
```

**Access Django Shell:**
```bash
cd backend-growfund && py manage.py shell
```

**Check Status:**
```bash
cd backend-growfund && py manage.py check
```

---

## 🎯 Next Steps

1. **Run Setup Commands** (above)
2. **Start Both Servers** (above)
3. **Login to Frontend** (http://localhost:3000)
4. **Navigate to Trade Now**
5. **Open a Test Trade**
6. **Monitor Real-Time Updates**
7. **Close Trade and Check History**

---

## 📚 Documentation

- **Complete Guide**: `TRADING-COMPLETE-GUIDE.md`
- **Setup Guide**: `TRADING-SYSTEM-SETUP.md`
- **Quick Start**: `TRADING-QUICK-START.md`
- **Implementation**: `TRADING-IMPLEMENTATION-SUMMARY.md`

---

## ✨ You're All Set!

Everything is ready to go. Just run the commands above and start trading! 🚀
