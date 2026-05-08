# Portfolio Profit/Loss Discrepancy - FIXED

## Problem Identified

The profit/loss values displayed in the **Portfolio** component were different from those shown in the **Dashboard/Overview** component.

### Root Cause

**Portfolio.js** (Line 190 - BEFORE FIX):
```javascript
const totalProfitLoss = totalCryptoValue - totalCryptoInvested;
```
- ❌ **Only calculated P&L for CRYPTO investments**
- ❌ **Completely ignored capital plans and real estate**
- ❌ **Did not use `current_value` from backend for non-crypto investments**

**Overview.js** (Lines 29-81):
```javascript
const calculateTotalProfits = () => {
  // Calculates current value for ALL investments
  safeInvestments.forEach((inv) => {
    if (isCrypto) {
      totalCurrentValue += quantity * currentPrice;
    } else {
      // For capital plans and real estate
      totalCurrentValue += parseFloat(inv.current_value) || amount;
    }
  });
  return totalCurrentValue - totalInvested;
};
```
- ✅ **Calculates P&L for ALL investment types** (crypto + capital + real estate)
- ✅ **Uses `current_value` from backend for non-crypto investments**

---

## Solution Implemented

Updated **Portfolio.js** to match the calculation logic in **Overview.js**:

### Changes Made

1. **Calculate current values for capital plans:**
```javascript
let totalCapitalPlansInvested = 0;
let totalCapitalPlansValue = 0;
capitalPlans.forEach(inv => {
  const amount = parseFloat(inv.amount) || 0;
  totalCapitalPlansInvested += amount;
  // Use current_value if provided by backend, otherwise use invested amount
  totalCapitalPlansValue += parseFloat(inv.current_value) || amount;
});
```

2. **Calculate current values for real estate:**
```javascript
let totalRealEstateInvested = 0;
let totalRealEstateValue = 0;
realEstateInvestments.forEach(inv => {
  const amount = parseFloat(inv.amount) || 0;
  totalRealEstateInvested += amount;
  // Use current_value if provided by backend, otherwise use invested amount
  totalRealEstateValue += parseFloat(inv.current_value) || amount;
});
```

3. **Calculate total P&L across ALL investment types:**
```javascript
const totalInvested = totalCryptoInvested + totalCapitalPlansInvested + totalRealEstateInvested;
const totalCurrentValue = totalCryptoValue + totalCapitalPlansValue + totalRealEstateValue;
const totalPortfolioValue = totalCurrentValue + (parseFloat(balance) || 0);
const totalProfitLoss = totalCurrentValue - totalInvested;
```

---

## What This Fixes

### Before Fix:
- **Portfolio P&L** = Crypto Current Value - Crypto Invested
- **Overview P&L** = (Crypto + Capital + Real Estate Current Value) - Total Invested
- ❌ **Numbers didn't match**

### After Fix:
- **Portfolio P&L** = (Crypto + Capital + Real Estate Current Value) - Total Invested
- **Overview P&L** = (Crypto + Capital + Real Estate Current Value) - Total Invested
- ✅ **Numbers now match perfectly**

---

## Backend Integration

Both components now properly use:
- `current_value` field from backend for capital plans and real estate
- `current_price` field from backend for crypto investments
- Fallback to invested amount if `current_value` is not provided

This ensures that when the backend calculates growth/returns for capital plans and real estate, the frontend displays the correct profit/loss.

---

## Testing

To verify the fix:

1. **Check Portfolio component:**
   - Navigate to Portfolio page
   - Look at the "Profit/Loss" card in the summary section

2. **Check Overview component:**
   - Navigate to Dashboard/Overview page
   - Look at the "Total Profits" card

3. **Verify they match:**
   - Both should show the same profit/loss value
   - Both should show the same percentage

4. **Test with different investment types:**
   - Add crypto investments → P&L should update
   - Add capital plans → P&L should update
   - Add real estate → P&L should update

---

## Files Modified

- `wazimu/Growfund-Dashboard/src/components/Portfolio.js`
  - Lines 183-207: Updated profit/loss calculation logic
  - Now includes current values for all investment types
  - Uses `current_value` from backend for non-crypto investments

---

## Status

✅ **FIXED** - Portfolio and Overview now show consistent profit/loss values across all investment types.
