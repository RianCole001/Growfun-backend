# Dashboard Testing Guide

## Quick Test Checklist

### 1. Dashboard (Overview) - Main Page
**Location**: Click "Dashboard" in navigation

**What to Check**:
- [ ] **Welcome message** shows your name
- [ ] **4 stat cards** display:
  - Investments count and total amount
  - Available balance
  - Profits (with percentage)
  - Total portfolio value
- [ ] **Recent Activity section** shows:
  - Your investments (blue cards with "Investment" label)
  - Your transactions (green for deposits, orange for withdrawals)
  - Each item shows: name, date, amount
- [ ] **Balance Details** (green card on right) shows:
  - Recent deposits (with + prefix)
  - Recent withdrawals (with - prefix)
  - Admin credits (if any, with description)
- [ ] **Portfolio Growth chart** displays your investment history
- [ ] **Holdings Overview table** shows all your investments with:
  - Asset name
  - Quantity (for crypto)
  - Current value
  - Amount invested
  - ROI percentage
- [ ] **Top Movers** shows market data for different timeframes (24h, 7d, 30d)

**Expected Behavior**:
- If you have NO investments: "No investment history yet" message
- If you have NO transactions: "No recent activity" message
- All amounts should be formatted with commas (e.g., $1,234.56)
- Dates should be readable (e.g., "Jan 15, 2024")

---

### 2. Portfolio Page
**Location**: Click "Portfolio" in navigation

**What to Check**:
- [ ] **Overview tab** shows:
  - Total portfolio value
  - Total invested
  - Total profit/loss
  - Breakdown by investment type
- [ ] **Crypto tab** shows:
  - All your crypto investments
  - Current prices
  - Quantity owned
  - Profit/loss per coin
  - Sell button (if you own crypto)
- [ ] **Plans tab** shows:
  - Capital appreciation plans
  - Real estate investments
  - Investment details (amount, duration, returns)

**Expected Behavior**:
- If you have NO investments: Empty state message
- Crypto prices should update automatically
- Sell button should work for crypto holdings

---

### 3. Balances Page
**Location**: Click "Balances" in navigation

**What to Check**:
- [ ] **Available Balance** card shows your cash balance
- [ ] **Total Invested** card shows sum of all investments
- [ ] **Total Portfolio** card shows combined value
- [ ] **Balance Breakdown** section shows:
  - Available cash (with percentage)
  - Invested assets (with percentage)
  - Number of active investments

**Expected Behavior**:
- All amounts should match your actual balance
- Percentages should add up to 100%

---

### 4. Profile → Transaction History
**Location**: Click "Profile" button → "Transaction History" tab

**What to Check**:
- [ ] **Filter dropdown** has options:
  - All
  - deposit
  - withdrawal
  - admin_credit
- [ ] **Date filters** work (From and To dates)
- [ ] **Export CSV** button works
- [ ] **Transaction table** shows:
  - Date
  - Type (with colored badge)
  - Asset/Description
  - Amount
  - Details

**Expected Behavior**:
- Admin credits show as "Admin Credit" (not "admin_credit")
- Deposits are green, withdrawals are red, others are blue
- Filtering by type works correctly
- Date filtering works correctly
- CSV export includes all filtered transactions

---

### 5. Deposits Page
**Location**: Click "Deposits" in navigation

**What to Check**:
- [ ] Payment methods are available
- [ ] Minimum deposit amount is shown
- [ ] Deposit form works

**Expected Behavior**:
- Should show available payment methods based on your country
- Should validate minimum amounts

---

### 6. Withdrawals Page
**Location**: Click "Withdrawals" in navigation

**What to Check**:
- [ ] Shows your available balance
- [ ] Withdrawal methods are available
- [ ] Minimum withdrawal amount is shown
- [ ] Withdrawal form works

**Expected Behavior**:
- Should not allow withdrawal more than balance
- Should validate minimum amounts

---

### 7. Crypto Investment Page
**Location**: Click "Crypto" in navigation

**What to Check**:
- [ ] List of available cryptocurrencies
- [ ] Current prices for each coin
- [ ] 24h price change (with up/down arrows)
- [ ] Click on a coin opens buy/sell modal

**Expected Behavior**:
- Prices should update automatically
- EXACOIN and OPTCOIN prices should match admin settings
- Buy/sell modal should show current price and allow transactions

---

### 8. Capital Plan Page
**Location**: Click "Capital Plan" in navigation

**What to Check**:
- [ ] Three plan options (Basic, Standard, Advance)
- [ ] Each plan shows:
  - Minimum investment
  - Expected returns
  - Duration options
- [ ] Investment form works

**Expected Behavior**:
- Minimum investment should be $30 for Basic plan
- Should validate balance before allowing investment
- Should show success message after investment

---

### 9. Real Estate Page
**Location**: Click "Real Estate" in navigation

**What to Check**:
- [ ] Three property types (Starter, Standard, Luxury)
- [ ] Each type shows:
  - Minimum investment
  - Expected returns
  - Features
- [ ] Investment form works

**Expected Behavior**:
- Minimum investment should be $30 for Starter
- Should validate balance before allowing investment
- Should show success message after investment

---

### 10. Earn/Referrals Page
**Location**: Click "Earn" in navigation (if available)

