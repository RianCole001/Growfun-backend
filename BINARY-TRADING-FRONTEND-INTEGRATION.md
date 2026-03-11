# Binary Trading - Frontend Integration Guide

## 🔧 Backend Fix Applied

**Issue Fixed:** Missing import in `trade_service.py` causing real trades to fail.

**Status:** ✅ Both demo and real trades now work correctly and deduct balances.

---

## 📊 API Endpoints

### Base URL
```
http://localhost:8000/api/binary/
```

### 1. Get All Assets
```http
GET /api/binary/assets/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "assets": [
    {
      "id": "uuid",
      "symbol": "OIL",
      "name": "Crude Oil",
      "asset_type": "commodity",
      "base_payout": 85.00,
      "min_trade_amount": 10.00,
      "max_trade_amount": 5000.00
    }
  ]
}
```

### 2. Get Current Price (Single Asset)
```http
GET /api/binary/assets/OIL/price/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "symbol": "OIL",
  "price": 75.50,
  "timestamp": "2024-03-11T10:30:00Z"
}
```

### 3. Get All Prices (All Assets)
```http
GET /api/binary/prices/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "prices": {
    "OIL": {
      "symbol": "OIL",
      "name": "Crude Oil",
      "price": 75.50,
      "timestamp": "2024-03-11T10:30:00Z"
    },
    "GOLD": { ... },
    "BTC": { ... }
  }
}
```

### 4. Open Trade
```http
POST /api/binary/trades/open/
Authorization: Bearer {token}
Content-Type: application/json

{
  "asset_symbol": "OIL",
  "direction": "buy",
  "amount": 100,
  "expiry_seconds": 300,
  "is_demo": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Demo trade opened successfully",
  "trade": {
    "id": "uuid",
    "asset": {
      "symbol": "OIL",
      "name": "Crude Oil"
    },
    "direction": "buy",
    "amount": 100.00,
    "strike_price": 75.50,
    "adjusted_payout_percentage": 80.00,
    "expiry_seconds": 300,
    "expires_at": "2024-03-11T10:35:00Z",
    "status": "active",
    "is_demo": true
  },
  "new_balance": 9900.00,
  "is_demo": true
}
```

### 5. Get Active Trades
```http
GET /api/binary/trades/active/?is_demo=true
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "trades": [ ... ],
  "count": 3,
  "is_demo": true
}
```

### 6. Get Balances
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

## 🎮 Frontend Implementation

### Issue 1: Balance Not Deducting

**Problem:** Balance not updating after placing trade
**Solution:** Backend was fixed. Ensure frontend calls the correct endpoint and updates state.

```javascript
const openTrade = async (tradeData) => {
  try {
    const response = await axios.post('/api/binary/trades/open/', {
      asset_symbol: tradeData.asset,
      direction: tradeData.direction,
      amount: tradeData.amount,
      expiry_seconds: tradeData.expiry,
      is_demo: tradingMode === 'demo'
    });
    
    if (response.data.success) {
      // Update balance immediately
      if (tradingMode === 'demo') {
        setDemoBalance(response.data.new_balance);
      } else {
        setRealBalance(response.data.new_balance);
      }
      
      // Add trade to active trades
      setActiveTrades(prev => [...prev, response.data.trade]);
      
      toast.success('Trade opened!');
    }
  } catch (error) {
    toast.error(error.response?.data?.error || 'Failed to open trade');
  }
};
```

### Issue 2: Chart Becomes Dormant

**Problem:** Chart stops updating after placing trade
**Likely Causes:**
1. Price polling stops when trade is placed
2. Component re-renders and loses interval
3. API calls are being blocked

**Solution:** Implement robust price polling

```javascript
useEffect(() => {
  let priceInterval;
  
  const fetchPrices = async () => {
    try {
      const response = await axios.get('/api/binary/prices/');
      if (response.data.success) {
        setPrices(response.data.prices);
      }
    } catch (error) {
      console.error('Failed to fetch prices:', error);
    }
  };
  
  // Initial fetch
  fetchPrices();
  
  // Poll every 1 second
  priceInterval = setInterval(fetchPrices, 1000);
  
  // Cleanup on unmount
  return () => {
    if (priceInterval) {
      clearInterval(priceInterval);
    }
  };
}, []); // Empty dependency array - runs once on mount

// Update chart when prices change
useEffect(() => {
  if (prices[selectedAsset]) {
    updateChart(prices[selectedAsset].price);
  }
}, [prices, selectedAsset]);
```

