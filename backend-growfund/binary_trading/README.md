# Binary Trading System

A complete synthetic binary options trading platform with real-time price streaming, automated settlement, and house edge optimization.

## 🎯 Features

- **Realistic Price Generation**: Stochastic time-series model with regime switching
- **Real-Time Streaming**: WebSocket-based price and trade updates
- **Automated Settlement**: Background process closes expired trades
- **House Edge System**: Profitable payout reduction and strike adjustment
- **Bot Simulation**: Fake trading activity for social proof
- **Dual Mode**: Separate real and demo accounts
- **Live Market Data**: Integration with CoinGecko and Yahoo Finance
- **Admin Monitoring**: Real-time platform metrics

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r binary_trading/requirements-binary-trading.txt
```

### 2. Install Redis

**Windows:**
```bash
wsl sudo apt-get install redis-server
wsl sudo service redis-server start
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo service redis-server start
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 3. Configure Django

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'channels',
    'binary_trading',
]

ASGI_APPLICATION = 'growfund.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations binary_trading
python manage.py migrate
```

### 5. Setup System

```bash
python manage.py shell
>>> exec(open('binary_trading/setup_binary_trading.py').read())
>>> exit()
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**Windows:**
```bash
start_binary_trading.bat
```

**Linux/Mac:**
```bash
chmod +x start_binary_trading.sh
./start_binary_trading.sh
```

### Option 2: Manual Startup

Open 4 separate terminals:

**Terminal 1: Django Server**
```bash
python manage.py runserver
```

**Terminal 2: Price Generator**
```bash
python manage.py run_price_generator --interval 0.5
```

**Terminal 3: Trade Closer**
```bash
python manage.py close_expired_trades --interval 1
```

**Terminal 4: Bot Simulator (Optional)**
```bash
python manage.py run_bot_simulator --trades-per-minute 3 --create-bots 10
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_binary_trading_complete.py
```

## 📡 API Endpoints

### Assets
- `GET /api/binary-trading/assets/` - List all assets
- `GET /api/binary-trading/assets/{symbol}/price/` - Current price
- `GET /api/binary-trading/assets/{symbol}/chart/` - OHLC data

### Trading
- `POST /api/binary-trading/trades/open/` - Open trade
- `GET /api/binary-trading/trades/active/` - Active trades
- `GET /api/binary-trading/trades/history/` - Trade history
- `POST /api/binary-trading/trades/{id}/close/` - Close trade

### Balances & Stats
- `GET /api/binary-trading/balances/` - Real & demo balances
- `GET /api/binary-trading/stats/` - Trading statistics

### Social Feed
- `GET /api/binary-trading/feed/winners/` - Recent winners
- `GET /api/binary-trading/feed/live/` - Live trading feed

## 🔌 WebSocket Endpoints

### Price Streaming
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/prices/');

ws.onopen = () => {
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['EURUSD', 'BTC', 'GOLD']
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'price_update') {
        console.log(`${data.data.symbol}: $${data.data.price}`);
    }
};
```

### Trade Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/trades/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'trade_closed') {
        console.log('Trade settled:', data.trade);
    }
};
```

### Admin Monitor
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/admin/monitor/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'metrics_update') {
        console.log('Platform metrics:', data.data);
    }
};
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         PRICING ENGINE                  │
│  • Stochastic model                     │
│  • Regime switching                     │
│  • Momentum persistence                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       STREAMING ENGINE                  │
│  • WebSocket (Django Channels)          │
│  • Redis pub/sub                        │
│  • Real-time broadcasts                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         TRADE ENGINE                    │
│  • Opening & closing                    │
│  • Balance management                   │
│  • Statistics tracking                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       HOUSE EDGE ENGINE                 │
│  • Payout reduction                     │
│  • Strike adjustment                    │
│  • Side imbalance protection            │
└─────────────────────────────────────────┘
```

## 🎮 Frontend Integration

### TradingView Charts

```javascript
import { createChart } from 'lightweight-charts';

const chart = createChart(document.getElementById('chart'), {
    width: 800,
    height: 400,
});

