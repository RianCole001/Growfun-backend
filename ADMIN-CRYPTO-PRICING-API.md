# 🪙 Admin Crypto Pricing System - Complete API Documentation

## 🎯 **Overview**

This system allows admins to control cryptocurrency buy/sell prices with spreads. Users trade at admin-set prices, ensuring profitability through the spread.

### **Key Features:**
- ✅ Admin-controlled buy/sell prices
- ✅ Automatic spread calculation (3-5% recommended)
- ✅ Price history tracking for audit trail
- ✅ Enable/disable trading per coin
- ✅ Bulk price updates
- ✅ Real-time price changes

---

## 📊 **Database Models**

### **AdminCryptoPrice**
```python
{
    "coin": "EXACOIN",           # Unique coin symbol
    "name": "Exacoin",           # Full coin name
    "buy_price": 62.00,          # Price users pay to buy
    "sell_price": 59.50,         # Price users receive when selling
    "spread": 2.50,              # Calculated: buy_price - sell_price
    "spread_percentage": 4.03,   # Calculated: (spread / buy_price) * 100
    "change_24h": 3.33,          # 24-hour price change %
    "change_7d": 12.80,          # 7-day price change %
    "change_30d": 89.50,         # 30-day price change %
    "is_active": true,           # Enable/disable trading
    "last_updated": "2024-02-17T10:30:00Z",
    "updated_by": "admin@growfund.com"
}
```

### **CryptoPriceHistory**
Automatically tracks all price changes for audit trail.

---

## 🔐 **Admin API Endpoints**

### **1. Get All Crypto Prices**
```http
GET /api/investments/admin/crypto-prices/
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "EXACOIN": {
      "id": 1,
      "coin": "EXACOIN",
      "name": "Exacoin",
      "buy_price": "62.00",
      "sell_price": "59.50",
      "spread": "2.50",
      "spread_percentage": 4.03,
      "change_24h": 3.33,
      "change_7d": 12.80,
      "change_30d": 89.50,
      "is_active": true,
      "last_updated": "2024-02-17T10:30:00Z",
      "updated_by": "admin@growfund.com"
    },
    "BTC": {
      "id": 2,
      "coin": "BTC",
      "name": "Bitcoin",
      "buy_price": "65000.00",
      "sell_price": "63050.00",
      "spread": "1950.00",
      "spread_percentage": 3.00,
      "change_24h": 2.10,
      "is_active": true,
      "last_updated": "2024-02-17T10:30:00Z"
    }
  }
}
```

### **2. Update/Create Crypto Price**
```http
PUT /api/investments/admin/crypto-prices/update/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "coin": "EXACOIN",
  "buy_price": 62.00,
  "sell_price": 59.50,
  "change_24h": 3.33,
  "change_7d": 12.80,
  "change_30d": 89.50
}
```

**Validation Rules:**
- `sell_price` must be less than `buy_price`
- Spread must be at least 2% (recommended 3-5%)
- Prices must be positive

**Response:**
```json
{
  "success": true,
  "message": "Price for EXACOIN updated successfully",
  "data": {
    "coin": "EXACOIN",
    "buy_price": "62.00",
    "sell_price": "59.50",
    "spread": "2.50",
    "spread_percentage": 4.03,
    "change_24h": 3.33,
    "last_updated": "2024-02-17T10:30:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "errors": {
    "sell_price": ["Spread too low (1.50%). Recommended: 3-5%."]
  }
}
```

### **3. Bulk Update Prices**
```http
POST /api/investments/admin/crypto-prices/bulk-update/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "prices": [
    {
      "coin": "EXACOIN",
      "buy_price": 62.00,
      "sell_price": 59.50,
      "change_24h": 3.33
    },
    {
      "coin": "BTC",
      "buy_price": 65000.00,
      "sell_price": 63050.00,
      "change_24h": 2.10
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Updated 2 prices",
  "updated": ["EXACOIN", "BTC"],
  "errors": null
}
```

### **4. Toggle Coin Trading**
```http
POST /api/investments/admin/crypto-prices/EXACOIN/toggle/
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "message": "EXACOIN trading enabled",
  "data": {
    "coin": "EXACOIN",
    "is_active": true
  }
}
```

### **5. Get Price History**
```http
GET /api/investments/admin/crypto-prices/EXACOIN/history/
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 15,
      "coin": "EXACOIN",
      "buy_price": "62.00",
      "sell_price": "59.50",
      "change_24h": 3.33,
      "updated_by_email": "admin@growfund.com",
      "created_at": "2024-02-17T10:30:00Z"
    },
    {
      "id": 14,
      "coin": "EXACOIN",
      "buy_price": "60.00",
      "sell_price": "58.00",
      "change_24h": 2.50,
      "updated_by_email": "admin@growfund.com",
      "created_at": "2024-02-16T15:20:00Z"
    }
  ]
}
```

---

## 👥 **User API Endpoints**

### **1. Get Public Crypto Prices**
```http
GET /api/investments/crypto/prices/
Authorization: Bearer {user_token}
```

**Response (Users see buy prices only):**
```json
{
  "data": {
    "EXACOIN": {
      "price": 62.00,
      "change24h": 3.33,
      "change7d": 12.80,
      "change30d": 89.50
    },
    "BTC": {
      "price": 65000.00,
      "change24h": 2.10,
      "change7d": -1.50,
      "change30d": 8.70
    }
  }
}
```

