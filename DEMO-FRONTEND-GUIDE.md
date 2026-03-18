# Demo Account — Frontend Integration Guide

Base URL: `https://growfun-backend.onrender.com/api/demo`

All endpoints require `Authorization: Bearer <token>` header.

---

## Account

### Initialize / Get Account
Always call this first on any demo page load. Auto-creates the account with $10,000 if it doesn't exist.

```
GET /api/demo/account/
```

Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "balance": "10000.00",
    "is_active": true,
    "created_at": "2026-03-18T10:00:00Z",
    "updated_at": "2026-03-18T10:00:00Z"
  }
}
```

### Reset Account
Wipes all investments and transactions, restores balance to $10,000.

```
POST /api/demo/account/
```

### Get Balance Only
```
GET /api/demo/balance/
```

Response:
```json
{ "success": true, "data": { "balance": "8500.00" } }
```

### Add Virtual Funds
```
POST /api/demo/deposit/
Body: { "amount": 5000 }
```

---

## Crypto

### Buy Crypto
Do NOT send a price — the backend fetches the live price server-side.

```
POST /api/demo/crypto/buy/
Body: { "coin": "BTC", "amount": 500 }
```

Supported coins: `BTC`, `ETH`, `BNB`, `ADA`, `SOL`, `DOT`, `USDT`, `EXACOIN`, `OPTCOIN`

Response:
```json
{
  "success": true,
  "data": {
    "new_balance": "9500.00",
    "investment": {
      "id": 1,
      "investment_type": "crypto",
      "asset_name": "BTC",
      "amount": "500.00",
      "quantity": "0.00775194",
      "price_at_purchase": "64444.00",
      "current_price": "64444.00",
      "status": "active",
      "created_at": "2026-03-18T10:00:00Z"
    },
    "transaction": { ... }
  }
}
```

### Sell Crypto
```
POST /api/demo/crypto/sell/
Body: { "coin": "BTC", "quantity": 0.005 }
```

Sells FIFO (oldest holdings first). Price fetched server-side.

Response:
```json
{
  "success": true,
  "data": {
    "new_balance": "9822.20",
    "transaction": { ... }
  }
}
```

---

## Capital Plans

Fixed rates — do not send a rate field.

| plan_type  | Monthly Return |
|------------|---------------|
| `basic`    | 20%/month     |
| `standard` | 30%/month     |
| `advance`  | 40%/month     |

```
POST /api/demo/capital-plan/
Body: {
  "plan_type": "basic",
  "amount": 1000,
  "months": 3
}
```

Response:
```json
{
  "success": true,
  "data": {
    "new_balance": "9000.00",
    "investment": {
      "id": 2,
      "investment_type": "capital_plan",
      "asset_name": "Basic Capital Plan",
      "amount": "1000.00",
      "monthly_rate": "20.00",
      "duration_months": 3,
      "status": "active",
      "created_at": "2026-03-18T10:00:00Z"
    },
    "transaction": { ... }
  }
}
```

---

## Real Estate

Fixed rates and 12-month duration — do not send rate or months.

| property_type | Monthly Return | Duration |
|---------------|---------------|----------|
| `starter`     | 8%/month      | 12 months |
| `premium`     | 12%/month     | 12 months |
| `luxury`      | 18%/month     | 12 months |

```
POST /api/demo/real-estate/
Body: {
  "property_type": "premium",
  "amount": 2000
}
```

Response:
```json
{
  "success": true,
  "data": {
    "new_balance": "7000.00",
    "investment": {
      "id": 3,
      "investment_type": "real_estate",
      "asset_name": "Premium Property",
      "amount": "2000.00",
      "monthly_rate": "12.00",
      "duration_months": 12,
      "status": "active",
      "created_at": "2026-03-18T10:00:00Z"
    },
    "transaction": { ... }
  }
}
```

---

## Portfolio

Use this for the demo dashboard — returns everything in one call including live crypto values.

```
GET /api/demo/portfolio/
```

Response:
```json
{
  "success": true,
  "data": {
    "balance": "7000.00",
    "crypto_value": "522.20",
    "capital_plan_value": "1000.00",
    "real_estate_value": "2000.00",
    "total_invested": "3522.20",
    "total_portfolio_value": "10522.20",
    "investments": [ ...all active investments with live prices... ]
  }
}
```

To calculate unrealized P&L on a crypto holding:
```js
const unrealizedPnl = (inv.current_price - inv.price_at_purchase) * inv.quantity
const pnlPercent = ((inv.current_price - inv.price_at_purchase) / inv.price_at_purchase) * 100
```

---

## Investments List

```
GET /api/demo/investments/                        // all active
GET /api/demo/investments/?type=crypto            // crypto only
GET /api/demo/investments/?type=capital_plan      // capital plans only
GET /api/demo/investments/?type=real_estate       // real estate only
```

Response:
```json
{
  "success": true,
  "data": [ ...investments... ],
  "count": 3
}
```

---

## Transaction History

Supports pagination and type filtering.

```
GET /api/demo/transactions/
GET /api/demo/transactions/?limit=20&offset=0
GET /api/demo/transactions/?type=crypto_buy
```

Response:
```json
{
  "success": true,
  "data": [ ...transactions... ],
  "count": 20,
  "total": 87
}
```

### Transaction Types

| type                | When it appears                          |
|---------------------|------------------------------------------|
| `deposit`           | Account created, reset, or top-up        |
| `crypto_buy`        | Crypto purchased                         |
| `crypto_sell`       | Crypto sold                              |
| `investment`        | Capital plan or real estate invested     |
| `return`            | Investment return credited               |
| `binary_trade_open` | Binary trade placed (demo mode)          |
| `binary_trade_win`  | Binary trade won                         |
| `binary_trade_loss` | Binary trade lost                        |

Pagination example:
```js
const loadMore = async (page) => {
  const limit = 20
  const offset = page * limit
  const res = await api.get(`/demo/transactions/?limit=${limit}&offset=${offset}`)
  const hasMore = offset + res.data.count < res.data.total
}
```

---

## Binary Trading (Demo Mode)

No changes to the binary trading endpoints — just pass `is_demo: true`.

```
POST /api/binary/trade/open/
Body: {
  "asset_symbol": "BTC",
  "direction": "buy",
  "amount": 100,
  "expiry_seconds": 60,
  "is_demo": true
}
```

The stake is deducted from the demo balance. On close, a `binary_trade_win` or `binary_trade_loss` transaction is written to demo history automatically.

Get demo trade history:
```
GET /api/binary/history/?is_demo=true
```

Get demo stats:
```
GET /api/binary/stats/?is_demo=true
```

---

## Changes Required in Frontend Code

1. **Remove `price` from crypto buy requests** — it's ignored now, backend fetches it live
2. **Replace `POST /demo/invest/`** with `/demo/capital-plan/` or `/demo/real-estate/`
3. **Use `GET /demo/portfolio/`** for the demo dashboard instead of 3 separate calls
4. **Add pagination** to transaction history using `total` from the response
5. **Call `GET /demo/account/` on every demo page load** — it auto-creates the account so you'll never get a 404
6. **Never mix demo and real data** — always check `is_demo` flag and use separate state

---

## Error Responses

All errors follow this shape:
```json
{ "success": false, "error": "Insufficient demo balance" }
```

Common errors:
- `Insufficient demo balance` — user needs to reset or deposit
- `Unable to fetch live price for BTC` — CoinGecko API temporarily down, retry
- `Demo account not found` — shouldn't happen if you call `GET /demo/account/` first
- `coin is required` / `amount must be > 0` — validation errors, check request body
