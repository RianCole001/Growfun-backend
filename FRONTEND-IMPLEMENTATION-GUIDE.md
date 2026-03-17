# Frontend Implementation Guide
Backend: `https://growfun-backend.onrender.com`
All requests require `Authorization: Bearer <access_token>` unless marked public.

---

## 1. Authentication

### Register
```
POST /api/auth/register/
{ first_name, last_name, email, password, referral_code? }
```
Response: `{ success, email }` — do NOT expect a token here, user must log in after.

### Login
```
POST /api/auth/login/
{ email, password }
```
Response: `{ tokens: { access, refresh }, user: { id, email, balance, ... } }`
Store both tokens. Use `access` for all API calls. Use `refresh` to get a new access token when it expires.

### Refresh Token
```
POST /api/auth/token/refresh/
{ refresh }
```

### Forgot Password
```
POST /api/auth/forgot-password/
{ email }
```
Response: `{ message }` — token is sent via email only, never in the response.

### Reset Password
```
POST /api/auth/reset-password/
{ token, password }
```

---

## 2. User Profile

### Get current user
```
GET /api/auth/me/
```
Returns full user object including `balance`.

### Update profile
```
PATCH /api/auth/profile/
{ first_name?, last_name?, phone?, location? }
```

### Change password
```
POST /api/auth/change-password/
{ old_password, new_password }
```

### Get balance
```
GET /api/auth/balance/
```
Returns `{ balance }` (real account only).

---

## 3. Referrals

### Get referral stats + link
```
GET /api/auth/referral-stats/
```
Response:
```json
{
  "referral_code": "ABC12345",
  "referral_link": "https://dashboard-yfb8.onrender.com/register?ref=ABC12345",
  "total_referrals": 3,
  "total_earned": 150.00,
  "pending_earnings": 50.00
}
```
Display the `referral_link` as a copyable link. Do NOT construct this URL yourself.

---

## 4. Transactions

### Deposit (ExpressPay Ghana)
```
POST /api/transactions/expresspay/deposit/
{ amount }   ← GHS amount, minimum 1.00
```
Response: `{ checkout_url, reference, transaction_id }`
Redirect the user to `checkout_url` to complete payment on ExpressPay's page.

### Payment callback (after ExpressPay redirect)
ExpressPay redirects to `https://dashboard-yfb8.onrender.com/payment/callback?order-id=xxx&token=xxx`
Your callback page should call:
```
GET /api/transactions/expresspay/callback/?order-id=xxx&token=xxx
```
Response: `{ status: "approved"|"declined"|"pending", transaction }`

### Verify payment manually
```
POST /api/transactions/expresspay/verify/
{ reference: "DEP-XXXX" }   OR   { token: "..." }
```

### Withdraw (MoMo)
```
POST /api/transactions/momo/withdrawal/
{ amount, phone_number }
```

### Transaction list
```
GET /api/transactions/
```

### Transaction summary
```
GET /api/transactions/summary/
```
Returns `{ total_deposits, total_withdrawals, pending_deposits, pending_withdrawals, current_balance, recent_transactions }`

---

## 5. Crypto Portfolio

### Get prices (all coins)
```
GET /api/investments/crypto/prices/
```
Returns prices for BTC, ETH, BNB, ADA, SOL, DOT, USDT (live from CoinGecko) plus EXACOIN and OPTCOIN (admin-controlled).
```json
{
  "data": {
    "BTC":     { "price": 64444.00, "change24h": 2.10, "change7d": -1.50, "change30d": 8.70 },
    "EXACOIN": { "price": 62.00,    "change24h": 3.33, "change7d": 12.80, "change30d": 89.50 }
  }
}
```

### Buy crypto
```
POST /api/investments/crypto/buy/
{ coin: "BTC", amount: 100.00 }   ← amount in USD
```
Response includes `investment.id` — save this, you need it to sell.

### Sell crypto
```
POST /api/investments/crypto/sell/
{ investment_id, coin: "BTC", quantity: 0.00150000 }
```

### Portfolio (holdings)
```
GET /api/investments/crypto/portfolio/
```
Returns live-priced holdings. Each entry has `name` (full coin name e.g. "Bitcoin"), `coin`, `quantity`, `current_price`, `current_value`, `profit_loss`.

---

## 6. Binary Trading (Trade Now)

### Important: Real vs Demo
Every trading endpoint accepts/returns `is_demo: true|false`.
**These are completely separate** — different balances, different history, different stats.
Never mix them in the UI. Use a clear toggle (e.g. "Real" / "Demo" tab).

---

### Get both balances
```
GET /api/binary/balances/
```
```json
{ "real_balance": 500.00, "demo_balance": 10000.00 }
```
Show both. Let the user switch modes.

### Get available assets
```
GET /api/binary/assets/
```
Returns list of tradeable assets with `symbol`, `name`, `asset_type`, `min_trade_amount`, `max_trade_amount`.

