# Capital Investment Plan - Complete Guide

## Overview

The Capital Investment Plan system allows users to invest capital with monthly growth rates. Three plan types are available with different growth rates and customizable periods.

---

## Plan Types

### 1. Basic Plan
- **Monthly Growth**: 20%
- **Best For**: Conservative investors
- **Example**: $1,000 invested for 3 months
  - Month 1: $1,000 → $1,200 (gain: $200)
  - Month 2: $1,200 → $1,440 (gain: $240)
  - Month 3: $1,440 → $1,728 (gain: $288)
  - **Total Return**: $728 (72.8%)

### 2. Standard Plan
- **Monthly Growth**: 30%
- **Best For**: Moderate investors
- **Example**: $1,000 invested for 3 months
  - Month 1: $1,000 → $1,300 (gain: $300)
  - Month 2: $1,300 → $1,690 (gain: $390)
  - Month 3: $1,690 → $2,197 (gain: $507)
  - **Total Return**: $1,197 (119.7%)

### 3. Advance Plan
- **Monthly Growth**: 40%, 50%, or 60% (user selectable)
- **Best For**: Aggressive investors
- **Example 1 (40%)**: $1,000 invested for 3 months
  - Month 1: $1,000 → $1,400 (gain: $400)
  - Month 2: $1,400 → $1,960 (gain: $560)
  - Month 3: $1,960 → $2,744 (gain: $784)
  - **Total Return**: $1,744 (174.4%)

- **Example 2 (50%)**: $1,000 invested for 3 months
  - Month 1: $1,000 → $1,500 (gain: $500)
  - Month 2: $1,500 → $2,250 (gain: $750)
  - Month 3: $2,250 → $3,375 (gain: $1,125)
  - **Total Return**: $2,375 (237.5%)

- **Example 3 (60%)**: $1,000 invested for 3 months
  - Month 1: $1,000 → $1,600 (gain: $600)
  - Month 2: $1,600 → $2,560 (gain: $960)
  - Month 3: $2,560 → $4,096 (gain: $1,536)
  - **Total Return**: $3,096 (309.6%)

---

## Investment Period

- **Minimum**: 1 month
- **Maximum**: 60 months (5 years)
- **Flexibility**: Choose any period between 1-60 months
- **Common Periods**: 3, 6, 12, 24, 36 months

---

## API Endpoints

### Create Investment Plan
```
POST /api/investments/investment-plans/
Authorization: Bearer <token>

Request:
{
  "plan_type": "advance",
  "initial_amount": 1000.00,
  "period_months": 3,
  "growth_rate": 40.00
}

Response:
{
  "id": "uuid-here",
  "plan_type": "advance",
  "status": "active",
  "initial_amount": 1000.00,
  "period_months": 3,
  "growth_rate": 40.00,
  "total_return": 1744.00,
  "final_amount": 2744.00,
  "monthly_growth": [
    {
      "month": 1,
      "starting_amount": 1000.00,
      "growth_rate": 40.00,
      "monthly_gain": 400.00,
      "ending_amount": 1400.00
    },
    {
      "month": 2,
      "starting_amount": 1400.00,
      "growth_rate": 40.00,
      "monthly_gain": 560.00,
      "ending_amount": 1960.00
    },
    {
      "month": 3,
      "starting_amount": 1960.00,
      "growth_rate": 40.00,
      "monthly_gain": 784.00,
      "ending_amount": 2744.00
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "start_date": "2024-01-15T10:30:00Z",
  "end_date": "2024-04-15T10:30:00Z",
  "completed_at": null,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Investment Plan Details
```
GET /api/investments/investment-plans/{id}/
Authorization: Bearer <token>

Response: (Same as above with detailed monthly breakdown)
```

### List All Investment Plans
```
GET /api/investments/investment-plans/
Authorization: Bearer <token>

Response:
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    { ... plan 1 ... },
    { ... plan 2 ... }
  ]
}
```

### Get Active Plans
```
GET /api/investments/investment-plans/active_plans/
Authorization: Bearer <token>

Response: List of active plans only
```

### Get Completed Plans
```
GET /api/investments/investment-plans/completed_plans/
Authorization: Bearer <token>

Response: List of completed plans only
```

### Get Investment Summary
```
GET /api/investments/investment-plans/summary/
Authorization: Bearer <token>

Response:
{
  "total_invested": 5000.00,
  "total_returns": 2500.00,
  "active_plans": 2,
  "completed_plans": 1,
  "total_plans": 3
}
```

### Complete Investment Plan
```
POST /api/investments/investment-plans/{id}/complete/
Authorization: Bearer <token>

Response: Updated plan with status='completed'
```

### Cancel Investment Plan
```
POST /api/investments/investment-plans/{id}/cancel/
Authorization: Bearer <token>

