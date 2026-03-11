# Binary Trading - Frontend Integration Data

## 🎯 Quick Reference for Frontend Developers

### API Base URL
```
http://localhost:8000/api/binary/
```

### Authentication
All endpoints require JWT token in header:
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

---

## 📊 Data Structures

### Asset Object
```typescript
interface Asset {
  id: string;
  symbol: string;          // "OIL", "GOLD", "BTC", etc.
  name: string;            // "Crude Oil", "Gold", etc.
  asset_type: string;      // "commodity", "forex", "crypto"
  base_payout: number;     // 85.00
  volatility: number;      // 0.0050
  is_active: boolean;
  min_trade_amount: number; // 10.00
  max_trade_amount: number; // 5000.00
}
```

### Trade Object
```typescript
interface Trade {
  id: string;
  asset_symbol: string;
  asset_name: string;
  direction: 'buy' | 'sell';
  amount: number;
  strike_price: number;
  final_price: number | null;
  adjusted_payout_percentage: number;
  expiry_seconds: number;
  opened_at: string;        // ISO datetime
  expires_at: string;       // ISO datetime
  closed_at: string | null; // ISO datetime
  status: 'pending' | 'active' | 'won' | 'lost' | 'cancelled';
  profit_loss: number;
  time_remaining: number;   // seconds
  potential_profit: number;
}
```

### Stats Object
```typescript
interface TradingStats {
  total_trades: number;
  total_wins: number;
  total_losses: number;
  current_win_streak: number;
  max_win_streak: number;
  win_rate: number;         // percentage
  total_profit: number;
  total_loss: number;
  net_profit: number;
  total_volume: number;
}
```

---

## 🎨 UI Components Needed

### 1. Asset Selector
```javascript
const assets = [
  { symbol: 'OIL', name: 'Crude Oil', icon: '🛢️' },
  { symbol: 'GOLD', name: 'Gold', icon: '🥇' },
  { symbol: 'EURUSD', name: 'EUR/USD', icon: '💱' },
  { symbol: 'GBPUSD', name: 'GBP/USD', icon: '💱' },
  { symbol: 'BTC', name: 'Bitcoin', icon: '₿' },
  { symbol: 'ETH', name: 'Ethereum', icon: 'Ξ' }
];
```

### 2. Expiry Time Options
```javascript
const expiryOptions = [
  { value: 60, label: '1 Minute', icon: '⚡' },
  { value: 180, label: '3 Minutes', icon: '⏱️' },
  { value: 300, label: '5 Minutes', icon: '⏱️' },
  { value: 600, label: '10 Minutes', icon: '⏰' },
  { value: 1800, label: '30 Minutes', icon: '⏰' },
  { value: 3600, label: '1 Hour', icon: '🕐' }
];
```

### 3. Direction Buttons
```javascript
const directions = [
  { 
    value: 'buy', 
    label: 'BUY / CALL', 
    color: '#10b981',
    description: 'Price will go UP'
  },
  { 
    value: 'sell', 
    label: 'SELL / PUT', 
    color: '#ef4444',
    description: 'Price will go DOWN'
  }
];
```

---

## 🔄 Real-Time Updates

### Price Update Loop
```javascript
// Update prices every 1 second
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch('/api/binary/prices/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setPrices(data.prices);
  }, 1000);
  
  return () => clearInterval(interval);
}, [token]);
```

### Countdown Timer
```javascript
// Update countdown every second
useEffect(() => {
  const interval = setInterval(() => {
    setActiveTrades(prev => prev.map(trade => ({
      ...trade,
      time_remaining: Math.max(0, trade.time_remaining - 1)
    })));
  }, 1000);
  
  return () => clearInterval(interval);
}, []);
```

### Auto-Refresh Active Trades
```javascript
// Refresh active trades every 5 seconds
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch('/api/binary/trades/active/', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setActiveTrades(data.trades);
  }, 5000);
  
  return () => clearInterval(interval);
}, [token]);
```

---

## 💰 Amount Presets

```javascript
const amountPresets = [
  { value: 10, label: '$10' },
  { value: 25, label: '$25' },
  { value: 50, label: '$50' },
  { value: 100, label: '$100' },
  { value: 250, label: '$250' },
  { value: 500, label: '$500' },
  { value: 1000, label: '$1000' }
];
```

---

## 🎯 Trade Flow

### 1. User Selects Asset
```javascript
const handleAssetChange = (symbol) => {
  setSelectedAsset(assets.find(a => a.symbol === symbol));
  fetchPrice(symbol);
};
```

### 2. User Chooses Direction
```javascript
const handleDirectionChange = (dir) => {
  setDirection(dir);
  // Update UI to show selected direction
};
```

### 3. User Sets Amount
```javascript
const handleAmountChange = (value) => {
  const asset = selectedAsset;
  if (value < asset.min_trade_amount) {
    setError(`Minimum: $${asset.min_trade_amount}`);
  } else if (value > asset.max_trade_amount) {
    setError(`Maximum: $${asset.max_trade_amount}`);
  } else if (value > userBalance) {
    setError('Insufficient balance');
  } else {
    setAmount(value);
    setError(null);
  }
};
```

### 4. User Selects Expiry
```javascript
const handleExpiryChange = (seconds) => {
  setExpirySeconds(seconds);
};
```

