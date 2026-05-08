# Profit/Loss Calculation Reference

## Overview

Both **Portfolio** and **Overview** components now use the **same calculation logic** for profit/loss across all investment types.

---

## Calculation Formula

```javascript
Total P&L = Total Current Value - Total Invested

Where:
  Total Current Value = Crypto Current Value + Capital Plans Current Value + Real Estate Current Value
  Total Invested = Crypto Invested + Capital Plans Invested + Real Estate Invested
```

---

## Investment Type Breakdown

### 1. Crypto Investments

**Current Value Calculation:**
```javascript
currentValue = quantity × currentPrice
```

**Price Priority:**
1. Backend `current_price` field (highest priority)
2. Admin localStorage prices (for EXACOIN/OPTCOIN)
3. Live market prices from props
4. Fallback defaults (EXACOIN: $62, OPTCOIN: $85.30)

**P&L:**
```javascript
cryptoProfitLoss = totalCryptoValue - totalCryptoInvested
```

---

### 2. Capital Plans

**Current Value Calculation:**
```javascript
currentValue = inv.current_value || inv.amount
```

- Uses `current_value` from backend if available
- Falls back to invested `amount` if not provided
- Backend should calculate growth based on plan type and duration

**P&L:**
```javascript
capitalProfitLoss = totalCapitalPlansValue - totalCapitalPlansInvested
```

---

### 3. Real Estate

**Current Value Calculation:**
```javascript
currentValue = inv.current_value || inv.amount
```

- Uses `current_value` from backend if available
- Falls back to invested `amount` if not provided
- Backend should calculate appreciation based on property type

**P&L:**
```javascript
realEstateProfitLoss = totalRealEstateValue - totalRealEstateInvested
```

---

## Backend Integration

### Expected Fields from Backend

**Crypto Investments:**
```json
{
  "investment_type": "crypto",
  "asset": "BTC",
  "amount": 1000,
  "quantity": 0.025,
  "price_at_purchase": 40000,
  "current_price": 45000  // ← Backend provides this
}
```

**Capital Plans:**
```json
{
  "investment_type": "capital_plan",
  "plan_type": "standard",
  "amount": 5000,
  "current_value": 6500  // ← Backend calculates growth
}
```

**Real Estate:**
```json
{
  "investment_type": "real_estate",
  "name": "Premium Property",
  "amount": 10000,
  "current_value": 12000  // ← Backend calculates appreciation
}
```

---

## Component Locations

### Portfolio Component
**File:** `wazimu/Growfund-Dashboard/src/components/Portfolio.js`
**Lines:** 183-210 (profit/loss calculation)

### Overview Component
**File:** `wazimu/Growfund-Dashboard/src/components/Overview.js`
**Lines:** 29-81 (calculateTotalProfits function)

---

## Display Locations

### Portfolio Page
- **Summary Card:** "Profit/Loss" card shows total P&L
- **Crypto Table:** Individual P&L per coin
- **Percentage:** Calculated as `(totalProfitLoss / totalInvested) × 100`

### Dashboard/Overview Page
- **Summary Card:** "Total Profits" card shows total P&L
- **Percentage:** Calculated as `(totalProfits / totalInvested) × 100`

---

## Consistency Guarantee

✅ Both components now:
1. Calculate P&L for **all investment types** (not just crypto)
2. Use `current_value` from backend for capital plans and real estate
3. Use `current_price` from backend for crypto
4. Apply the same fallback logic
5. Show **identical profit/loss values**

---

## Testing Checklist

- [ ] Portfolio P&L matches Overview P&L
- [ ] Crypto investments show correct P&L
- [ ] Capital plans show correct P&L (if backend provides `current_value`)
- [ ] Real estate shows correct P&L (if backend provides `current_value`)
- [ ] Percentage calculations match between components
- [ ] Values update when prices change
- [ ] Values update when new investments are added

---

## Notes

- If backend doesn't provide `current_value` for capital plans/real estate, P&L will be $0 (current = invested)
- Backend should implement growth calculations for capital plans and real estate
- Admin-controlled prices (EXACOIN/OPTCOIN) are stored in localStorage
- Price updates trigger re-calculation via `priceUpdateTrigger` state
