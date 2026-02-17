# 🎨 Django Admin Panel - Crypto Price Management Guide

## 🚀 Quick Start

After deployment and migrations, you'll manage crypto prices through the Django Admin Panel.

---

## 📍 Accessing the Admin Panel

### URL:
```
https://growfun-backend.onrender.com/admin/
```

### Login Credentials:
- **Email:** admin001@gmail.com
- **Password:** Your admin password

---

## 🎯 Managing Crypto Prices

### Step 1: Login to Admin Panel

1. Go to: https://growfun-backend.onrender.com/admin/
2. Enter your email and password
3. Click "Log in"

### Step 2: Navigate to Crypto Prices

You'll see the admin dashboard with sections:
```
ACCOUNTS
  └─ Users
  └─ Referrals

INVESTMENTS
  └─ Admin Crypto Prices  ← Click here!
  └─ Crypto Price History
  └─ Trades
  └─ Capital Investment Plans

NOTIFICATIONS
  └─ Notifications

TRANSACTIONS
  └─ Transactions
```

Click on **"Admin Crypto Prices"**

### Step 3: View All Crypto Prices

You'll see a table with your cryptocurrencies:

| Coin | Name | Buy Price | Sell Price | Spread | Active | Last Updated |
|------|------|-----------|------------|--------|--------|--------------|
| EXACOIN | Exacoin | $62.00 | $59.50 | $2.50 | ✓ | Feb 17, 2026 |
| BTC | Bitcoin | $65,000.00 | $63,050.00 | $1,950.00 | ✓ | Feb 17, 2026 |
| ETH | Ethereum | $3,200.00 | $3,104.00 | $96.00 | ✓ | Feb 17, 2026 |
| USDT | Tether | $1.00 | $0.97 | $0.03 | ✓ | Feb 17, 2026 |

---

## ✏️ Editing Crypto Prices

### To Update a Price:

1. **Click on the coin name** (e.g., "EXACOIN")
2. You'll see the edit form:

```
Coin: EXACOIN
Name: Exacoin

Buy price: [62.00]  ← Price users pay to buy
Sell price: [59.50] ← Price users receive when selling

Change 24h: [3.33]
Change 7d: [12.80]
Change 30d: [89.50]

Is active: [✓] ← Uncheck to disable trading

Last updated: Feb 17, 2026, 10:30 a.m.
Updated by: admin001@gmail.com
```

3. **Change the values** you want to update
4. **Click "Save"** at the bottom
5. **Done!** Prices update immediately for all users

### Important Rules:

✅ **Sell price MUST be less than buy price**
- Example: Buy $62.00, Sell $59.50 ✓
- Example: Buy $62.00, Sell $65.00 ✗ (Error!)

✅ **Recommended spread: 3-5%**
- This ensures platform profitability
- Formula: `(Buy - Sell) / Buy × 100`

✅ **Prices must be positive**
- No negative or zero prices allowed

---

## ➕ Adding New Cryptocurrencies

### To Add a New Coin:

1. Click **"Add Admin Crypto Price"** button (top right)
2. Fill in the form:

```
Coin: [BNB]           ← Coin symbol (uppercase)
Name: [Binance Coin]  ← Full name

Buy price: [450.00]   ← Set buy price
Sell price: [437.00]  ← Set sell price (must be < buy)

Change 24h: [2.50]    ← 24-hour change %
Change 7d: [5.00]     ← 7-day change %
Change 30d: [15.00]   ← 30-day change %

Is active: [✓]        ← Check to enable trading
```

3. Click **"Save"**
4. New coin is now available for trading!

---

## 🔄 Common Tasks

### 1. Update EXACOIN Price to $70

1. Click "Admin Crypto Prices"
2. Click "EXACOIN"
3. Change `Buy price` to `70.00`
4. Change `Sell price` to `67.00` (maintain ~4% spread)
5. Click "Save"

### 2. Disable BTC Trading

1. Click "Admin Crypto Prices"
2. Click "BTC"
3. Uncheck `Is active`
4. Click "Save"
5. Users can no longer buy/sell BTC

### 3. Add Market Changes

1. Click on any crypto
2. Update `Change 24h`, `Change 7d`, `Change 30d`
3. Click "Save"
4. Users see updated market trends

### 4. Bulk Update Multiple Coins

**Option A: Via Admin Panel**
1. Select multiple coins (checkboxes)
2. Choose action from dropdown
3. Click "Go"