### Get live price (poll every 2-3 seconds)
```
GET /api/binary/assets/BTC/price/
```
```json
{ "symbol": "BTC", "price": 64321.50, "timestamp": "..." }
```

### Get chart data (OHLC candlesticks)
```
GET /api/binary/assets/BTC/chart/?interval=1m&limit=100
```
Intervals: `1m 5m 15m 30m 1h 4h 1d`
Each candle: `{ time (unix seconds), open, high, low, close, volume }`

Use [Lightweight Charts by TradingView](https://tradingview.github.io/lightweight-charts/) — it's free, tiny, and handles live updates via `series.update()` without re-rendering the whole chart.

---

### Open a trade
```
POST /api/binary/trades/open/
{
  asset_symbol: "BTC",
  direction: "buy",        ← "buy" (Call) or "sell" (Put)
  amount: 50.00,
  expiry_seconds: 60,      ← 60 to 3600
  is_demo: false
}
```
Response:
```json
{
  "trade": {
    "id": "uuid",
    "asset_symbol": "BTC",
    "direction": "buy",
    "amount": 50.00,
    "strike_price": 64385.12,       ← house-edge adjusted, show as entry price
    "adjusted_payout_percentage": 82.00,
    "expires_at": "2026-03-18T10:01:00Z",
    "expiry_seconds": 60,
    "potential_profit": 41.00,
    "time_remaining": 60,
    "status": "active",
    "is_demo": false
  },
  "new_balance": 450.00,
  "is_demo": false
}
```
Show `strike_price` as the "Entry Price" in the UI.
Show `adjusted_payout_percentage` as the payout % (e.g. "82% payout").
Show `potential_profit` as the profit if they win.

---

### Countdown timer + close trade
Start a countdown from `expiry_seconds`. When it hits 0, call:
```
POST /api/binary/trades/<trade_id>/close/
```
Response:
```json
{
  "trade": {
    "status": "won",          ← "won" or "lost"
    "profit_loss": 41.00,     ← positive = profit, negative = loss
    "final_price": 64410.00,
    "strike_price": 64385.12
  },
  "new_balance": 491.00,
  "is_demo": false
}
```
Show a result overlay: green for won, red for lost, with the P&L amount.

Note: The backend allows closing up to 2 seconds before expiry. If you call it too early you get a `400` with `"Trade expires in Xs"` — just wait and retry.

---

### Active trades
```
GET /api/binary/trades/active/?is_demo=false
```
Show each active trade with a live countdown. When a trade's `time_remaining` hits 0, call the close endpoint.

---

### Trade history
```
GET /api/binary/trades/history/?is_demo=false&limit=50&offset=0
```
Includes `won`, `lost`, and `cancelled` trades.
Response includes a `summary` block:
```json
{
  "summary": {
    "total_wagered": 500.00,
    "total_won": 82.00,
    "net_pnl": -18.00,
    "win_count": 3,
    "loss_count": 4
  }
}
```
Display this as a stats bar above the history table.

---

### Trading stats
```
GET /api/binary/stats/?is_demo=false
GET /api/binary/stats/?is_demo=true
```
Returns `{ total_trades, total_wins, total_losses, win_rate, net_profit, current_win_streak, ... }`
Real and demo stats are completely separate — never mixed.

---

## 7. Demo Account

### Get / Reset demo account
```
GET  /api/demo/account/    ← get balance and info
POST /api/demo/account/    ← reset to $10,000 (clears all demo data)
```

### Demo transaction history
```
GET /api/demo/transactions/
```
Includes binary trade results (won/lost), crypto buys/sells, and investments.

---

## 8. Key UI Rules

### Real vs Demo toggle
- Show a persistent toggle in the trading UI: **Real** | **Demo**
- When in Demo mode: show demo balance, demo history, demo stats
- When in Real mode: show real balance, real history, real stats
- Never show demo data in real mode or vice versa

### Chart
- Use Lightweight Charts (TradingView) — `npm install lightweight-charts`
- Load historical candles on mount via the chart endpoint
- Poll `/api/binary/assets/<symbol>/price/` every 2-3 seconds
- On each tick call `series.update({ time: Math.floor(Date.now()/1000), value: price })` — no full reload

### Trade flow
1. User selects asset, direction (Buy/Sell), amount, expiry
2. Call `POST /api/binary/trades/open/` → show strike price + payout %
3. Start countdown timer
4. At 0: call `POST /api/binary/trades/<id>/close/` → show result overlay
5. Refresh balance

### Payout display
Show `adjusted_payout_percentage` from the trade response, not a hardcoded number. It varies per user based on win streak and trade size.

### Payment callback page
Route: `/payment/callback`
On load, read `order-id` and `token` from URL query params and call the callback endpoint. Show loading → then success/failure based on `status`.

---

## 9. API Base URL
```
https://growfun-backend.onrender.com
```
First request after inactivity may take ~30-60 seconds (Render free tier cold start). Show a loading spinner, don't treat it as an error.
