# Binary Trading Engine - Complete Implementation

## 🎯 Overview

This is a complete synthetic binary trading platform with four tightly coupled engines:

1. **📈 Pricing Engine** - Stochastic price generation
2. **🔄 Streaming Engine** - Real-time WebSocket delivery
3. **💱 Trade Engine** - Execution and settlement logic
4. **🏦 House Edge Engine** - Profit control layer
5. **🤖 Bot Simulator** - Automated trading activity

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRICING ENGINE                          │
│  (price_generator.py)                                       │
│  • Stochastic time-series model                            │
│  • Regime switching (trending/sideways/volatile)           │
│  • Momentum persistence                                     │
│  • Drift bias for house edge                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   STREAMING ENGINE                          │
│  (consumers.py + routing.py)                                │
│  • WebSocket connections (Django Channels)                 │
│  • Real-time price broadcasts                              │
│  • Trade update notifications                              │
│  • Admin monitoring dashboard                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     TRADE ENGINE                            │
│  (trade_service.py)                                         │
│  • Trade opening with validation                           │
│  • Automatic expiry and settlement                         │
│  • Balance management (real + demo)                        │
│  • Statistics tracking                                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  HOUSE EDGE ENGINE                          │
│  (house_edge.py)                                            │
│  • Payout reduction (win streaks, high amounts)            │
│  • Strike price adjustment                                 │
│  • Side imbalance protection                               │
│  • Execution delay calculation                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   BOT SIMULATOR                             │
│  (bot_simulator.py)                                         │
│  • Fake user generation                                    │
│  • Realistic trading patterns                              │
│  • 55-65% win rate                                         │
│  • Recent winners feed                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Setup

### 1. Install Dependencies

```bash
pip install channels channels-redis redis
```

### 2. Update Django Settings

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'channels',
    'binary_trading',
]

# Channels configuration
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

### 3. Install and Start Redis

**Windows:**
```bash
# Download Redis from https://github.com/microsoftarchive/redis/releases
# Or use WSL
wsl sudo service redis-server start
```

**Linux/Mac:**
```bash
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS
redis-server
```

### 4. Run Migrations

```bash
python manage.py makemigrations binary_trading
python manage.py migrate
```

### 5. Create Trading Assets

```bash
python manage.py shell
```

```python
from binary_trading.models import TradingAsset
from decimal import Decimal

# Forex
TradingAsset.objects.create(
    symbol='EURUSD', name='Euro/US Dollar', asset_type='forex',
    base_payout=Decimal('85.00'), volatility=Decimal('0.0030')
)
TradingAsset.objects.create(
    symbol='GBPUSD', name='British Pound/US Dollar', asset_type='forex',
    base_payout=Decimal('85.00'), volatility=Decimal('0.0035')
)

# Crypto
TradingAsset.objects.create(
    symbol='BTC', name='Bitcoin', asset_type='crypto',
    base_payout=Decimal('80.00'), volatility=Decimal('0.0100')
)
TradingAsset.objects.create(
    symbol='ETH', name='Ethereum', asset_type='crypto',
    base_payout=Decimal('82.00'), volatility=Decimal('0.0120')
)

# Commodities
TradingAsset.objects.create(
    symbol='GOLD', name='Gold', asset_type='commodity',
    base_payout=Decimal('85.00'), volatility=Decimal('0.0040')
)
TradingAsset.objects.create(
    symbol='OIL', name='Crude Oil', asset_type='commodity',
    base_payout=Decimal('83.00'), volatility=Decimal('0.0080')
)
```

### 6. Create House Edge Configuration

```python
from binary_trading.models import HouseEdgeConfig

HouseEdgeConfig.objects.create(
    name='Default',
    win_streak_3_reduction=5.00,
    win_streak_5_reduction=10.00,
    high_amount_threshold=1000.00,
    high_amount_reduction=3.00,
    strike_price_adjustment=0.0010,
    atm_is_loss=True,
    min_delay_ms=100,
    max_delay_ms=500,
    is_active=True
)
```

---

## 🚀 Running the System

You need to run **4 processes** simultaneously:

### Terminal 1: Django Server (HTTP + WebSocket)

```bash
python manage.py runserver
```

Or with Daphne (production ASGI server):

```bash
pip install daphne
daphne -b 0.0.0.0 -p 8000 growfund.asgi:application
```

### Terminal 2: Price Generator

```bash
python manage.py run_price_generator --interval 0.5
```

This generates price ticks every 500ms for all active assets.

### Terminal 3: Trade Closer

