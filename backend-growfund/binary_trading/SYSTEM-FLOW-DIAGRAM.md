# Binary Trading System - Flow Diagrams

## 🔄 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRICE GENERATION LOOP                        │
│                  (run_price_generator.py)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Every 200-500ms
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PriceGenerator.generate_tick()                     │
│  • Calculate drift (regime-based + house edge bias)             │
│  • Calculate noise (Gaussian random)                            │
│  • Calculate momentum (trend persistence)                       │
│  • Update price: P(t+1) = P(t) + drift + noise + momentum      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Store in Database                              │
│              AssetPrice.objects.create()                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Broadcast via WebSocket                            │
│         PriceStreamConsumer.send(price_update)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Frontend Receives                              │
│         • Update chart (TradingView)                            │
│         • Update price display                                  │
│         • Update trade buttons                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💱 Trade Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CLICKS "BUY"                            │
│              Frontend: openTrade('EURUSD', 'buy')               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              POST /api/binary-trading/trades/open/              │
│  Body: {                                                        │
│    asset_symbol: 'EURUSD',                                      │
│    direction: 'buy',                                            │
│    amount: '100.00',                                            │
│    expiry_seconds: 60                                           │
│  }                                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           TradeExecutionService.open_trade()                    │
│  1. Validate asset exists                                       │
│  2. Validate amount (min/max)                                   │
│  3. Validate user balance                                       │
│  4. Validate trade limits (max open trades, exposure)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Fetch Current Price                                │
│         PriceFeedService.get_current_price()                    │
│              current_price = 1.0850                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           HouseEdgeCalculator.get_trade_parameters()            │
│  1. Calculate payout reduction:                                 │
│     • Check win streak → -5% or -10%                            │
│     • Check trade amount → -3% or -5%                           │
│     • Check user profit → -10%                                  │
│     • Check side imbalance → -10%                               │
│     base_payout: 85% → adjusted_payout: 75%                     │
│                                                                 │
│  2. Adjust strike price:                                        │
│     BUY: 1.0850 → 1.0861 (+0.1%)                                │
│                                                                 │
│  3. Calculate execution delay:                                  │
│     house_edge: 10% → delay: 300ms                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Atomic Transaction BEGIN                           │
│  1. Lock user balance (SELECT FOR UPDATE)                       │
│  2. Deduct amount: $10000 → $9900                               │
│  3. Create BinaryTrade:                                         │
│     • strike_price: 1.0861                                      │
│     • adjusted_payout: 75%                                      │
│     • house_edge: 10%                                           │
│     • status: 'active'                                          │
│     • expires_at: now + 60s                                     │
│  4. COMMIT                                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Response to Frontend                               │
│  {                                                              │
│    success: true,                                               │
│    trade: { id, strike_price, payout, expires_at },            │
│    new_balance: 9900.00                                         │
│  }                                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend Updates                                   │
│  • Show countdown timer (60s)                                   │
│  • Display strike price                                         │
│  • Update balance                                               │
│  • Add to active trades list                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Trade Settlement Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  TRADE EXPIRES (60s elapsed)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           close_expired_trades.py (Background Process)          │
│  • Runs every 1 second                                          │
│  • Queries: BinaryTrade.filter(status='active',                 │
│              expires_at__lte=now)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           TradeExecutionService.close_trade()                   │
│  1. Lock trade (SELECT FOR UPDATE)                              │
│  2. Fetch final price from PriceFeedService                     │
│     final_price = 1.0870                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Determine Outcome                                  │
│  Direction: BUY                                                 │
│  Strike Price: 1.0861                                           │
│  Final Price: 1.0870                                            │
│                                                                 │
│  final_price (1.0870) > strike_price (1.0861)                   │
│  → USER WINS! ✅                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Calculate Payout                                   │
│  stake: $100                                                    │
│  adjusted_payout: 75%                                           │
│  profit = $100 × 0.75 = $75                                     │
│  total_payout = $100 + $75 = $175                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Atomic Transaction BEGIN                           │
│  1. Lock user balance                                           │
│  2. Credit payout: $9900 + $175 = $10075                        │
│  3. Update trade:                                               │
│     • status: 'won'                                             │
│     • final_price: 1.0870                                       │
│     • profit_loss: +$75                                         │
│     • closed_at: now                                            │
│  4. COMMIT                                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Update Statistics                                  │
│  UserTradingStats:                                              │
│  • total_trades += 1                                            │
│  • total_wins += 1                                              │
│  • current_win_streak += 1                                      │
│  • total_profit += $75                                          │
│  • net_profit = total_profit - total_loss                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Broadcast via WebSocket                            │
│  TradeUpdatesConsumer.send({                                    │
│    type: 'trade_closed',                                        │
│    trade: { status: 'won', profit: 75 },                        │
│    new_balance: 10075                                           │
│  })                                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend Updates                                   │
│  • Show "YOU WON $75!" notification                             │
│  • Update balance display                                       │
│  • Remove from active trades                                    │
│  • Add to trade history                                         │
│  • Update statistics                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏦 House Edge Application

