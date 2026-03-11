# Capital Plan Minimum Investment Update

## ✅ Changes Applied

### Updated Minimum Investment Amounts

The minimum investment amounts for capital plans have been updated:

| Plan Type | Old Minimum | New Minimum |
|-----------|-------------|-------------|
| **Basic** | $100.00 | **$30.00** |
| **Standard** | $500.00 | **$60.00** |
| **Advance** | $2,000.00 | **$100.00** |

### Validation Added

✅ **Automatic validation** now enforces these minimums when users create investment plans.

If a user tries to invest less than the minimum:
- **Basic Plan**: Must invest at least $30.00
- **Standard Plan**: Must invest at least $60.00
- **Advance Plan**: Must invest at least $100.00

### Error Messages

Users will receive clear error messages if they try to invest below the minimum:

```json
{
  "initial_amount": "Minimum investment for Basic plan is $30.00"
}
```

## How It Works

1. **Database Updated**: Platform settings now store the new minimums
2. **Validation Active**: Investment creation automatically checks minimums
3. **Dynamic Settings**: Admins can update these minimums through the admin panel

## Testing

To test the validation, try creating an investment with an amount below the minimum:

```bash
# This will fail - amount too low for Basic plan
POST /api/investments/capital-plans/
{
  "plan_type": "basic",
  "initial_amount": 25.00,
  "period_months": 6
}

# This will succeed
POST /api/investments/capital-plans/
{
  "plan_type": "basic",
  "initial_amount": 30.00,
  "period_months": 6
}
```

## Admin Panel

Admins can view and modify these minimums at:
- **URL**: http://localhost:8000/admin/settings_app/platformsettings/
- **Fields**: 
  - `capital_basic_min`
  - `capital_standard_min`
  - `capital_advance_min`

## Files Modified

1. `settings_app/models.py` - Updated default minimum values
2. `investments/serializers.py` - Added validation logic
3. Database migration created and applied
4. Platform settings updated in database

---

**Status**: ✅ Complete and Active
**Server**: Running at http://127.0.0.1:8000/
