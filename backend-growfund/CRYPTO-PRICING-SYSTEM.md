# Crypto Pricing System - How It Works

## Overview

The system has **ONE endpoint** for frontend to get all crypto prices, and **ONE endpoint** for admin to control EXACOIN price.

---

## For Frontend Developers

### Get All Crypto Prices (User & Admin)

```
GET /api/crypto/prices/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": {
    "EXACOIN": {
      "price": 125.50,
      "change24h": 45.20,
      "change7d": 12.80,
      "change30d": 89.50
    },
    "BTC": {
      "price": 64444.00,
      "change24h": 2.10,
      "change7d": -1.50,
      "change30d": 8.70
    },
    "ETH": {
      "price": 3200.00,
      "change24h": 1.80,
      "change7d": 3.20,
      "change30d": 15.40
    },
    "BNB": { ... },
    "ADA": { ... },
    "SOL": { ... },
    "DOT": { ... }
  },
  "success": true
}
```

**What You Get:**
- EXACOIN: Admin-controlled price from database
- BTC, ETH, BNB, ADA, SOL, DOT: Real-time prices from CoinGecko API
- All prices formatted with 2 decimal places
- All percentages formatted with 2 decimal places

**Usage:**
```javascript
// Fetch all crypto prices
const response = await axios.get('/api/crypto/prices/', {
  headers: { Authorization: `Bearer ${token}` }
});

const prices = response.data.data;
console.log(prices.EXACOIN.price);  // 125.50
console.log(prices.BTC.price);      // 64444.00 (live from CoinGecko)
```

---

## For Admin Panel

### Update EXACOIN Price (Admin Only)

```
POST /api/admin/crypto-prices/update/
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "coin": "EXACOIN",
  "price": 130.00,
  "change24h": 48.5,
  "change7d": 12.8,
  "change30d": 89.5
}
```

**Response:**
```json
{
  "data": {
    "coin": "EXACOIN",
    "price": 130.00,
    "change24h": 48.50,
    "change7d": 12.80,
    "change30d": 89.50,
    "updated_at": "2026-02-17T10:30:00Z"
  },
  "success": true
}
```

**Usage:**
```javascript
// Admin updates EXACOIN price
const response = await axios.post('/api/admin/crypto-prices/update/', {
  coin: 'EXACOIN',
  price: 130.00,
  change24h: 48.5
}, {
  headers: { Authorization: `Bearer ${adminToken}` }
});

// After update, frontend calls GET /api/crypto/prices/ to get new price
```

---

## How It Works Behind the Scenes

### 1. EXACOIN (Admin-Controlled)
- Stored in database table `AdminCryptoPrice`
- Admin can set any price they want
- Admin can set any change percentages (24h, 7d, 30d)
- Price persists until admin changes it again
- Default: $125.50 if not set by admin

### 2. Other Coins (Real-Time Market Prices)
- BTC, ETH, BNB, ADA, SOL, DOT
- Fetched from CoinGecko API every time endpoint is called
- Always shows current market prices
- Cannot be manipulated by admin
- Fallback to static prices if API fails (rare)

### 3. Data Flow

```
Frontend Request → Backend
                    ↓
            GET /api/crypto/prices/
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   EXACOIN                  Other Coins
   (Database)               (CoinGecko API)
        ↓                       ↓
        └───────────┬───────────┘
                    ↓
            Combine & Format
                    ↓
            Return to Frontend
```

---

## Admin Control Flow

```
Admin Panel → Update EXACOIN Price
                    ↓
        POST /api/admin/crypto-prices/update/
                    ↓
            Save to Database
                    ↓
        Log to Price History
                    ↓
            Return Success
                    ↓
    Frontend Refreshes Prices
                    ↓
        GET /api/crypto/prices/
                    ↓
        Shows New EXACOIN Price
```

---

## Key Points

✅ **ONE endpoint** for frontend: `GET /api/crypto/prices/`
✅ **ONE endpoint** for admin: `POST /api/admin/crypto-prices/update/`
✅ Admin controls **ONLY EXACOIN**
✅ All other coins are **real-time from CoinGecko**
✅ Frontend gets everything from one call
✅ All prices formatted consistently (2 decimals)
✅ All percentages formatted consistently (2 decimals)

---

## Testing

### Test User Endpoint
```bash
curl -H "Authorization: Bearer <token>" \
  https://growfun-backend.onrender.com/api/crypto/prices/
```

### Test Admin Update
```bash
curl -X POST \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"coin":"EXACOIN","price":150.00,"change24h":55.5}' \
  https://growfun-backend.onrender.com/api/admin/crypto-prices/update/
```

---

## Database Schema

### AdminCryptoPrice Model
```python
coin = CharField(max_length=10, unique=True)  # "EXACOIN"
name = CharField(max_length=50)               # "EXACOIN"
buy_price = DecimalField(max_digits=12, decimal_places=2)
sell_price = DecimalField(max_digits=12, decimal_places=2)
change_24h = DecimalField(max_digits=5, decimal_places=2)
change_7d = DecimalField(max_digits=5, decimal_places=2)
change_30d = DecimalField(max_digits=5, decimal_places=2)
is_active = BooleanField(default=True)
last_updated = DateTimeField(auto_now=True)
updated_by = ForeignKey(User)
```

### CryptoPriceHistory Model
```python
coin = CharField(max_length=10)
buy_price = DecimalField(max_digits=12, decimal_places=2)
sell_price = DecimalField(max_digits=12, decimal_places=2)
change_24h = DecimalField(max_digits=5, decimal_places=2)
updated_by = ForeignKey(User)
created_at = DateTimeField(auto_now_add=True)
```

---

## Troubleshooting

### Issue: EXACOIN not showing
**Solution**: Admin needs to set initial price via admin panel

### Issue: Other coins showing fallback prices
**Solution**: CoinGecko API might be down, prices will auto-update when API is back

### Issue: Prices not updating
**Solution**: Check authentication token, ensure user is logged in

### Issue: Admin can't update price
**Solution**: Ensure user has admin/staff permissions (is_staff=True or is_superuser=True)
