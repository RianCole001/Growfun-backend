# Binary Trading - Balance Update Flow

## ✅ How Balance Updates Work

The binary trading system automatically updates balances when trades are opened and closed, with complete separation between demo and real modes.

---

## 💰 Balance Flow

### Opening a Trade

**Demo Mode (`is_demo: true`):**
```
1. User has demo balance: $10,000
2. User opens trade: $100
3. Demo balance deducted: $10,000 - $100 = $9,900
4. Real balance unchanged: $5,000 (stays same)
```

**Real Mode (`is_demo: false`):**
```
1. User has real balance: $5,000
2. User opens trade: $100
3. Real balance deducted: $5,000 - $100 = $4,900
4. Demo balance unchanged: $10,000 (stays same)
```

### Closing a Trade - WIN

**Demo Mode:**
```
1. Trade amount: $100
2. Payout: 85%
3. Profit: $100 × 0.85 = $85
4. Demo balance updated: $9,900 + $100 (stake) + $85 (profit) = $10,085
5. Real balance unchanged
```

**Real Mode:**
```
1. Trade amount: $100
2. Payout: 85%
3. Profit: $100 × 0.85 = $85
4. Real balance updated: $4,900 + $100 (stake) + $85 (profit) = $5,085
5. Demo balance unchanged
```

### Closing a Trade - LOSS

**Demo Mode:**
```
1. Trade amount: $100
2. Loss: -$100 (stake already deducted)
3. Demo balance stays: $9,900 (no refund)
4. Real balance unchanged
```

**Real Mode:**
```
1. Trade amount: $100
2. Loss: -$100 (stake already deducted)
3. Real balance stays: $4,900 (no refund)
4. Demo balance unchanged
```

---

## 🔄 Complete Trade Example

### Demo Trade Example

```javascript
// Initial State
Real Balance: $5,000
Demo Balance: $10,000

// 1. Open Demo Trade
POST /api/binary/trades/open/
{
  "asset_symbol": "OIL",
  "direction": "buy",
  "amount": 100,
  "expiry_seconds": 300,
  "is_demo": true
}

Response:
{
  "success": true,
  "new_balance": 9900.00,  // Demo balance
  "is_demo": true
}

// After Opening
Real Balance: $5,000 (unchanged)
Demo Balance: $9,900 (deducted $100)

// 2. Trade Expires - WIN
// System automatically closes trade
// Strike Price: $75.50
// Final Price: $75.60 (price went up, BUY wins!)
// Payout: 85%
// Profit: $100 × 0.85 = $85

// After Winning
Real Balance: $5,000 (unchanged)
Demo Balance: $10,085 ($9,900 + $100 stake + $85 profit)
```

### Real Trade Example

```javascript
// Initial State
Real Balance: $5,000
Demo Balance: $10,000

// 1. Open Real Trade
POST /api/binary/trades/open/
{
  "asset_symbol": "OIL",
  "direction": "sell",
  "amount": 200,
  "expiry_seconds": 300,
  "is_demo": false
}

Response:
{
  "success": true,
  "new_balance": 4800.00,  // Real balance
  "is_demo": false
}

// After Opening
Real Balance: $4,800 (deducted $200)
Demo Balance: $10,000 (unchanged)

// 2. Trade Expires - LOSS
// Strike Price: $75.50
// Final Price: $75.60 (price went up, SELL loses!)
// Loss: -$200

// After Losing
Real Balance: $4,800 (stays same, stake already lost)
Demo Balance: $10,000 (unchanged)
```

---

## 📊 API Response Examples

### Get Balances
```http
GET /api/binary/balances/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "real_balance": 5000.00,
  "demo_balance": 10000.00
}
```

### After Opening Demo Trade
```json
{
  "success": true,
  "message": "Demo trade opened successfully",
  "trade": {
    "id": "uuid",
    "amount": 100.00,
    "is_demo": true,
    "status": "active"
  },
  "new_balance": 9900.00,  // Updated demo balance
  "is_demo": true
}
```

### After Winning Demo Trade
```http
GET /api/binary/balances/
```

