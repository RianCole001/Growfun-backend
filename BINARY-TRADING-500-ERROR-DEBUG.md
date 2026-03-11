# Binary Trading - 500 Error Debugging Guide

## ✅ Backend Status

**Tested:** API is working correctly
**Test Result:** Trade opened successfully with 201 status
**Server Logs:** No 500 errors detected

```bash
# Test confirmed working:
POST /api/binary/trades/open/ → 201 Created
Response includes: new_balance, trade details, success: true
```

---

## 🔍 Possible Causes of 500 Error

### 1. Missing or Invalid Data in Request

**Check Frontend Request:**
```javascript
// Required fields
{
  "asset_symbol": "OIL",      // Must be valid: OIL, GOLD, BTC, ETH, EURUSD, GBPUSD
  "direction": "buy",         // Must be: "buy" or "sell"
  "amount": 100,              // Number, not string
  "expiry_seconds": 300,      // Number: 60, 180, 300, 600, 1800, 3600
  "is_demo": true             // Boolean, not string
}
```

**Common Mistakes:**
- ❌ `"amount": "100"` (string instead of number)
- ❌ `"is_demo": "true"` (string instead of boolean)
- ❌ `"asset_symbol": "oil"` (lowercase instead of uppercase)
- ❌ Missing `is_demo` field (defaults to false)

### 2. Authentication Token Issues

**Check Token:**
```javascript
// Token should be in headers
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}

// Token format from login response:
response.data.tokens.access  // ← Correct path
```

**Common Mistakes:**
- ❌ Using `response.data.access` (wrong path)
- ❌ Token expired (tokens expire after 1 hour)
- ❌ Missing "Bearer " prefix

### 3. Insufficient Balance

**Check Balance Before Trade:**
```javascript
// Get balances first
const balances = await axios.get('/api/binary/balances/');
const currentBalance = tradingMode === 'demo' 
  ? balances.data.demo_balance 
  : balances.data.real_balance;

// Validate before opening trade
if (amount > currentBalance) {
  alert('Insufficient balance');
  return;
}
```

### 4. Invalid Asset Symbol

**Valid Assets:**
- OIL (Crude Oil)
- GOLD (Gold)
- EURUSD (EUR/USD)
- GBPUSD (GBP/USD)
- BTC (Bitcoin)
- ETH (Ethereum)

**Check:**
```javascript
const validAssets = ['OIL', 'GOLD', 'EURUSD', 'GBPUSD', 'BTC', 'ETH'];
if (!validAssets.includes(assetSymbol.toUpperCase())) {
  console.error('Invalid asset:', assetSymbol);
}
```

---

## 🐛 Debugging Steps

### Step 1: Check Browser Console

```javascript
// Add detailed logging
const openTrade = async (tradeData) => {
  console.log('Opening trade with data:', tradeData);
  console.log('Trading mode:', tradingMode);
  console.log('Token:', token ? 'Present' : 'Missing');
  
  try {
    const response = await axios.post('/api/binary/trades/open/', tradeData);
    console.log('Success response:', response.data);
  } catch (error) {
    console.error('Error details:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
  }
};
```

### Step 2: Check Network Tab

1. Open DevTools → Network tab
2. Place a trade
3. Find the `/api/binary/trades/open/` request
4. Check:
   - Request Headers (Authorization present?)
   - Request Payload (data correct?)
   - Response (what error message?)

### Step 3: Verify Data Types

```javascript
// Ensure correct types
const tradeData = {
  asset_symbol: String(selectedAsset).toUpperCase(),
  direction: String(direction).toLowerCase(),
  amount: Number(amount),  // ← Convert to number
  expiry_seconds: Number(expirySeconds),  // ← Convert to number
  is_demo: Boolean(tradingMode === 'demo')  // ← Convert to boolean
};

console.log('Trade data types:', {
  asset_symbol: typeof tradeData.asset_symbol,
  direction: typeof tradeData.direction,
  amount: typeof tradeData.amount,
  expiry_seconds: typeof tradeData.expiry_seconds,
  is_demo: typeof tradeData.is_demo
});
```

### Step 4: Test with Curl

```bash
# Get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"TestPass123!"}'

# Use token to open trade
curl -X POST http://localhost:8000/api/binary/trades/open/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "OIL",
    "direction": "buy",
    "amount": 10,
    "expiry_seconds": 60,
    "is_demo": true
  }'
```