### **2. Buy Cryptocurrency**
```http
POST /api/investments/crypto/buy/
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "coin": "EXACOIN",
  "amount": 1000.00
}
```

**Logic:**
1. Get admin buy_price for EXACOIN
2. Calculate quantity = amount / buy_price
3. Deduct amount from user balance
4. Create investment record
5. Create transaction record

**Response:**
```json
{
  "data": {
    "investment": {
      "id": 123,
      "type": "crypto",
      "coin": "EXACOIN",
      "amount": "1000.00",
      "quantity": "16.12903226",
      "price_at_purchase": "62.00",
      "status": "active",
      "date": "2024-02-17T10:30:00Z"
    },
    "transaction": {
      "id": 123,
      "type": "Crypto Purchase",
      "amount": "1000.00",
      "asset": "EXACOIN",
      "quantity": "16.12903226",
      "price": "62.00",
      "status": "completed"
    },
    "new_balance": "4000.00",
    "message": "Crypto purchase successful"
  }
}
```

### **3. Sell Cryptocurrency**
```http
POST /api/investments/crypto/sell/
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "investment_id": 123,
  "coin": "EXACOIN",
  "quantity": 16.12903226
}
```

**Logic:**
1. Get admin sell_price for EXACOIN
2. Calculate amount = quantity * sell_price
3. Verify user owns the crypto
4. Calculate P&L = (sell_price - buy_price) * quantity
5. Credit amount to user balance
6. Update/close investment record
7. Create transaction record

**Response:**
```json
{
  "data": {
    "transaction": {
      "id": 123,
      "type": "Crypto Sale",
      "amount": "959.68",
      "asset": "EXACOIN",
      "quantity": "16.12903226",
      "price": "59.50",
      "status": "completed",
      "date": "2024-02-17T11:00:00Z"
    },
    "new_balance": "4959.68",
    "updated_investment": null,
    "profit_loss": "-40.32",
    "message": "Crypto sale successful"
  }
}
```

---

## 💰 **Spread Management**

### **Recommended Spreads:**
- **3-5%**: Standard spread for profitability
- **2-3%**: Competitive spread for high-volume coins
- **5-10%**: Higher spread for volatile/low-volume coins

### **Spread Calculation:**
```
Spread = Buy Price - Sell Price
Spread % = (Spread / Buy Price) * 100

Example:
Buy Price: $62.00
Sell Price: $59.50
Spread: $2.50
Spread %: 4.03%
```

### **Profitability Example:**
```
User buys 10 EXACOIN:
- Pays: 10 * $62.00 = $620.00

User sells 10 EXACOIN:
- Receives: 10 * $59.50 = $595.00

Platform profit: $620.00 - $595.00 = $25.00 (4.03%)
```

---

## 🔒 **Permissions**

### **Admin Endpoints:**
- Require `IsAuthenticated` + `IsAdminUser` (is_staff=True)
- Only admins can view/update prices
- Price changes are logged with admin user

### **User Endpoints:**
- Require `IsAuthenticated` only
- Users see buy prices only
- Users trade at admin-set prices

---

## 🧪 **Testing**

### **1. Set Initial Prices (Admin)**
```bash
curl -X PUT "https://growfun-backend.onrender.com/api/investments/admin/crypto-prices/update/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coin": "EXACOIN",
    "buy_price": 62.00,
    "sell_price": 59.50,
    "change_24h": 3.33
  }'
```

### **2. Check Public Prices (User)**
```bash
curl -X GET "https://growfun-backend.onrender.com/api/investments/crypto/prices/" \
  -H "Authorization: Bearer USER_TOKEN"
```

### **3. Buy Crypto (User)**
```bash
curl -X POST "https://growfun-backend.onrender.com/api/investments/crypto/buy/" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "coin": "EXACOIN",
    "amount": 1000.00
  }'
```

### **4. Sell Crypto (User)**
```bash
curl -X POST "https://growfun-backend.onrender.com/api/investments/crypto/sell/" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "investment_id": 123,
    "coin": "EXACOIN",
    "quantity": 16.12903226
  }'
```

---

## 🚀 **Deployment Steps**

### **1. Run Migrations**
```bash
python manage.py makemigrations investments
python manage.py migrate
```

### **2. Create Initial Prices (Django Admin or API)**
```python
from investments.admin_models import AdminCryptoPrice

AdminCryptoPrice.objects.create(
    coin='EXACOIN',
    name='Exacoin',
    buy_price=62.00,
    sell_price=59.50,
    change_24h=3.33,
    is_active=True
)
```

### **3. Test Endpoints**
Use the testing commands above to verify functionality.

---

## 🎯 **Frontend Integration**

Your frontend is already built and ready! It will:
- Display admin-controlled prices to users
- Use buy prices for purchases
- Use sell prices for sales
- Show real-time spread-based pricing

**No frontend changes needed** - just deploy the backend and it works! 🚀

---

## 📞 **Support**

The system is production-ready with:
- ✅ Admin price control
- ✅ Automatic spread calculation
- ✅ Price history tracking
- ✅ Transaction integrity
- ✅ Notification system
- ✅ Full audit trail

**Your crypto trading platform is now complete with admin-controlled pricing!** 🎉