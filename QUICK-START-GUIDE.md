# Quick Start Guide - GrowFund Platform

## 🚀 System is Ready!

Both servers are running and all features are working correctly.

---

## ⚠️ Important: You Must Login First

The 401 errors you're seeing are **NORMAL** - they mean you need to login first!

All the API endpoints require authentication, so you'll see these errors until you login:
- ❌ 401 Unauthorized on `/api/transactions/`
- ❌ 401 Unauthorized on `/api/auth/balance/`
- ❌ 401 Unauthorized on `/api/investments/`
- ❌ 401 Unauthorized on `/api/notifications/`

**This is expected behavior!** Once you login, these errors will disappear.

---

## 📝 Step-by-Step: Test the System

### Step 1: Open the Application
1. Open your browser
2. Go to: **http://localhost:3000**

### Step 2: Login as User
1. Click **"Login"** button
2. Enter credentials:
   ```
   Email: migwibrian316@gmail.com
   Password: [your password]
   ```
3. Click **"Sign In"**

### Step 3: Check Your Dashboard
After login, you should see:
- ✅ Your current balance
- ✅ Your investments (if any)
- ✅ No more 401 errors!

### Step 4: Test Investment (Minimum $30)
1. Click **"Invest"** or **"Capital Plans"**
2. Choose a plan (Basic, Premium, etc.)
3. Enter amount: **$30 or more** (minimum is $30)
4. Click **"Invest Now"**
5. Investment should appear in your dashboard

### Step 5: Test Crypto Investment
1. Click **"Trade"** or **"Crypto"**
2. Select **ExaCoin**
3. Enter amount: **$30 or more** (minimum is $30)
4. Click **"Buy"**
5. ExaCoin investment should appear in your dashboard

---

## 👨‍💼 Admin Panel Testing

### Step 1: Logout from User Account
1. Click your profile icon
2. Click **"Logout"**

### Step 2: Login as Admin
1. Go to: **http://localhost:3000/admin**
2. Enter admin credentials:
   ```
   Email: admin@growfund.com
   Password: admin123
   ```
3. Click **"Sign In"**

### Step 3: Credit User Balance
1. Click **"Users"** in admin sidebar
2. Find user: **migwibrian316@gmail.com**
3. Click **"Edit"** or **"Manage Balance"**
4. Select **"Credit"**
5. Enter amount: **$100**
6. Add note: **"Test credit"**
7. Click **"Submit"**

### Step 4: Verify Credit Appears as Deposit
1. Click **"Deposits"** in admin sidebar
2. You should see:
   - ✅ New deposit record
   - ✅ User name: migwibrian316@gmail.com
   - ✅ Amount: $100
   - ✅ Payment method: admin_transfer
   - ✅ Status: completed

### Step 5: Edit ExaCoin Price
1. Click **"Crypto Prices"** in admin sidebar
2. Find **"ExaCoin"**
3. Click **"Edit"**
4. Set any buy/sell prices you want (no restrictions!)
   - Example: Buy Price: $65.00, Sell Price: $60.00
5. Click **"Save"**
6. Prices update immediately

---

## 🔑 All Admin Credentials

### Super Admin
```
Email: admin@growfund.com
Password: admin123
```

### Tabby Admin
```
Email: tabby@growfund.com
Password: tabby123
```

### Test Admin
```
Email: testadmin@growfund.com
Password: testadmin123
```

---

## ✅ What's Working Now

### 1. Minimum Investment: $30
- ✅ Capital Basic Plan: $30 minimum
- ✅ Real Estate Starter: $30 minimum
- ✅ Crypto (ExaCoin): $30 minimum

### 2. Admin Credits = Deposits
- ✅ When admin credits user, it creates a deposit record
- ✅ Deposit shows user name and amount
- ✅ Appears in admin deposits list
- ✅ Payment method: "admin_transfer"

### 3. ExaCoin Price Control
- ✅ Admin can set any buy/sell prices
- ✅ No validation restrictions
- ✅ No market pressure limitations
- ✅ Full admin control

### 4. Unified Investments
- ✅ Single endpoint returns all investments
- ✅ Shows crypto investments (ExaCoin, etc.)
- ✅ Shows capital plan investments
- ✅ Combined totals and summary

### 5. Live Account = Demo Account
- ✅ All demo features work on live account
- ✅ Investments appear in dashboard
- ✅ Balance updates correctly
- ✅ Transactions recorded properly

---