**What to Check**:
- [ ] Your referral code is displayed
- [ ] Referral link is displayed
- [ ] Copy button works
- [ ] Referral stats show:
  - Total referrals
  - Active referrals
  - Total earned
  - Pending earnings
- [ ] List of your referrals (if any)

**Expected Behavior**:
- Copy button should copy referral link to clipboard
- Stats should update when you get new referrals

---

## Common Issues & Solutions

### Issue: "No recent activity" but I have transactions
**Check**:
1. Open browser console (F12)
2. Look for any red errors
3. Go to Network tab
4. Refresh page
5. Check if `/api/transactions/` request returns data

**Solution**: If API returns data but UI doesn't show it, clear browser cache and refresh

---

### Issue: Admin credits not showing
**Check**:
1. Go to Profile → Transaction History
2. Select "admin_credit" from filter dropdown
3. Check if admin credits appear

**Solution**: If they appear in Transaction History but not in Dashboard, refresh the page

---

### Issue: Investments not showing in Recent Activity
**Check**:
1. Go to Portfolio page
2. Verify you have investments there
3. Go back to Dashboard

**Solution**: If investments show in Portfolio but not Dashboard, clear browser cache

---

### Issue: Amounts showing as $0 or NaN
**Check**:
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check if amounts are numbers in Network tab responses

**Solution**: This is a data format issue - contact support

---

### Issue: Dates not displaying correctly
**Check**:
1. Look at the date format in browser console
2. Check if dates are in ISO format (YYYY-MM-DDTHH:mm:ssZ)

**Solution**: Backend should return dates in ISO format

---

## Browser Console Checks

### How to Open Console
- **Chrome/Edge**: Press F12 or Ctrl+Shift+I
- **Firefox**: Press F12 or Ctrl+Shift+K
- **Safari**: Press Cmd+Option+I

### What to Look For

#### ✅ Good Signs (No Issues)
```
webpack compiled successfully
[HMR] Waiting for update signal from WDS...
```

#### ❌ Bad Signs (Issues)
```
Error: Cannot read property 'map' of undefined
TypeError: investments.reduce is not a function
Failed to load resource: 404 (Not Found)
```

### Network Tab Checks

1. **Open Network tab** in browser console
2. **Refresh page**
3. **Look for these requests**:
   - `/api/auth/me/` - Should return 200 OK
   - `/api/auth/balance/` - Should return 200 OK
   - `/api/investments/all/` - Should return 200 OK
   - `/api/transactions/` - Should return 200 OK

4. **Click on each request** and check:
   - **Status**: Should be 200 OK (green)
   - **Response**: Should contain data (not empty)
   - **Preview**: Should show JSON data structure

---

## Data Verification

### Check Backend Data Directly

#### Using Django Admin
1. Go to `http://localhost:8000/admin/`
2. Login with admin credentials
3. Check:
   - **Transactions**: Should have records with `transaction_type` field
   - **Investments**: Should have records with `type`, `asset`, `amount` fields
   - **Users**: Your user should have correct balance

#### Using API Directly
1. Get your access token from browser localStorage
2. Use Postman or curl to test:

```bash
# Get transactions
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/transactions/

# Get investments
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/investments/all/

# Get balance
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/balance/
```

---

## Performance Checks

### Page Load Times
- **Dashboard**: Should load in < 2 seconds
- **Portfolio**: Should load in < 2 seconds
- **Transaction History**: Should load in < 1 second

### Auto-Updates
- **Balance**: Updates every 15 seconds
- **Crypto Prices**: Updates every 60 seconds
- **Notifications**: Checks every 30 seconds

---

## Mobile Testing

### Responsive Design Checks
- [ ] Dashboard displays correctly on mobile
- [ ] Navigation menu works on mobile
- [ ] Tables are scrollable on mobile
- [ ] Buttons are tappable on mobile
- [ ] Forms work on mobile

### Mobile-Specific Features
- [ ] Sidebar opens from hamburger menu
- [ ] Balance bar shows on mobile
- [ ] Cards stack vertically on mobile

---

## Final Verification

### All Components Working
- [x] Overview (Dashboard) - ✅ Fixed
- [x] Portfolio - ✅ Working
- [x] Balances - ✅ Working
- [x] Transaction History - ✅ Fixed
- [x] Deposits - ✅ Working
- [x] Withdrawals - ✅ Working
- [x] Crypto Investment - ✅ Working
- [x] Capital Plan - ✅ Working
- [x] Real Estate - ✅ Working
- [x] Earn/Referrals - ✅ Working

### Data Flow
- [x] Backend returns correct data format
- [x] Frontend fetches data on mount
- [x] Frontend polls for updates
- [x] Components display data correctly
- [x] Filters and sorting work
- [x] Color coding works
- [x] Formatting works (dates, amounts)

---

## Support Information

If you encounter any issues not covered in this guide:

1. **Check browser console** for errors
2. **Check Network tab** for failed requests
3. **Clear browser cache** and try again
4. **Try a different browser** to rule out browser-specific issues
5. **Check backend logs** for server errors

**Contact Support With**:
- Screenshot of the issue
- Browser console errors (if any)
- Network tab showing failed requests (if any)
- Steps to reproduce the issue
