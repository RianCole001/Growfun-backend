# EXACOIN Buy Price Flow - Backend Endpoints

## Summary
The EXACOIN buy price is served by **TWO different endpoints** depending on the context:

## 1. For Users (Frontend Trading) - `/api/crypto/prices/`
**File:** `backend-growfund/investments/views.py` - `crypto_prices()` function (line ~650)
**Endpoint:** `GET /api/crypto/prices/`
**Purpose:** Users see this price when trading/viewing crypto prices
**Response Format:**
```json
{
  "data": {
    "EXACOIN": {
      "price": 125.50,
      "change24h": 45.20,
      "change7d": 12.80,
      "change30d": 89.50
    }
  },
  "success": true
}
```

## 2. For Admin (Price Management) - `/api/investments/admin/crypto-prices/`
**File:** `backend-growfund/investments/admin_crypto_views.py` - `admin_get_crypto_prices()` function
**Endpoint:** `GET /api/investments/admin/crypto-prices/`
**Purpose:** Admin manages and views detailed price information
**Response Format:**
```json
{
  "data": {
    "EXACOIN": {
      "id": 1,
      "coin": "EXACOIN",
      "name": "EXACOIN",
      "buy_price": "125.50",
      "sell_price": "122.00",
      "spread": "3.50",
      "spread_percentage": 2.87,
      "change_24h": 45.20,
      "change_7d": 12.80,
      "change_30d": 89.50,
      "is_active": true,
      "last_updated": "2026-02-19T10:30:00Z",
      "updated_by": "admin@growfund.com"
    }
  },
  "success": true
}
```

## Key Differences:
1. **User endpoint** returns `price` (number) - this is the buy price users see
2. **Admin endpoint** returns `buy_price` (string) and `sell_price` (string) - admin sees both prices
3. **Data source:** Both read from `AdminCryptoPrice` model in database
4. **Frontend issue:** Admin endpoint returns strings, but frontend expects numbers (needs parseFloat)

## Current Fix Applied:
- Added `parseFloat()` in AdminPriceControl.js `loadCurrentPrices()` function
- Fixed both AdminPriceControl files:
  - `Grow dashboard/src/admin/AdminPriceControl.js` 
  - `Grow dashboard/Growfund-Dashboard/trading-dashboard/src/admin/AdminPriceControl.js`

## API Endpoints in Frontend:
- **User API:** `userAuthAPI.getCryptoPrices()` → `/api/crypto/prices/`
- **Admin API:** `adminAuthAPI.getCryptoPrices()` → `/api/investments/admin/crypto-prices/`