**Response:**
```json
{
  "success": true,
  "real_balance": 5000.00,    // Unchanged
  "demo_balance": 10085.00    // Updated with profit
}
```

---

## 🎮 Frontend Implementation

### Display Both Balances

```javascript
const [realBalance, setRealBalance] = useState(0);
const [demoBalance, setDemoBalance] = useState(10000);
const [tradingMode, setTradingMode] = useState('demo');

// Fetch balances on mount
useEffect(() => {
  fetchBalances();
}, []);

const fetchBalances = async () => {
  const response = await axios.get('/api/binary/balances/');
  setRealBalance(response.data.real_balance);
  setDemoBalance(response.data.demo_balance);
};

// Display current balance based on mode
const currentBalance = tradingMode === 'demo' ? demoBalance : realBalance;

return (
  <div className="balance-display">
    <div className="mode-indicator">
      {tradingMode === 'demo' ? '🎮 Demo Mode' : '💰 Real Mode'}
    </div>
    <div className="balance">
      ${currentBalance.toFixed(2)}
    </div>
  </div>
);
```

### Update Balance After Trade

```javascript
const handleOpenTrade = async () => {
  try {
    const response = await axios.post('/api/binary/trades/open/', {
      asset_symbol: 'OIL',
      direction: 'buy',
      amount: 100,
      expiry_seconds: 300,
      is_demo: tradingMode === 'demo'
    });
    
    if (response.data.success) {
      // Update appropriate balance immediately
      if (tradingMode === 'demo') {
        setDemoBalance(response.data.new_balance);
      } else {
        setRealBalance(response.data.new_balance);
      }
      
      showSuccess('Trade opened!');
    }
  } catch (error) {
    showError(error.response.data.error);
  }
};

// Poll for balance updates (when trades close)
useEffect(() => {
  const interval = setInterval(() => {
    fetchBalances();  // Refresh balances every 5 seconds
  }, 5000);
  
  return () => clearInterval(interval);
}, []);
```

### Real-Time Balance Updates

```javascript
// Check for closed trades and update balance
useEffect(() => {
  const checkClosedTrades = async () => {
    const response = await axios.get('/api/binary/trades/active/', {
      params: { is_demo: tradingMode === 'demo' }
    });
    
    const activeTrades = response.data.trades;
    
    // If any trade just closed, refresh balance
    if (activeTrades.length < previousTradeCount) {
      fetchBalances();
      showNotification('Trade closed! Balance updated.');
    }
    
    setPreviousTradeCount(activeTrades.length);
  };
  
  const interval = setInterval(checkClosedTrades, 2000);
  return () => clearInterval(interval);
}, [tradingMode, previousTradeCount]);
```

---

## ✅ Guaranteed Behavior

### Demo Mode
✅ **Opening trade**: Demo balance decreases
✅ **Winning trade**: Demo balance increases (stake + profit)
✅ **Losing trade**: Demo balance stays same (stake already lost)
✅ **Real balance**: NEVER affected

### Real Mode
✅ **Opening trade**: Real balance decreases
✅ **Winning trade**: Real balance increases (stake + profit)
✅ **Losing trade**: Real balance stays same (stake already lost)
✅ **Demo balance**: NEVER affected

---

## 🔒 Code Implementation

### Backend (Already Implemented)

```python
# Opening Trade
if is_demo:
    demo_account.balance -= amount  # Deduct from demo
else:
    user.balance -= amount  # Deduct from real

# Closing Trade - WIN
if won:
    profit = amount * (payout_percentage / 100)
    if trade.is_demo:
        demo_account.balance += (amount + profit)  # Return to demo
    else:
        user.balance += (amount + profit)  # Return to real

# Closing Trade - LOSS
# No refund, stake already deducted
```

---

## 📝 Summary

**The system automatically handles balance updates:**

1. ✅ **Opening trade** → Balance deducted immediately
2. ✅ **Winning trade** → Balance increased (stake + profit)
3. ✅ **Losing trade** → No change (stake already lost)
4. ✅ **Demo/Real separation** → Completely isolated
5. ✅ **Real-time updates** → Balance reflects immediately

**No manual intervention needed - it's all automatic!** 🚀
