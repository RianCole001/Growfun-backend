# Admin Privileges Summary - Prices & Minimums

## ✅ Admin Can Control Everything!

Admins have **full control** over both investment minimums and crypto prices through multiple interfaces.

---

## 1. Investment Minimums Control

### Django Admin Panel
**URL**: `http://localhost:8000/admin/settings_app/platformsettings/`

Admins can edit all investment minimums through organized sections:

#### Capital Plan Minimums
- ✅ **Basic Plan Minimum** (`capital_basic_min`) - Currently: $30.00
- ✅ **Standard Plan Minimum** (`capital_standard_min`) - Currently: $60.00
- ✅ **Advance Plan Minimum** (`capital_advance_min`) - Currently: $100.00

#### General Investment Minimums
- ✅ **Capital Plan Investment** (`min_capital_plan_investment`) - $500.00
- ✅ **Crypto Investment** (`min_crypto_investment`) - $50.00
- ✅ **Real Estate Investment** (`min_real_estate_investment`) - $1,000.00

#### Real Estate Minimums
- ✅ **Starter Property** (`real_estate_starter_min`) - $1,000.00
- ✅ **Premium Property** (`real_estate_premium_min`) - $5,000.00
- ✅ **Luxury Estate** (`real_estate_luxury_min`) - $20,000.00

### API Endpoint (Admin Only)
**Endpoint**: `GET/PUT /api/settings/`
**Permission**: Admin users only

```json
{
  "capitalBasicMin": 30.00,
  "capitalStandardMin": 60.00,
  "capitalAdvanceMin": 100.00,
  "minCapitalPlanInvestment": 500.00,
  "minCryptoInvestment": 50.00,
  "minRealEstateInvestment": 1000.00
}
```

---

## 2. Crypto Prices Control

### Django Admin Panel
**URL**: `http://localhost:8000/admin/investments/admincryptoprice/`

Admins can manage crypto prices with full control:

#### Available Fields
- ✅ **Coin Symbol** (e.g., EXACOIN, BTC, ETH)
- ✅ **Coin Name** (e.g., Exacoin, Bitcoin)
- ✅ **Buy Price** - Price users pay to buy
- ✅ **Sell Price** - Price users receive when selling
- ✅ **Spread** - Automatically calculated (buy - sell)
- ✅ **Spread Percentage** - Automatically calculated
- ✅ **24h Change** - Market change percentage
- ✅ **7d Change** - Weekly change percentage
- ✅ **30d Change** - Monthly change percentage
- ✅ **Is Active** - Enable/disable trading for this coin

#### Features
- View spread and spread percentage (read-only, auto-calculated)
- Track who updated prices and when
- Price history is automatically saved
- Can set any buy/sell price combination (no restrictions)

### API Endpoints (Admin Only)

#### Get All Crypto Prices
```
GET /api/investments/admin/crypto-prices/
Permission: Admin only
```

#### Update Single Crypto Price
```
POST /api/investments/admin/crypto-prices/update/
Permission: Admin only

Body:
{
  "coin": "EXACOIN",
  "buy_price": 62.00,
  "sell_price": 59.50,
  "change_24h": 3.33
}
```

#### Bulk Update Prices
```
POST /api/investments/admin/crypto-prices/bulk-update/
Permission: Admin only

Body:
{
  "prices": [
    {
      "coin": "EXACOIN",
      "buy_price": 62.00,
      "sell_price": 59.50
    },
    {
      "coin": "BTC",
      "buy_price": 65000.00,
      "sell_price": 63050.00
    }
  ]
}
```

#### Toggle Coin Active Status
```
POST /api/investments/admin/crypto-prices/{coin}/toggle/
Permission: Admin only
```

#### View Price History
```
GET /api/investments/admin/crypto-prices/{coin}/history/
Permission: Admin only
```

---

## 3. Additional Admin Controls

### Transaction Limits
- Min/Max Deposit amounts
- Min/Max Withdrawal amounts
- Deposit/Withdrawal fees

### Automation Settings
- Auto-approve deposits/withdrawals
- Auto-approve limits

### Referral Program
- Referral bonus amount

### Platform Settings
- Platform name and email
- Maintenance mode
- Email/SMS notifications

---

## 4. Security & Permissions

### Who Can Access?
- ✅ **Superusers** (`is_superuser=True`)
- ✅ **Staff users** (`is_staff=True`)
- ❌ Regular users cannot access admin features

### Audit Trail
- All changes are tracked with:
  - Who made the change (`updated_by`)
  - When it was changed (`updated_at`)
  - Settings history is automatically saved

### Protection
- Only one PlatformSettings instance allowed
- Settings cannot be deleted
- Price history cannot be modified or deleted

---

## 5. How to Access Admin Panel

1. **Login as Admin**
   - URL: `http://localhost:8000/admin/`
   - Use admin credentials

2. **Navigate to Settings**
   - Settings App → Platform Settings
   - Investments → Admin Crypto Prices

3. **Make Changes**
   - Edit any field
   - Click "Save"
   - Changes take effect immediately

---

## Summary

✅ **Investment Minimums**: Fully controllable via Django Admin & API
✅ **Crypto Prices**: Fully controllable via Django Admin & API  
✅ **No Restrictions**: Can set any price combination
✅ **Audit Trail**: All changes tracked
✅ **Secure**: Admin-only access
✅ **Real-time**: Changes apply immediately

**Admin has complete control over all pricing and minimum investment settings!**