```
┌─────────────────────────────────────────────────────────────────┐
│                    BASE CONFIGURATION                           │
│  Asset: EURUSD                                                  │
│  Base Payout: 85%                                               │
│  Current Price: 1.0850                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CHECK USER STATISTICS                              │
│  • Current win streak: 4                                        │
│  • Total profit: $1200                                          │
│  • Trade amount: $500                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CALCULATE PAYOUT REDUCTION                         │
│  1. Win streak 3+: -5%                                          │
│  2. High profit ($1200 > $1000): -10%                           │
│  3. High amount ($500 < $1000): 0%                              │
│  4. Side imbalance: 0%                                          │
│                                                                 │
│  Total reduction: -15%                                          │
│  Adjusted payout: 85% - 15% = 70%                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              ADJUST STRIKE PRICE                                │
│  Direction: BUY                                                 │
│  Adjustment: +0.1%                                              │
│                                                                 │
│  Original: 1.0850                                               │
│  Adjusted: 1.0850 × 1.001 = 1.0861                              │
│                                                                 │
│  User needs price to reach 1.0861 (not 1.0850) to win          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CALCULATE EXECUTION DELAY                          │
│  House edge: 15%                                                │
│  Delay factor: 15 / 30 = 0.5                                    │
│  Delay range: 100ms - 500ms                                     │
│  Delay: 100 + (400 × 0.5) = 300ms                               │
│                                                                 │
│  (Price may move against user during delay)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              FINAL TRADE PARAMETERS                             │
│  • Strike Price: 1.0861 (adjusted)                              │
│  • Payout: 70% (reduced from 85%)                               │
│  • House Edge: 15%                                              │
│  • Execution Delay: 300ms                                       │
│                                                                 │
│  Expected Value (User): -15% (house profitable)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Bot Simulator Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              run_bot_simulator.py (Background Process)          │
│  • Runs continuously                                            │
│  • Target: 3 trades per minute                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Every ~20 seconds
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              BotSimulator.simulate_bot_trade()                  │
│  1. Select random bot user                                      │
│  2. Select random asset                                         │
│  3. Check bot's current win rate                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Determine Trade Parameters                         │
│  • Direction: random (buy/sell)                                 │
│  • Amount: $10 - $500 (random)                                  │
│  • Expiry: 30s, 60s, 120s, 180s, 300s (random)                 │
│  • Target win rate: 55-65%                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Open Trade (Same as User)                          │
│  TradeExecutionService.open_trade(                              │
│    user=bot_user,                                               │
│    asset_symbol='EURUSD',                                       │
│    direction='buy',                                             │
│    amount=250.00,                                               │
│    expiry_seconds=60                                            │
│  )                                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Trade Settles Automatically                        │
│  • close_expired_trades.py handles settlement                   │
│  • Bot wins ~60% of the time (target rate)                      │
│  • Appears in "Recent Winners" feed                             │
│  • Appears in "Live Trading" feed                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 WebSocket Subscription Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              Frontend Opens WebSocket                           │
│  const ws = new WebSocket(                                      │
│    'ws://localhost:8000/ws/binary-trading/prices/'              │
│  );                                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PriceStreamConsumer.connect()                      │
│  • Accept connection                                            │
│  • Send connection confirmation                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend Subscribes                                │
│  ws.send(JSON.stringify({                                       │
│    action: 'subscribe',                                         │
│    symbols: ['EURUSD', 'BTC', 'GOLD']                           │
│  }));                                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PriceStreamConsumer.handle_subscribe()             │
│  • Add symbols to subscribed_symbols set                        │
│  • Join channel groups: 'prices_EURUSD', etc.                   │
│  • Start price streaming task                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PriceStreamConsumer.stream_prices()                │
│  Loop forever:                                                  │
│    For each subscribed symbol:                                  │
│      1. Get price generator                                     │
│      2. Generate tick                                           │
│      3. Store in database                                       │
│      4. Send to client via WebSocket                            │
│    Sleep 200-500ms (random)                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend Receives Updates                          │
│  ws.onmessage = (event) => {                                    │
│    const data = JSON.parse(event.data);                         │
│    if (data.type === 'price_update') {                          │
│      updateChart(data.data.symbol, data.data.price);            │
│    }                                                            │
│  };                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  • React/Vue/Angular                                             │
│  • TradingView Charts                                            │
│  • WebSocket Client                                              │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 │ HTTP REST API + WebSocket
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                      DJANGO SERVER                               │
│  • REST API (views.py)                                           │
│  • WebSocket Consumers (consumers.py)                            │
│  • ASGI Application (asgi.py)                                    │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ├─────────────────┬─────────────────┬─────────────┐
                 ▼                 ▼                 ▼             ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────┐  ┌──────────┐
│  PRICE GENERATOR │  │  TRADE CLOSER    │  │   BOTS   │  │  REDIS   │
│  (Background)    │  │  (Background)    │  │(Optional)│  │(Channel) │
│  • Generate ticks│  │  • Close expired │  │• Simulate│  │  Layer   │
│  • Store prices  │  │  • Settle trades │  │  trades  │  │          │
└──────────────────┘  └──────────────────┘  └──────────┘  └──────────┘
         │                     │                   │             │
         └─────────────────────┴───────────────────┴─────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   POSTGRESQL DB      │
                    │  • TradingAsset      │
                    │  • BinaryTrade       │
                    │  • AssetPrice        │
                    │  • UserTradingStats  │
                    └──────────────────────┘
```

This completes the visual documentation of the binary trading system!
