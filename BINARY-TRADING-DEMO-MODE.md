# Binary Trading - Demo Mode Implementation

## ✅ Demo Mode Complete!

The binary trading system now supports **completely separate demo and real trading modes**.

---

## 🎯 Key Features

### Complete Separation
✅ **Demo trades use demo balance** - Never touches real money
✅ **Real trades use real balance** - Completely isolated
✅ **Separate trade histories** - Demo and real trades don't mix
✅ **Separate statistics** - Only real trades affect user stats
✅ **Same trading experience** - Demo uses same house edge algorithm

### Demo Account
- **Initial Balance**: $10,000 (auto-created on first use)
- **Unlimited Practice**: Trade without risk
- **Real Prices**: Uses same live price feed
- **Real House Edge**: Experience actual trading conditions

---

## 🔌 API Changes

### 1. Open Trade (Updated)
```http
POST /api/binary/trades/open/
Authorization: Bearer {token}
Content-Type: application/json

{
  "asset_symbol": "OIL",
  "direction": "buy",
  "amount": 100.00,
  "expiry_seconds": 300,
  "is_demo": true    // NEW: Set to true for demo mode
}
```

**Response:**
```json
{
  "success": true,
  "message": "Demo trade opened successfully",
  "trade": {
    "id": "uuid",
    "asset_symbol": "OIL",
    "direction": "buy",
    "amount": 100.00,
    "is_demo": true,
    ...
  },
  "new_balance": 9900.00,
  "is_demo": true
}
```

### 2. Get Active Trades (Updated)
```http
GET /api/binary/trades/active/?is_demo=true
Authorization: Bearer {token}
```

**Query Parameters:**
- `is_demo=true` - Get demo trades
- `is_demo=false` or omit - Get real trades

**Response:**
```json
{
  "success": true,
  "trades": [...],
  "count": 3,
  "is_demo": true
}
```

### 3. Get Trade History (Updated)
```http
GET /api/binary/trades/history/?is_demo=true&limit=50&offset=0
Authorization: Bearer {token}
```

**Query Parameters:**
- `is_demo=true` - Get demo history
- `is_demo=false` or omit - Get real history
- `limit` - Number of trades to return
- `offset` - Pagination offset

**Response:**
```json
{
  "success": true,
  "trades": [...],
  "count": 50,
  "total": 150,
  "is_demo": true
}
```

### 4. Get Balances (NEW)
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

---

## 💻 Frontend Integration

### 1. Mode Switcher Component

```javascript
const [tradingMode, setTradingMode] = useState('demo'); // 'demo' or 'real'
const [realBalance, setRealBalance] = useState(0);
const [demoBalance, setDemoBalance] = useState(10000);

// Fetch balances
useEffect(() => {
  const fetchBalances = async () => {
    const response = await axios.get('/api/binary/balances/');
    setRealBalance(response.data.real_balance);
    setDemoBalance(response.data.demo_balance);
  };
  fetchBalances();
}, []);

// Mode switcher UI
<div className="mode-switcher">
  <button 
    className={tradingMode === 'demo' ? 'active' : ''}
    onClick={() => setTradingMode('demo')}
  >
    <span className="icon">🎮</span>
    Demo Mode
    <span className="balance">${demoBalance.toFixed(2)}</span>
  </button>
  
  <button 
    className={tradingMode === 'real' ? 'active' : ''}
    onClick={() => setTradingMode('real')}
  >
    <span className="icon">💰</span>
    Real Mode
    <span className="balance">${realBalance.toFixed(2)}</span>
  </button>
</div>
```

### 2. Open Trade with Mode

```javascript
const handleOpenTrade = async () => {
  try {
    const response = await axios.post('/api/binary/trades/open/', {
      asset_symbol: selectedAsset.symbol,
      direction: direction,
      amount: amount,
      expiry_seconds: expirySeconds,
      is_demo: tradingMode === 'demo'  // Pass mode flag
    });
    
    if (response.data.success) {
      // Update appropriate balance
      if (tradingMode === 'demo') {
        setDemoBalance(response.data.new_balance);
      } else {
        setRealBalance(response.data.new_balance);
      }
      
      showSuccess(`${tradingMode === 'demo' ? 'Demo' : 'Real'} trade opened!`);
      fetchActiveTrades();
    }
  } catch (error) {
    showError(error.response.data.error);
  }
};
```

### 3. Fetch Trades by Mode