```bash
python manage.py close_expired_trades --interval 1
```

This checks every second for expired trades and settles them.

### Terminal 4: Bot Simulator (Optional)

```bash
python manage.py run_bot_simulator --trades-per-minute 3 --create-bots 10
```

This creates 10 bot users and simulates ~3 trades per minute.

---

## 🔌 WebSocket Endpoints

### 1. Price Streaming

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/prices/');

ws.onopen = () => {
    // Subscribe to assets
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['EURUSD', 'BTC', 'GOLD']
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'price_update') {
        console.log(`${data.data.symbol}: $${data.data.price}`);
        // Update chart here
    }
};
```

### 2. Trade Updates

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/trades/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'trade_closed') {
        console.log('Trade settled:', data.trade);
        console.log('New balance:', data.new_balance);
    }
};
```

### 3. Admin Monitor

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/admin/monitor/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'metrics_update') {
        console.log('Platform metrics:', data.data);
    }
};
```

---

## 📡 REST API Endpoints

### Assets

- `GET /api/binary-trading/assets/` - List all active assets
- `GET /api/binary-trading/assets/{symbol}/price/` - Get current price
- `GET /api/binary-trading/assets/{symbol}/chart/?interval=1m&limit=100` - Get OHLC data
- `GET /api/binary-trading/prices/` - Get all current prices

### Trading

- `POST /api/binary-trading/trades/open/` - Open a new trade
  ```json
  {
    "asset_symbol": "EURUSD",
    "direction": "buy",
    "amount": "100.00",
    "expiry_seconds": 60,
    "is_demo": false
  }
  ```

- `GET /api/binary-trading/trades/active/?is_demo=false` - Get active trades
- `GET /api/binary-trading/trades/history/?is_demo=false&limit=50` - Get trade history
- `POST /api/binary-trading/trades/{trade_id}/close/` - Close a trade manually

### Balances & Stats

- `GET /api/binary-trading/balances/` - Get real and demo balances
- `GET /api/binary-trading/stats/?is_demo=false` - Get trading statistics

### Social Feed

- `GET /api/binary-trading/feed/winners/?limit=10` - Recent winners (public)
- `GET /api/binary-trading/feed/live/?limit=20` - Live trading feed

---

## 🎮 Frontend Integration

### TradingView Lightweight Charts

```javascript
import { createChart } from 'lightweight-charts';

const chart = createChart(document.getElementById('chart'), {
    width: 800,
    height: 400,
    layout: {
        backgroundColor: '#1e1e1e',
        textColor: '#d1d4dc',
    },
    grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
    },
});

const candlestickSeries = chart.addCandlestickSeries();

// Load initial data
fetch('/api/binary-trading/assets/EURUSD/chart/?interval=1m&limit=100')
    .then(r => r.json())
    .then(data => {
        candlestickSeries.setData(data.candles);
    });

// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/binary-trading/prices/');

ws.onopen = () => {
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['EURUSD']
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'price_update' && data.data.symbol === 'EURUSD') {
        // Update chart with new price
        candlestickSeries.update({
            time: Math.floor(new Date(data.data.timestamp).getTime() / 1000),
            close: parseFloat(data.data.price)
        });
    }
};
```

---

## 🏦 House Edge Mechanics

### 1. Payout Reduction

The system reduces payout percentage based on:

- **Win Streaks**: 3+ wins → -5%, 5+ wins → -10%
- **High Amounts**: $1000+ → -3%, $5000+ → -5%
- **High Profit**: User profit > $1000 → -10%
- **Side Imbalance**: If 70%+ users on one side → -10%

### 2. Strike Price Adjustment

- **BUY trades**: Strike price increased by 0.1% (user needs higher price to win)
- **SELL trades**: Strike price decreased by 0.1% (user needs lower price to win)

### 3. Execution Delay

- Delay ranges from 100ms to 500ms based on house edge
- Higher edge → longer delay → price moves further against user

### 4. ATM (At-The-Money) Rule

If final price exactly equals strike price:
- **Default**: Treat as loss (house keeps stake)
- **Configurable**: Can be set to refund stake

---

## 🤖 Bot Simulator

### Create Bot Users

```bash
python manage.py shell
```

```python
from binary_trading.bot_simulator import BotSimulator

# Create 10 bots
bots = BotSimulator.create_bot_fleet(10)

# Simulate a single trade
trade = BotSimulator.simulate_bot_trade()