**Option B: Via API (Faster)**
```bash
curl -X POST "https://growfun-backend.onrender.com/api/investments/admin/crypto-prices/bulk-update/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prices": [
      {"coin": "EXACOIN", "buy_price": 70.00, "sell_price": 67.00},
      {"coin": "BTC", "buy_price": 66000.00, "sell_price": 64020.00},
      {"coin": "ETH", "buy_price": 3300.00, "sell_price": 3201.00}
    ]
  }'
```

---

## 📊 Viewing Price History

### To See All Price Changes:

1. Click "Crypto Price History" (in INVESTMENTS section)
2. You'll see all historical changes:

| Coin | Buy Price | Sell Price | Updated By | Created At |
|------|-----------|------------|------------|------------|
| EXACOIN | $70.00 | $67.00 | admin001@gmail.com | Feb 17, 2026, 11:00 |
| EXACOIN | $65.00 | $62.00 | admin001@gmail.com | Feb 17, 2026, 10:45 |
| EXACOIN | $62.00 | $59.50 | admin001@gmail.com | Feb 17, 2026, 10:30 |

This provides a complete audit trail of all price changes!

---

## 💡 Best Practices

### 1. Maintain Consistent Spreads
```
EXACOIN: 4.03% spread
BTC: 3.00% spread
ETH: 3.00% spread
USDT: 3.00% spread
```

### 2. Update Prices Regularly
- Check market prices daily
- Adjust to maintain competitiveness
- Keep spreads profitable (3-5%)

### 3. Monitor User Activity
- Check which coins are popular
- Adjust prices based on demand
- Disable low-volume coins if needed

### 4. Test Before Major Changes
- Update one coin first
- Verify frontend displays correctly
- Then update others

### 5. Document Price Changes
- Price history is automatic
- But keep notes on why you changed prices
- Helps with future decisions

---

## 🎯 Spread Calculator

Use this to calculate optimal prices:

### Formula:
```
Spread % = (Buy Price - Sell Price) / Buy Price × 100
```

### Examples:

**3% Spread:**
- Buy: $100.00
- Sell: $97.00
- Spread: $3.00 (3%)

**4% Spread:**
- Buy: $100.00
- Sell: $96.00
- Spread: $4.00 (4%)

**5% Spread:**
- Buy: $100.00
- Sell: $95.00
- Spread: $5.00 (5%)

### Quick Reference Table:

| Buy Price | 3% Spread | 4% Spread | 5% Spread |
|-----------|-----------|-----------|-----------|
| $50.00 | $48.50 | $48.00 | $47.50 |
| $100.00 | $97.00 | $96.00 | $95.00 |
| $500.00 | $485.00 | $480.00 | $475.00 |
| $1,000.00 | $970.00 | $960.00 | $950.00 |
| $10,000.00 | $9,700.00 | $9,600.00 | $9,500.00 |

---

## 🔐 Security Tips

1. **Keep admin credentials secure**
   - Don't share your password
   - Use a strong password
   - Change it regularly

2. **Only trusted admins should have access**
   - Price changes affect all users
   - Wrong prices can cause losses

3. **Monitor price history**
   - Check who made changes
   - Verify changes are correct
   - Investigate suspicious activity

---

## 🆘 Troubleshooting

### Error: "Sell price must be less than buy price"
**Solution:** Make sure sell price is lower than buy price

### Error: "Ensure that there are no more than 4 decimal places"
**Solution:** Use max 4 decimal places (e.g., 3.3300, not 3.33333)

### Can't save changes
**Solution:** Check all validation rules are met

### Prices not updating on frontend
**Solution:** 
1. Clear browser cache
2. Check if coin is active
3. Verify API endpoint returns new prices

---

## 📞 Quick Reference

### Admin Panel URL:
```
https://growfun-backend.onrender.com/admin/
```

### Key Sections:
- **Admin Crypto Prices** - Manage current prices
- **Crypto Price History** - View all changes
- **Users** - Manage user accounts
- **Transactions** - View all trades

### Keyboard Shortcuts:
- `Ctrl + S` - Save changes
- `Ctrl + Z` - Undo (in text fields)
- `Esc` - Cancel/Go back

---

## 🎉 You're Ready!

You now know how to:
✅ Access the admin panel
✅ View all crypto prices
✅ Edit existing prices
✅ Add new cryptocurrencies
✅ Disable/enable trading
✅ View price history
✅ Calculate optimal spreads

**Start managing your crypto prices like a pro!** 🚀