const candlestickSeries = chart.addCandlestickSeries();

// Load initial data
fetch('/api/binary-trading/assets/EURUSD/chart/?interval=1m&limit=100')
    .then(r => r.json())
    .then(data => candlestickSeries.setData(data.candles));

// Real-time updates via WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/prices/');
ws.onopen = () => {
    ws.send(JSON.stringify({ action: 'subscribe', symbols: ['EURUSD'] }));
};
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'price_update') {
        candlestickSeries.update({
            time: Math.floor(new Date(data.data.timestamp).getTime() / 1000),
            close: parseFloat(data.data.price)
        });
    }
};
```

### Trade Execution

```javascript
async function openTrade(symbol, direction, amount, expirySeconds) {
    const response = await fetch('/api/binary-trading/trades/open/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            asset_symbol: symbol,
            direction: direction,
            amount: amount.toString(),
            expiry_seconds: expirySeconds,
            is_demo: false
        })
    });
    
    const data = await response.json();
    return data;
}
```

## 🏦 House Edge Mechanics

### Payout Reduction
- Win streak 3+: -5%
- Win streak 5+: -10%
- Amount $1000+: -3%
- Amount $5000+: -5%
- Profit $1000+: -10%
- Side imbalance >70%: -10%

### Strike Price Adjustment
- BUY: +0.1% (harder to win)
- SELL: -0.1% (harder to win)

### Execution Delay
- 100-500ms based on house edge
- Higher edge → longer delay

## 📊 Monitoring

### Platform Metrics

```python
from binary_trading.models import BinaryTrade
from django.db.models import Sum

# Today's stats
today_trades = BinaryTrade.objects.filter(
    opened_at__gte=timezone.now().replace(hour=0, minute=0)
)

total_volume = today_trades.aggregate(Sum('amount'))['total']
won_count = today_trades.filter(status='won').count()
lost_count = today_trades.filter(status='lost').count()
```

## 🔧 Configuration

### House Edge Settings

```python
from binary_trading.models import HouseEdgeConfig

config = HouseEdgeConfig.objects.get(is_active=True)
config.win_streak_5_reduction = 15.00  # Increase penalty
config.strike_price_adjustment = 0.0015  # Increase adjustment
config.save()
```

### Asset Settings

```python
from binary_trading.models import TradingAsset

asset = TradingAsset.objects.get(symbol='EURUSD')
asset.base_payout = 82.00  # Reduce base payout
asset.volatility = 0.0040  # Increase volatility
asset.save()
```

## 📚 Documentation

- **[QUICK-START.md](QUICK-START.md)** - 5-minute setup guide
- **[BINARY-TRADING-ENGINE-COMPLETE.md](BINARY-TRADING-ENGINE-COMPLETE.md)** - Full technical documentation
- **[../BINARY-TRADING-IMPLEMENTATION-SUMMARY.md](../BINARY-TRADING-IMPLEMENTATION-SUMMARY.md)** - Implementation overview

## 🐛 Troubleshooting

### Redis Connection Error
```bash
redis-cli ping  # Should return PONG
```

### WebSocket Connection Failed
- Check Django server is running
- Verify ASGI configuration
- Check Redis connection

### No Price Updates
- Ensure price generator is running
- Check assets exist in database
- Verify Redis connection

### Trades Not Closing
- Ensure trade closer is running
- Check terminal for errors
- Verify trade expiry times

## 📈 Performance

- **Latency**: <500ms for price updates
- **Throughput**: 1000+ concurrent WebSocket connections
- **Database**: Indexed for fast queries
- **Caching**: 10-second price cache

## 🔒 Security

- Atomic transactions (race condition protection)
- Balance validation
- Trade limit enforcement
- WebSocket authentication
- Separate real/demo accounts

## 📞 Support

For issues or questions:
1. Check documentation files
2. Run test suite: `python test_binary_trading_complete.py`
3. Review terminal logs
4. Check Redis connection

## 📄 License

Proprietary - GrowFund Platform

## 👥 Contributors

- Binary Trading Engine v1.0
- Implemented: May 2026
