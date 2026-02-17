# EXACOIN Buy Price Flow

## Summary

**EXACOIN buy price is served by these endpoints:**

1. **Display Price**: `GET /api/crypto/prices/` - Shows current buy price
2. **Execute Purchase**: `POST /api/crypto/buy/` - Uses buy price for transaction
3. **Admin Control**: `POST /api/admin/crypto-prices/update/` - Sets the buy price

---

## Complete Flow

### 1. Admin Sets EXACOIN Price

```http
POST /api/admin/crypto-prices/update/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "coin": "EXACOIN",
  "price": 130.00,
  "change24h": 48.5
}
```

**What happens:**
- Saves to `AdminCryptoPrice` table
- Sets `buy_price = 130.00`
- Sets `sell_price = 130.00` (same as buy for EXACOIN)

---

### 2. User Views EXACOIN Price

```http
GET /api/crypto/prices/
Authorization: Bearer <user_token>
```

**Response:**
```json
{
  "data": {
    "EXACOIN": {
      "price": 130.00,
      "change24h": 48.50,
      "change7d": 12.80,
      "change30d": 89.50
    },
    "BTC": { ... },
    "ETH": { ... }
  },
  "success": true
}
```

**What happens:**
- Queries `AdminCryptoPrice.objects.get(coin='EXACOIN')`
- Returns `buy_price` as the display price
- User sees current EXACOIN price in frontend

---

### 3. User Buys EXACOIN

```http
POST /api/crypto/buy/
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "coin": "EXACOIN",
  "amount": 100.00
}
```

**What happens:**
1. Gets `AdminCryptoPrice.objects.get(coin='EXACOIN')`
2. Uses `admin_price.buy_price` for calculation
3. Calculates `quantity = amount / buy_price`
4. Creates `Trade` record:
   ```python
   Trade.objects.create(
       user=user,
       asset='EXACOIN',
       trade_type='buy',
       entry_price=buy_price,  # 130.00
       current_price=buy_price,  # 130.00
       quantity=quantity,  # 0.76923077 (100/130)
       status='open'
   )
   ```
5. Deducts amount from user balance
6. Creates transaction record
7. Sends success notification

**Response:**
```json
{
  "data": {
    "investment": {
      "id": "uuid-here",
      "type": "crypto",
      "coin": "EXACOIN",
      "amount": "100.00",
      "quantity": "0.76923077",
      "price_at_purchase": "130.00",
      "status": "active",
      "date": "2026-02-17T10:30:00Z"
    },
    "new_balance": "900.00",
    "message": "Crypto purchase successful"
  },
  "success": true
}
```

---

## Database Tables Involved

### AdminCryptoPrice
```sql
SELECT * FROM investments_admincryptoprice WHERE coin = 'EXACOIN';

| coin    | buy_price | sell_price | change_24h | is_active |
|---------|-----------|------------|------------|-----------|
| EXACOIN | 130.00    | 130.00     | 48.50      | true      |
```

### Trade (User's Investment)
```sql
SELECT * FROM investments_trade WHERE asset = 'EXACOIN' AND user_id = 123;

| user_id | asset   | trade_type | entry_price | quantity   | status |
|---------|---------|------------|-------------|------------|--------|
| 123     | EXACOIN | buy        | 130.00      | 0.76923077 | open   |
```

---

## Key Points

✅ **Single Source of Truth**: `AdminCryptoPrice.buy_price` is used everywhere
✅ **Admin Control**: Only admin can change EXACOIN price
✅ **Real-time**: Price changes immediately affect new purchases
✅ **Consistent**: Same price used for display and transactions
✅ **Tracked**: All purchases recorded in Trade table with entry_price

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Who Uses |
|----------|--------|---------|----------|
| `/api/crypto/prices/` | GET | Display current prices | Users & Admin |
| `/api/crypto/buy/` | POST | Purchase crypto | Users |
| `/api/admin/crypto-prices/update/` | POST | Set EXACOIN price | Admin only |

---

## Testing the Flow

### 1. Set EXACOIN Price (Admin)
```bash
curl -X POST \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"coin":"EXACOIN","price":150.00,"change24h":60.0}' \
  https://growfun-backend.onrender.com/api/admin/crypto-prices/update/
```

### 2. Check Price (User)
```bash
curl -H "Authorization: Bearer <user_token>" \
  https://growfun-backend.onrender.com/api/crypto/prices/
```

### 3. Buy EXACOIN (User)
```bash
curl -X POST \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{"coin":"EXACOIN","amount":100.00}' \
  https://growfun-backend.onrender.com/api/crypto/buy/
```

---

## Recent Fix (Commit 5b15b65)

**Issue**: `crypto_buy` endpoint was trying to set non-existent `amount` field on Trade model

**Fix**: Removed `amount=amount` from Trade.objects.create() call

**Result**: EXACOIN purchases now work correctly without database errors