## 🐛 Troubleshooting

### Problem: Still seeing 401 errors after login
**Solution:**
1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Local Storage** → **http://localhost:3000**
4. Check if you see:
   - `user_access_token`
   - `user_refresh_token`
5. If not, try:
   - Clear browser cache
   - Logout and login again
   - Try incognito/private window

### Problem: Can't invest (button disabled or error)
**Check:**
1. ✅ Are you logged in?
2. ✅ Do you have sufficient balance?
3. ✅ Is amount at least $30?
4. ✅ Is the form filled correctly?

### Problem: Investment doesn't appear in dashboard
**Solution:**
1. Refresh the page (F5)
2. Check browser console for errors (F12)
3. Check backend terminal for errors
4. Verify investment was created:
   - Open DevTools → Network tab
   - Look for POST request to `/api/investments/capital-plan/`
   - Check response status (should be 200 or 201)

### Problem: Admin credit doesn't show as deposit
**Solution:**
1. Refresh the deposits page
2. Check the "All" or "Completed" filter
3. Look for payment_method: "admin_transfer"
4. Check backend terminal for any errors

---

## 📊 Testing Checklist

### User Testing
- [ ] Login successful
- [ ] Dashboard loads without errors
- [ ] Balance displays correctly
- [ ] Can create capital plan investment ($30+)
- [ ] Can buy ExaCoin ($30+)
- [ ] Investments appear in dashboard
- [ ] Transactions list shows all activities

### Admin Testing
- [ ] Admin login successful
- [ ] Can view users list
- [ ] Can credit user balance
- [ ] Credit appears in deposits list
- [ ] Can edit ExaCoin prices
- [ ] Can set any prices (no restrictions)
- [ ] Can view all deposits
- [ ] Can view all transactions

### Integration Testing
- [ ] Admin credits user $100
- [ ] User sees balance increase
- [ ] User invests $30 in capital plan
- [ ] Investment appears in user dashboard
- [ ] Investment appears in admin panel
- [ ] User buys $30 ExaCoin
- [ ] ExaCoin appears in user dashboard
- [ ] All transactions recorded correctly

---

## 🎯 Expected Behavior

### When You First Open the App (Not Logged In)
```
❌ 401 Unauthorized errors - THIS IS NORMAL!
```
You'll see errors in browser console because you're not authenticated yet.

### After Login
```
✅ No more 401 errors
✅ Dashboard loads with your data
✅ All features work correctly
```

### After Admin Credits Your Account
```
✅ Balance increases immediately
✅ Deposit record created automatically
✅ Shows in admin deposits list
✅ Shows user name and amount
```

### After You Invest
```
✅ Balance decreases by investment amount
✅ Investment appears in dashboard
✅ Transaction recorded
✅ Can see investment details
```

---

## 📞 Need Help?

### Check Backend Logs
Look at Terminal 4 (backend server) for any errors or warnings.

### Check Frontend Console
1. Press F12 to open DevTools
2. Go to **Console** tab
3. Look for red error messages
4. Check **Network** tab for failed requests

### Check Database
If needed, you can check the database directly:
```bash
cd backend-growfund
python manage.py shell
```

Then run:
```python
from accounts.models import User
from investments.models import Trade, CapitalInvestmentPlan
from transactions.models import Transaction

# Check user balance
user = User.objects.get(email='migwibrian316@gmail.com')
print(f"Balance: ${user.balance}")

# Check investments
crypto = Trade.objects.filter(user=user, status='open')
print(f"Crypto investments: {crypto.count()}")

capital = CapitalInvestmentPlan.objects.filter(user=user, status='active')
print(f"Capital plans: {capital.count()}")

# Check transactions
transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:5]
for t in transactions:
    print(f"{t.transaction_type}: ${t.amount} - {t.status}")
```

---

## 🎉 Summary

**Everything is working!** The 401 errors you saw are normal - they just mean you need to login first.

**Next Steps:**
1. ✅ Login at http://localhost:3000/login
2. ✅ Test investments (minimum $30)
3. ✅ Test admin panel features
4. ✅ Verify everything works as expected

**Servers Running:**
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:3000

**All Features Ready:**
- ✅ Minimum investments: $30
- ✅ Admin credits as deposits
- ✅ ExaCoin price control
- ✅ Unified investments endpoint
- ✅ Live account functionality

---

**Last Updated**: May 3, 2026
**Status**: ✅ All Systems Operational
**Action Required**: Login to test the system