Response: Updated plan with status='cancelled'
```

---

## Database Schema

### CapitalInvestmentPlan Model
```
id (UUID, Primary Key)
user (Foreign Key to User)
plan_type (CharField: basic, standard, advance)
status (CharField: active, completed, cancelled)
initial_amount (Decimal)
period_months (Integer)
growth_rate (Decimal: 20, 30, 40, 50, 60)
total_return (Decimal, calculated)
final_amount (Decimal, calculated)
monthly_growth (JSON: array of monthly breakdown)
created_at (DateTime)
start_date (DateTime)
end_date (DateTime, calculated)
completed_at (DateTime, nullable)
updated_at (DateTime)
```

---

## Monthly Growth Calculation

The system uses compound growth calculation:

```
For each month:
  monthly_gain = current_amount * (growth_rate / 100)
  current_amount = current_amount + monthly_gain

Example (40% growth, $1,000 initial):
  Month 1: 1000 * 0.40 = 400 gain → 1400
  Month 2: 1400 * 0.40 = 560 gain → 1960
  Month 3: 1960 * 0.40 = 784 gain → 2744
```

---

## Features

✅ **Three Plan Types**: Basic (20%), Standard (30%), Advance (40/50/60%)
✅ **Flexible Periods**: 1-60 months
✅ **Monthly Breakdown**: Detailed month-by-month growth tracking
✅ **Compound Growth**: Realistic investment returns
✅ **Plan Management**: Create, view, complete, cancel plans
✅ **Summary Statistics**: Total invested, returns, active/completed counts
✅ **User Isolation**: Each user sees only their own plans
✅ **Status Tracking**: Active, completed, cancelled states

---

## Usage Examples

### Example 1: Create Basic Plan
```python
# User invests $5,000 for 6 months at 20% monthly growth
POST /api/investments/investment-plans/
{
  "plan_type": "basic",
  "initial_amount": 5000.00,
  "period_months": 6
}

# Result: $5,000 → $12,441.60 (Total return: $7,441.60)
```

### Example 2: Create Advance Plan (50%)
```python
# User invests $10,000 for 12 months at 50% monthly growth
POST /api/investments/investment-plans/
{
  "plan_type": "advance",
  "initial_amount": 10000.00,
  "period_months": 12,
  "growth_rate": 50.00
}

# Result: $10,000 → $129,746.30 (Total return: $119,746.30)
```

### Example 3: Create Standard Plan
```python
# User invests $2,500 for 3 months at 30% monthly growth
POST /api/investments/investment-plans/
{
  "plan_type": "standard",
  "initial_amount": 2500.00,
  "period_months": 3
}

# Result: $2,500 → $5,492.50 (Total return: $2,992.50)
```

---

## Implementation Steps

### Step 1: Apply Migration
```bash
cd backend-growfund
py manage.py migrate investments
```

### Step 2: Register ViewSet in Admin (Optional)
```python
# In investments/admin.py
from django.contrib import admin
from .models import CapitalInvestmentPlan

@admin.register(CapitalInvestmentPlan)
class CapitalInvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'status', 'initial_amount', 'final_amount', 'created_at')
    list_filter = ('plan_type', 'status', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('id', 'total_return', 'final_amount', 'monthly_growth', 'created_at', 'updated_at')
```

### Step 3: Test API Endpoints
```bash
# Create a plan
curl -X POST http://localhost:8000/api/investments/investment-plans/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "advance",
    "initial_amount": 1000,
    "period_months": 3,
    "growth_rate": 40
  }'

# Get summary
curl -X GET http://localhost:8000/api/investments/investment-plans/summary/ \
  -H "Authorization: Bearer <token>"
```

---

## Validation Rules

### Plan Type Validation
- Basic: Always 20% growth
- Standard: Always 30% growth
- Advance: Must be 40%, 50%, or 60%

### Amount Validation
- Must be greater than 0
- Supports decimal values (e.g., 1000.50)

### Period Validation
- Minimum: 1 month
- Maximum: 60 months
- Must be integer

---

## Error Handling

### Invalid Plan Type
```
Error: Invalid plan type
Solution: Use 'basic', 'standard', or 'advance'
```

### Invalid Growth Rate for Advance
```
Error: Advance plan growth rate must be 40%, 50%, or 60%
Solution: Use one of the allowed rates
```

### Invalid Amount
```
Error: Initial amount must be greater than 0
Solution: Provide positive amount
```

### Invalid Period
```
Error: Period must be between 1 and 60 months
Solution: Use valid period range
```

---

## Performance Considerations

- Monthly breakdown is calculated on save
- Stored as JSON for quick retrieval
- No ongoing calculations needed
- Efficient for large number of plans

---

## Future Enhancements

1. **Partial Withdrawal**: Allow withdrawing funds before completion
2. **Reinvestment**: Automatically reinvest returns
3. **Notifications**: Alert users when plan completes
4. **Performance Tracking**: Compare actual vs projected returns
5. **Tax Reporting**: Generate tax documents
6. **Dividend Distribution**: Distribute returns periodically

---

## Summary

The Capital Investment Plan system provides:
- Three investment tiers with different growth rates
- Flexible investment periods (1-60 months)
- Detailed monthly breakdown of returns
- Compound growth calculations
- Complete plan management (create, view, complete, cancel)
- User-specific plan isolation
- Comprehensive API endpoints

Users can now invest capital with predictable monthly growth and track their investments in detail.
