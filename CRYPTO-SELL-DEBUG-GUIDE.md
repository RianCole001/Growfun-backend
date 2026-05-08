# Crypto Sell 400 Error - Debug Guide

## Current Status

**Error**: `POST /api/investments/crypto/sell/ 400 (Bad Request)`

## What We Know

### ✅ Backend Setup is Correct
- EXACOIN has AdminCryptoPrice set:
  - Buy Price: $40.00
  - Sell Price: $18.00
  - Active: True
- There are 2 open EXACOIN trades for user `migwibrian316@gmail.com`
- Trade IDs are valid UUIDs

### ❓ What's Causing the 400 Error

The backend expects:
```python
investment_id = request.data.get('investment_id')  # Must not be None/empty
coin = request.data.get('coin', '').upper()        # Must not be empty
quantity = Decimal(str(request.data.get('quantity', 0)))  # Must not be 0

if not all([investment_id, coin, quantity]):
    return 400 error
```

## Debugging Steps

### Step 1: Check Browser Console
Open browser console (F12) and look for the actual request data being sent.

**What to look for**:
```javascript
Sending sell request with data: {
  investment_id: "...",  // Should be a UUID
  coin: "EXACOIN",       // Should be uppercase
  quantity: 0.5          // Should be > 0
}
```

### Step 2: Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Click "Sell" button
4. Find the `/api/investments/crypto/sell/` request
5. Click on it
6. Check "Payload" or "Request" tab

**Expected Payload**:
```json
{
  "investment_id": "07bfcf59-e86b-4267-8883-31972a3d16ae",
  "coin": "EXACOIN",
  "quantity": 0.5
}
```

### Step 3: Check Response
In the same Network request, check the "Response" tab.

**Possible Error Messages**:
1. `"Missing required fields: investment_id, coin, quantity"` 
   - One of the fields is missing or falsy
   
2. `"EXACOIN is not available for trading or price not set by admin"`
   - AdminCryptoPrice not found (unlikely, we verified it exists)
   
3. `"Crypto investment not found"`
   - Trade doesn't exist or doesn't belong to current user

### Step 4: Verify You're Logged In
Check if you're logged in as the user who owns the EXACOIN trades.

**Current EXACOIN owner**: `migwibrian316@gmail.com`

If you're logged in as a different user, you won't be able to sell those trades.

## Common Issues & Solutions

### Issue 1: `investment_id` is undefined
**Symptom**: `investmentIds[0]` is undefined

**Cause**: The `investmentIds` array is empty

**Solution**: Check Portfolio component's `cryptoHoldings` calculation:
```javascript
cryptoHoldings[coin].investmentIds.push(inv.id);
```

Make sure `inv.id` exists in the investment data from backend.

### Issue 2: `quantity` is 0
**Symptom**: Quantity is 0 or NaN

**Cause**: `sellAmount` input is empty or invalid

**Solution**: Verify the sell modal input has a valid number

### Issue 3: Wrong user
**Symptom**: "Crypto investment not found"

**Cause**: Logged in as different user than trade owner

**Solution**: 
1. Check who you're logged in as
2. Check who owns the trades (see test output above)
3. Either login as correct user or buy EXACOIN with current user first

### Issue 4: Trade already closed
**Symptom**: "Crypto investment not found"

**Cause**: Trade status is 'closed' not 'open'

**Solution**: Buy new EXACOIN to create an open trade

## Quick Fix: Add Console Logging

### In Portfolio.js (around line 245-260)
Add logging before the sell call:
```javascript
console.log('=== SELL DEBUG ===');
console.log('Selected Holding:', selectedHolding);
console.log('Investment IDs:', selectedHolding.investmentIds);
console.log('Sell Data:', {
  investment_id: selectedHolding.investmentIds[0],
  coin: selectedHolding.coin,
  quantity: sellQuantity
});
```

### In AppNew.js (around line 543)
Add logging in handleSellCrypto:
```javascript
console.log('=== SELL REQUEST ===');
console.log('Sell Data:', sellData);
console.log('User:', user);
```

## Testing with Correct User

### Option 1: Login as migwibrian316@gmail.com
If you have access to this account, login and try selling.

### Option 2: Buy EXACOIN with Current User
1. Go to Crypto page
2. Buy some EXACOIN
3. Go to Portfolio
4. Try selling the EXACOIN you just bought

### Option 3: Create Test Trade
Run this in Django shell:
```python
from django.contrib.auth import get_user_model
from investments.models import Trade
from decimal import Decimal

User = get_user_model()

# Get your current user (replace email)
user = User.objects.get(email='your-email@example.com')

# Create a test trade
trade = Trade.objects.create(
    user=user,
    asset='EXACOIN',
    trade_type='buy',
    entry_price=Decimal('40.00'),
    current_price=Decimal('18.00'),
    quantity=Decimal('1.0'),
    status='open'
)

print(f"Created trade: {trade.id}")
```

## Expected Working Flow

1. **User buys EXACOIN**:
   - Trade created with status='open'
   - Trade ID stored in database

2. **Frontend fetches investments**:
   - `/api/investments/all/` returns investment with `id` field
   - Portfolio groups by coin and stores IDs in `investmentIds` array

3. **User clicks Sell**:
   - Modal opens with holding data
   - `selectedHolding.investmentIds[0]` contains Trade UUID

4. **User confirms sell**:
   - Frontend sends: `{investment_id, coin, quantity}`
   - Backend validates and processes
   - Returns success with new balance

## Next Steps

1. **Add console logging** to see what data is being sent
2. **Check Network tab** to see actual request payload
3. **Verify user** matches trade owner
4. **Check response** to see exact error message

Once you have the console logs, we can identify the exact issue!
