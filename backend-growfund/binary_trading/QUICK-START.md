# Binary Trading System - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies

```bash
pip install channels channels-redis daphne redis
```

### 2. Install & Start Redis

```bash
# Windows (WSL)
wsl sudo service redis-server start

# Linux
sudo service redis-server start

# macOS
brew services start redis
```

### 3. Run Setup Script

```bash
python manage.py shell
>>> exec(open('binary_trading/setup_binary_trading.py').read())
>>> exit()
```

### 4. Start All Services

**Terminal 1: Django Server**
```bash
python manage.py runserver
```

**Terminal 2: Price Generator**
```bash
python manage.py run_price_generator
```

**Terminal 3: Trade Closer**
```bash
python manage.py close_expired_trades
```

**Terminal 4: Bot Simulator (Optional)**
```bash
python manage.py run_bot_simulator --trades-per-minute 3 --create-bots 10
```

---

## 🧪 Test the System

```bash
python test_binary_trading_complete.py
```

---

## 🔌 WebSocket Test (JavaScript)

```javascript
// Connect to price stream
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/prices/');

ws.onopen = () => {
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['EURUSD', 'BTC']
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

---

## 📡 REST API Quick Test

### Open a Trade

```bash
curl -X POST http://localhost:8000/api/binary-trading/trades/open/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "EURUSD",
    "direction": "buy",
    "amount": "100.00",
    "expiry_seconds": 60,
    "is_demo": false
  }'
```

### Get Active Trades

```bash
curl http://localhost:8000/api/binary-trading/trades/active/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Recent Winners

```bash
curl http://localhost:8000/api/binary-trading/feed/winners/?limit=10
```

---

## 🎯 Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/binary-trading/assets/` | GET | List all assets |
| `/api/binary-trading/assets/{symbol}/price/` | GET | Current price |
| `/api/binary-trading/assets/{symbol}/chart/` | GET | OHLC data |
| `/api/binary-trading/trades/open/` | POST | Open trade |
| `/api/binary-trading/trades/active/` | GET | Active trades |
| `/api/binary-trading/trades/history/` | GET | Trade history |
| `/api/binary-trading/balances/` | GET | Real & demo balance |
| `/api/binary-trading/stats/` | GET | Trading stats |
| `/api/binary-trading/feed/winners/` | GET | Recent winners |
| `/api/binary-trading/feed/live/` | GET | Live feed |

---

## 🔧 Troubleshooting

### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### WebSocket Connection Failed
- Ensure Django server is running
- Check ASGI configuration in `growfund/asgi.py`
- Verify `CHANNEL_LAYERS` in settings.py

### No Price Updates
- Check if price generator is running
- Verify assets exist in database
- Check Redis connection

### Trades Not Closing
- Ensure trade closer is running
- Check for errors in terminal output
- Verify trade expiry times

---

## 📊 Monitoring

### Check System Status

```python
from binary_trading.models import BinaryTrade, TradingAsset
from django.utils import timezone

# Active trades
active = BinaryTrade.objects.filter(status='active').count()
print(f"Active trades: {active}")

# Today's volume
today = timezone.now().replace(hour=0, minute=0)
volume = BinaryTrade.objects.filter(
    opened_at__gte=today
).aggregate(Sum('amount'))['total']
print(f"Today's volume: ${volume}")
```

---

## 🎨 Frontend Integration Example

```javascript
// React component example
import { useEffect, useState } from 'react';

function BinaryTrading() {
    const [price, setPrice] = useState(null);
    const [ws, setWs] = useState(null);

    useEffect(() => {
        const socket = new WebSocket('ws://localhost:8000/ws/binary-trading/prices/');
        
        socket.onopen = () => {
            socket.send(JSON.stringify({
                action: 'subscribe',
                symbols: ['EURUSD']
            }));
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'price_update') {
                setPrice(data.data.price);
            }
        };
        
        setWs(socket);
        
        return () => socket.close();
    }, []);

    const openTrade = async (direction) => {
        const response = await fetch('/api/binary-trading/trades/open/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                asset_symbol: 'EURUSD',
                direction: direction,
                amount: '100.00',
                expiry_seconds: 60,
                is_demo: false
            })
        });
        
        const data = await response.json();
        console.log('Trade opened:', data);
    };

    return (
        <div>
            <h1>EURUSD: ${price}</h1>
            <button onClick={() => openTrade('buy')}>BUY</button>
            <button onClick={() => openTrade('sell')}>SELL</button>
        </div>
    );
}
```

---

## 📚 Documentation

- **Full Guide**: `BINARY-TRADING-ENGINE-COMPLETE.md`
- **Models**: `binary_trading/models.py`
- **API Views**: `binary_trading/views.py`
- **WebSockets**: `binary_trading/consumers.py`
- **Price Engine**: `binary_trading/price_generator.py`
- **House Edge**: `binary_trading/house_edge.py`

---

## ✅ Production Checklist

- [ ] Redis configured with persistence
- [ ] Daphne running behind Nginx
- [ ] Database indexes optimized
- [ ] Celery for background tasks (optional)
- [ ] Monitoring & alerting setup
- [ ] Rate limiting enabled
- [ ] SSL/TLS for WebSockets
- [ ] Backup strategy for trades
- [ ] Compliance & KYC (if required)

---

## 🆘 Support

For issues:
1. Check logs in terminal outputs
2. Verify all 4 processes are running
3. Test with `test_binary_trading_complete.py`
4. Review `BINARY-TRADING-ENGINE-COMPLETE.md`