---

## 🔧 Frontend Fix Examples

### Fix 1: Ensure Correct Data Types

```javascript
// Before
const openTrade = async () => {
  const data = {
    asset_symbol: selectedAsset,
    direction: direction,
    amount: amountInput.value,  // ❌ String from input
    expiry_seconds: expiryInput.value,  // ❌ String from input
    is_demo: tradingMode === 'demo' ? 'true' : 'false'  // ❌ String
  };
};

// After
const openTrade = async () => {
  const data = {
    asset_symbol: selectedAsset.toUpperCase(),
    direction: direction.toLowerCase(),
    amount: parseFloat(amountInput.value),  // ✅ Number
    expiry_seconds: parseInt(expiryInput.value),  // ✅ Number
    is_demo: tradingMode === 'demo'  // ✅ Boolean
  };
};
```

### Fix 2: Add Validation

```javascript
const openTrade = async (amount, expiry) => {
  // Validate inputs
  if (!amount || amount <= 0) {
    toast.error('Invalid amount');
    return;
  }
  
  if (!expiry || expiry < 60) {
    toast.error('Minimum expiry is 60 seconds');
    return;
  }
  
  // Check balance
  const currentBalance = tradingMode === 'demo' ? demoBalance : realBalance;
  if (amount > currentBalance) {
    toast.error('Insufficient balance');
    return;
  }
  
  // Open trade
  try {
    const response = await axios.post('/api/binary/trades/open/', {
      asset_symbol: selectedAsset,
      direction: direction,
      amount: Number(amount),
      expiry_seconds: Number(expiry),
      is_demo: tradingMode === 'demo'
    });
    
    if (response.data.success) {
      // Update balance
      if (tradingMode === 'demo') {
        setDemoBalance(response.data.new_balance);
      } else {
        setRealBalance(response.data.new_balance);
      }
      toast.success('Trade opened!');
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || 'Failed to open trade';
    toast.error(errorMsg);
    console.error('Trade error:', error.response?.data);
  }
};
```

### Fix 3: Handle Token Refresh

```javascript
// Add axios interceptor for token refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired, refresh it
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('/api/token/refresh/', {
          refresh: refreshToken
        });
        
        const newToken = response.data.access;
        localStorage.setItem('accessToken', newToken);
        
        // Retry original request
        error.config.headers['Authorization'] = `Bearer ${newToken}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Refresh failed, logout user
        logout();
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 📋 Checklist

Before opening a trade, verify:

- [ ] Token is present in Authorization header
- [ ] Token format: `Bearer ${token}`
- [ ] `asset_symbol` is uppercase and valid
- [ ] `direction` is "buy" or "sell" (lowercase)
- [ ] `amount` is a number, not string
- [ ] `expiry_seconds` is a number, not string
- [ ] `is_demo` is a boolean, not string
- [ ] User has sufficient balance
- [ ] Content-Type header is application/json

---

## 🎯 Quick Test

Run this in browser console to test:

```javascript
// Test trade API
const testTrade = async () => {
  const token = localStorage.getItem('accessToken');
  
  const response = await fetch('http://localhost:8000/api/binary/trades/open/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      asset_symbol: 'OIL',
      direction: 'buy',
      amount: 10,
      expiry_seconds: 60,
      is_demo: true
    })
  });
  
  const data = await response.json();
  console.log('Status:', response.status);
  console.log('Response:', data);
};

testTrade();
```

---

## 📞 Still Getting 500 Error?

If error persists:

1. **Check backend logs:**
   ```bash
   # Look for error traceback in terminal running server
   ```

2. **Enable Django debug:**
   - Check `backend-growfund/growfund/settings.py`
   - Ensure `DEBUG = True`
   - Error details will show in response

3. **Test with provided script:**
   ```bash
   cd backend-growfund
   python test_api_call.py
   ```

4. **Check CORS settings:**
   - Verify frontend URL is in `CORS_ALLOWED_ORIGINS`
   - Check `settings.py` for CORS configuration

---

## ✅ Expected Behavior

**Successful Trade:**
```json
{
  "success": true,
  "message": "Demo trade opened successfully",
  "trade": { ... },
  "new_balance": 9990.00,
  "is_demo": true
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Insufficient balance"
}
```

Backend is confirmed working. The 500 error is likely a frontend data formatting issue.