### Complete Trading Component Example

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

const BinaryTrading = () => {
  const [tradingMode, setTradingMode] = useState('demo');
  const [realBalance, setRealBalance] = useState(0);
  const [demoBalance, setDemoBalance] = useState(10000);
  const [prices, setPrices] = useState({});
  const [selectedAsset, setSelectedAsset] = useState('OIL');
  const [activeTrades, setActiveTrades] = useState([]);
  
  // Fetch balances on mount
  useEffect(() => {
    fetchBalances();
  }, []);
  
  const fetchBalances = async () => {
    try {
      const response = await axios.get('/api/binary/balances/');
      setRealBalance(response.data.real_balance);
      setDemoBalance(response.data.demo_balance);
    } catch (error) {
      console.error('Failed to fetch balances:', error);
    }
  };
  
  // Price polling - NEVER STOPS
  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await axios.get('/api/binary/prices/');
        if (response.data.success) {
          setPrices(response.data.prices);
        }
      } catch (error) {
        console.error('Price fetch error:', error);
      }
    };
    
    fetchPrices(); // Initial
    const interval = setInterval(fetchPrices, 1000);
    
    return () => clearInterval(interval);
  }, []); // No dependencies - runs independently
  
  // Active trades polling
  useEffect(() => {
    const fetchActiveTrades = async () => {
      try {
        const response = await axios.get('/api/binary/trades/active/', {
          params: { is_demo: tradingMode === 'demo' }
        });
        setActiveTrades(response.data.trades);
      } catch (error) {
        console.error('Failed to fetch trades:', error);
      }
    };
    
    fetchActiveTrades(); // Initial
    const interval = setInterval(fetchActiveTrades, 2000);
    
    return () => clearInterval(interval);
  }, [tradingMode]);
  
  const openTrade = async (direction, amount, expiry) => {
    try {
      const response = await axios.post('/api/binary/trades/open/', {
        asset_symbol: selectedAsset,
        direction,
        amount,
        expiry_seconds: expiry,
        is_demo: tradingMode === 'demo'
      });
      
      if (response.data.success) {
        // Update balance
        if (tradingMode === 'demo') {
          setDemoBalance(response.data.new_balance);
        } else {
          setRealBalance(response.data.new_balance);
        }
        
        // Refresh active trades
        setActiveTrades(prev => [...prev, response.data.trade]);
        
        alert('Trade opened successfully!');
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to open trade');
    }
  };
  
  const currentBalance = tradingMode === 'demo' ? demoBalance : realBalance;
  const currentPrice = prices[selectedAsset]?.price || 0;
  
  return (
    <div>
      <div className="balance">
        {tradingMode === 'demo' ? '🎮 Demo' : '💰 Real'}: ${currentBalance.toFixed(2)}
      </div>
      
      <div className="price">
        {selectedAsset}: ${currentPrice.toFixed(2)}
      </div>
      
      <button onClick={() => openTrade('buy', 100, 300)}>
        BUY $100 (5min)
      </button>
      
      <button onClick={() => openTrade('sell', 100, 300)}>
        SELL $100 (5min)
      </button>
      
      <div className="active-trades">
        {activeTrades.map(trade => (
          <div key={trade.id}>
            {trade.asset.symbol} {trade.direction.toUpperCase()} ${trade.amount}
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## ✅ Checklist

### Backend (Fixed)
- ✅ Import error fixed in `trade_service.py`
- ✅ Demo trades deduct demo balance
- ✅ Real trades deduct real balance
- ✅ Balances update correctly on win/loss
- ✅ Price feed generates prices

### Frontend (To Implement)
- [ ] Call `/api/binary/prices/` every 1 second
- [ ] Update chart with new prices
- [ ] Don't stop polling when trade is placed
- [ ] Update balance from API response
- [ ] Poll active trades every 2 seconds
- [ ] Refresh balances when trades close

---

## 🐛 Debugging

### Check if backend is running
```bash
curl http://localhost:8000/api/binary/assets/
```

### Check if prices are updating
```bash
curl http://localhost:8000/api/binary/prices/
```

### Test opening a trade
```bash
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
```

---

## 📝 Summary

**Backend Status:** ✅ Fixed and working
**Balance Deduction:** ✅ Working correctly
**Chart Issue:** Frontend needs to maintain continuous price polling

The backend is now fully functional. The chart becoming dormant is a frontend issue - ensure price polling continues independently of trade actions.