### 5. User Opens Trade
```javascript
const handleOpenTrade = async () => {
  try {
    setLoading(true);
    const response = await fetch('/api/binary/trades/open/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        asset_symbol: selectedAsset.symbol,
        direction,
        amount,
        expiry_seconds: expirySeconds
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      showSuccess('Trade opened successfully!');
      setUserBalance(data.new_balance);
      fetchActiveTrades();
    } else {
      showError(data.error);
    }
  } catch (error) {
    showError('Failed to open trade');
  } finally {
    setLoading(false);
  }
};
```

---

## 📱 Responsive Design Breakpoints

```css
/* Mobile */
@media (max-width: 640px) {
  .trade-now {
    padding: 10px;
  }
  
  .price-display .price {
    font-size: 32px;
  }
  
  .direction-buttons {
    grid-template-columns: 1fr;
  }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  .trade-now {
    max-width: 500px;
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .trade-now {
    max-width: 600px;
  }
  
  .active-trades {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}
```

---

## 🎨 Color Scheme

```javascript
const colors = {
  // Directions
  buy: '#10b981',      // Green
  sell: '#ef4444',     // Red
  
  // Status
  active: '#3b82f6',   // Blue
  won: '#10b981',      // Green
  lost: '#ef4444',     // Red
  pending: '#f59e0b',  // Orange
  
  // UI
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  danger: '#ef4444',
  warning: '#f59e0b',
  info: '#06b6d4',
  
  // Backgrounds
  bgPrimary: '#ffffff',
  bgSecondary: '#f3f4f6',
  bgDark: '#1f2937',
  
  // Text
  textPrimary: '#111827',
  textSecondary: '#6b7280',
  textLight: '#9ca3af'
};
```

---

## 🔔 Notifications

### Trade Opened
```javascript
{
  type: 'success',
  title: 'Trade Opened',
  message: `${direction.toUpperCase()} $${amount} on ${asset.symbol}`,
  duration: 3000
}
```

### Trade Won
```javascript
{
  type: 'success',
  title: 'Trade Won! 🎉',
  message: `You won $${profit.toFixed(2)} on ${asset.symbol}`,
  duration: 5000
}
```

### Trade Lost
```javascript
{
  type: 'error',
  title: 'Trade Lost',
  message: `You lost $${amount.toFixed(2)} on ${asset.symbol}`,
  duration: 5000
}
```

### Insufficient Balance
```javascript
{
  type: 'warning',
  title: 'Insufficient Balance',
  message: 'Please deposit funds to continue trading',
  duration: 4000
}
```

---

## 📊 Chart Integration (Optional)

### TradingView Widget
```javascript
import { AdvancedRealTimeChart } from "react-ts-tradingview-widgets";

<AdvancedRealTimeChart
  symbol={`${selectedAsset.symbol}USD`}
  theme="dark"
  autosize
  interval="1"
  timezone="Etc/UTC"
  style="1"
  locale="en"
  toolbar_bg="#f1f3f6"
  enable_publishing={false}
  hide_side_toolbar={false}
  allow_symbol_change={true}
/>
```

---

## 🎮 Keyboard Shortcuts

```javascript
useEffect(() => {
  const handleKeyPress = (e) => {
    if (e.key === 'b' || e.key === 'B') {
      setDirection('buy');
    } else if (e.key === 's' || e.key === 'S') {
      setDirection('sell');
    } else if (e.key === 'Enter') {
      handleOpenTrade();
    }
  };
  
  window.addEventListener('keypress', handleKeyPress);
  return () => window.removeEventListener('keypress', handleKeyPress);
}, []);
```

---

## 🔒 Error Handling

```javascript
const errorMessages = {
  'Insufficient balance': 'You don\'t have enough funds. Please deposit.',
  'Asset not found or inactive': 'This asset is currently unavailable.',
  'Maximum 10 open trades allowed': 'Close some trades before opening new ones.',
  'Minimum trade amount': 'Trade amount is below minimum.',
  'Maximum trade amount': 'Trade amount exceeds maximum.',
  'Unable to get current price': 'Price feed unavailable. Try again.',
};

const handleError = (error) => {
  const message = errorMessages[error] || error || 'Something went wrong';
  showNotification({ type: 'error', message });
};
```

---

## 📈 Performance Tips

1. **Debounce Price Updates**: Don't update UI on every price change
2. **Memoize Components**: Use React.memo for trade cards
3. **Virtual Scrolling**: For long trade history lists
4. **Lazy Loading**: Load trade history on scroll
5. **WebSocket**: Consider WebSocket for real-time updates instead of polling

---

## ✅ Testing Checklist

- [ ] Can select different assets
- [ ] Price updates every second
- [ ] Can switch between BUY/SELL
- [ ] Amount validation works
- [ ] Expiry time selection works
- [ ] Trade opens successfully
- [ ] Balance updates after trade
- [ ] Active trades display correctly
- [ ] Countdown timer works
- [ ] Trade closes automatically
- [ ] Win/Loss calculated correctly
- [ ] Trade history loads
- [ ] Stats update correctly
- [ ] Error messages display
- [ ] Mobile responsive
- [ ] Keyboard shortcuts work

---

## 🚀 Ready to Build!

You have everything needed to build a complete binary trading frontend:
- ✅ All API endpoints documented
- ✅ Data structures defined
- ✅ Component examples provided
- ✅ Real-time update patterns
- ✅ Error handling
- ✅ Styling examples
- ✅ Testing checklist

Start building and integrate with: `http://localhost:8000/api/binary/`
