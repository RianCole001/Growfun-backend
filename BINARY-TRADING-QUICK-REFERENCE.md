# Binary Trading System - Quick Reference Card

## 🚀 Start Everything (One Command)

### Windows
```bash
cd backend-growfund
start_binary_trading.bat
```

### Linux/Mac
```bash
cd backend-growfund
chmod +x start_binary_trading.sh
./start_binary_trading.sh
```

---

## 📡 API Quick Reference

### Base URL
```
http://localhost:8000/api/binary-trading/
```

### Common Endpoints

```javascript
// Get assets
GET /assets/

// Get price
GET /assets/EURUSD/price/

// Get chart
GET /assets/EURUSD/chart/?interval=1m&limit=100

// Open trade
POST /trades/open/
{
  "asset_symbol": "EURUSD",
  "direction": "buy",
  "amount": "100.00",
  "expiry_seconds": 60,
  "is_demo": false
}

// Get active trades
GET /trades/active/?is_demo=false

// Get history
GET /trades/history/?is_demo=false&limit=50

// Get balances
GET /balances/

// Get stats
GET /stats/?is_demo=false
```

---

## 🔌 WebSocket Quick Reference

### URLs
```
ws://localhost:8000/ws/binary-trading/prices/
ws://localhost:8000/ws/binary-trading/trades/
```

### Usage

```javascript
import binaryTradingWS from './services/binaryTradingWebSocket';

// Connect
binaryTradingWS.connectPriceStream();

// Subscribe
binaryTradingWS.onPriceUpdate('EURUSD', (data) => {
  console.log(data.price);
});

// Disconnect
binaryTradingWS.disconnect();
```

---

## 🧪 Quick Test

### Backend
```bash
cd backend-growfund
python test_binary_trading_complete.py
```

### Frontend (Browser Console)
```javascript
// Test API
import { binaryOptionsAPI } from './services/api';
await binaryOptionsAPI.getAssets();

// Test WebSocket
import binaryTradingWS from './services/binaryTradingWebSocket';
binaryTradingWS.connectPriceStream();
binaryTradingWS.onPriceUpdate('EURUSD', console.log);
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Services won't start | Check Redis: `redis-cli ping` |
| No price updates | Start price generator |
| Trades not closing | Start trade closer |
| API 404 errors | Check `.env` file |
| WebSocket fails | Check `REACT_APP_WS_URL` |

---

## 📁 Key Files

### Backend
- `binary_trading/price_generator.py` - Price engine
- `binary_trading/consumers.py` - WebSocket
- `binary_trading/trade_service.py` - Trade logic
- `binary_trading/house_edge.py` - Profit control

### Frontend
- `src/services/api.js` - API service
- `src/services/binaryTradingWebSocket.js` - WebSocket
- `src/components/TradeNow.js` - Trading UI

---

## 📚 Documentation

- `BINARY-TRADING-SYNC-COMPLETE.md` - Full sync guide
- `backend-growfund/binary_trading/QUICK-START.md` - Backend setup
- `wazimu/Growfund-Dashboard/BINARY-TRADING-FRONTEND-INTEGRATION.md` - Frontend guide

---

## ✅ Status: READY TO USE

Everything is synchronized and ready to go!