# Get recent winners (includes bots)
winners = BotSimulator.get_recent_winners(limit=10)
```

### Bot Behavior

- **Win Rate**: 55-65% (slightly above average)
- **Trade Amounts**: $10 - $500
- **Expiry Times**: 30s, 60s, 120s, 180s, 300s
- **Frequency**: Configurable (default 3 trades/min)

---

## 📊 Monitoring & Admin

### Platform Metrics

Access via WebSocket or create a Django admin view:

```python
from binary_trading.models import BinaryTrade
from django.db.models import Sum, Count

# Today's stats
today_trades = BinaryTrade.objects.filter(
    opened_at__gte=timezone.now().replace(hour=0, minute=0)
)

total_volume = today_trades.aggregate(Sum('amount'))['total']
won_count = today_trades.filter(status='won').count()
lost_count = today_trades.filter(status='lost').count()

# Platform profit
platform_profit = today_trades.filter(status='lost').aggregate(Sum('amount'))['total']
platform_payout = today_trades.filter(status='won').aggregate(Sum('profit_loss'))['total']
net_profit = platform_profit - abs(platform_payout)
```

---

## 🔒 Security Considerations

1. **Rate Limiting**: Implement rate limits on trade opening
2. **Balance Validation**: Always validate balance in atomic transactions
3. **Price Manipulation**: Price generator is server-side only
4. **Bot Detection**: Monitor for suspicious patterns (100% win rate, etc.)
5. **WebSocket Auth**: Ensure WebSocket connections are authenticated

---

## 🧪 Testing

### Test Price Generation

```bash
python manage.py shell
```

```python
from binary_trading.price_generator import PriceGenerator
from decimal import Decimal

gen = PriceGenerator('EURUSD', Decimal('1.0850'), Decimal('0.0030'))

# Generate 10 ticks
for i in range(10):
    tick = gen.generate_tick()
    print(f"Tick {i+1}: ${tick['price']} ({tick['regime']})")

# Generate a candle
candle = gen.generate_candle(duration_seconds=60, ticks_per_candle=60)
print(f"Candle: O={candle['open']} H={candle['high']} L={candle['low']} C={candle['close']}")
```

### Test Trade Flow

```python
from binary_trading.trade_service import TradeExecutionService
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Open trade
trade, error = TradeExecutionService.open_trade(
    user=user,
    asset_symbol='EURUSD',
    direction='buy',
    amount=Decimal('100.00'),
    expiry_seconds=60,
    is_demo=False
)

print(f"Trade opened: {trade.id}")
print(f"Strike price: {trade.strike_price}")
print(f"Payout: {trade.adjusted_payout_percentage}%")

# Wait for expiry, then close
import time
time.sleep(60)

closed_trade, error = TradeExecutionService.close_trade(trade.id)
print(f"Trade result: {closed_trade.status}")
print(f"Profit/Loss: ${closed_trade.profit_loss}")
```

---

## 🎯 Performance Optimization

1. **Database Indexing**: Already configured in models
2. **Price Caching**: Prices cached for 10 seconds
3. **WebSocket Scaling**: Use Redis for channel layer
4. **Async Operations**: All WebSocket consumers are async
5. **Batch Processing**: Trade closer processes in batches

---

## 📈 Scaling Considerations

### Horizontal Scaling

- Run multiple Daphne workers behind a load balancer
- Use Redis Cluster for channel layer
- Separate price generator to dedicated server

### Database Optimization

- Archive old trades (>30 days) to separate table
- Use read replicas for analytics queries
- Implement database connection pooling

### Monitoring

- Track WebSocket connection count
- Monitor Redis memory usage
- Alert on high trade failure rates
- Track platform profit margins

---

## ✅ Checklist

- [x] Pricing Engine (stochastic model)
- [x] Streaming Engine (WebSockets)
- [x] Trade Engine (execution & settlement)
- [x] House Edge Engine (profit control)
- [x] Bot Simulator (fake activity)
- [x] Chart Service (OHLC data)
- [x] Management Commands
- [x] REST API Endpoints
- [x] WebSocket Consumers
- [x] Documentation

---

## 🚀 Next Steps

1. **Frontend Integration**: Connect React/Vue to WebSockets
2. **Admin Dashboard**: Build monitoring UI
3. **Mobile App**: WebSocket support in React Native
4. **Analytics**: Track user behavior and profitability
5. **Compliance**: Add KYC/AML if required by jurisdiction

---

## 📞 Support

For issues or questions, check:
- Models: `binary_trading/models.py`
- Services: `binary_trading/trade_service.py`, `binary_trading/house_edge.py`
- WebSockets: `binary_trading/consumers.py`
- Price Generation: `binary_trading/price_generator.py`