```javascript
const fetchActiveTrades = async () => {
  const response = await axios.get('/api/binary/trades/active/', {
    params: { is_demo: tradingMode === 'demo' }
  });
  setActiveTrades(response.data.trades);
};

const fetchTradeHistory = async () => {
  const response = await axios.get('/api/binary/trades/history/', {
    params: { 
      is_demo: tradingMode === 'demo',
      limit: 50,
      offset: 0
    }
  });
  setTradeHistory(response.data.trades);
};
```

### 4. Display Current Balance

```javascript
const currentBalance = tradingMode === 'demo' ? demoBalance : realBalance;

<div className="balance-display">
  <span className="label">
    {tradingMode === 'demo' ? '🎮 Demo' : '💰 Real'} Balance:
  </span>
  <span className="amount">${currentBalance.toFixed(2)}</span>
</div>
```

---

## 🎨 UI Design Recommendations

### Mode Indicator Colors
```css
/* Demo Mode */
.demo-mode {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid #667eea;
}

.demo-badge {
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

/* Real Mode */
.real-mode {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: 2px solid #f5576c;
}

.real-badge {
  background: #f5576c;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}
```

### Mode Switcher
```css
.mode-switcher {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px;
  background: #f3f4f6;
  border-radius: 12px;
}

.mode-switcher button {
  flex: 1;
  padding: 15px;
  border: 2px solid transparent;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.mode-switcher button.active {
  border-color: #3b82f6;
  background: #eff6ff;
  transform: scale(1.05);
}

.mode-switcher .icon {
  font-size: 24px;
}

.mode-switcher .balance {
  font-size: 14px;
  font-weight: bold;
  color: #10b981;
}
```

### Trade Card with Mode Badge
```javascript
<div className={`trade-card ${trade.is_demo ? 'demo-mode' : 'real-mode'}`}>
  <div className="trade-header">
    <span className="asset">{trade.asset_symbol}</span>
    <span className={trade.is_demo ? 'demo-badge' : 'real-badge'}>
      {trade.is_demo ? '🎮 DEMO' : '💰 REAL'}
    </span>
  </div>
  {/* Rest of trade card */}
</div>
```

---

## 🔒 Security & Separation

### What's Guaranteed
✅ **Demo trades NEVER affect real balance**
✅ **Real trades NEVER affect demo balance**
✅ **Demo trades don't count in user statistics**
✅ **Separate trade histories**
✅ **Same house edge applies to both modes**

### Database Level
- `is_demo` field on every trade
- Separate balance fields (user.balance vs demo_account.balance)
- Filtered queries ensure no mixing

### Code Level
```python
# Opening trade
if is_demo:
    demo_account.balance -= amount  # Use demo balance
else:
    user.balance -= amount  # Use real balance

# Closing trade
if trade.is_demo:
    demo_account.balance += payout  # Return to demo
else:
    user.balance += payout  # Return to real

# Statistics
if not trade.is_demo:
    update_user_stats(trade)  # Only real trades count
```

---

## 📊 Admin Panel

### Filter by Mode
Admins can now filter trades by demo/real mode in Django admin:
- Filter: "Is demo" checkbox
- List display shows demo badge
- Separate statistics for demo vs real

---

## 🧪 Testing

### Test Demo Mode
```bash
# Open demo trade
curl -X POST http://localhost:8000/api/binary/trades/open/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "OIL",
    "direction": "buy",
    "amount": 100,
    "expiry_seconds": 300,
    "is_demo": true
  }'

# Get demo trades
curl http://localhost:8000/api/binary/trades/active/?is_demo=true \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get balances
curl http://localhost:8000/api/binary/balances/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Real Mode
```bash
# Open real trade (is_demo: false or omit)
curl -X POST http://localhost:8000/api/binary/trades/open/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "OIL",
    "direction": "buy",
    "amount": 100,
    "expiry_seconds": 300,
    "is_demo": false
  }'
```

---

## ✅ Migration Applied

The database has been updated with:
- `is_demo` field added to BinaryTrade model
- Default value: `False` (real mode)
- All existing trades marked as real trades

---

## 📝 Summary

**Demo Mode Features:**
- ✅ Separate $10,000 demo balance
- ✅ Practice trading without risk
- ✅ Same prices and house edge as real mode
- ✅ Separate trade histories
- ✅ Real trades don't affect demo, demo doesn't affect real
- ✅ Easy mode switching in frontend
- ✅ Clear visual indicators

**Perfect for:**
- New users learning the platform
- Testing strategies
- Practicing before real trading
- Demo accounts for marketing

**The system is now production-ready with full demo support!** 🚀
