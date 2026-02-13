# Capital Investment Plan - API Reference

## Base URL
```
http://localhost:8000/api/investments/investment-plans/
```

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📝 Endpoints

### 1. Create Investment Plan
**POST** `/api/investments/investment-plans/`

**Request:**
```json
{
  "plan_type": "basic",
  "initial_amount": 1000,
  "period_months": 6,
  "growth_rate": 20
}
```

**Valid plan_type values:**
- `basic` (growth_rate: 20)
- `standard` (growth_rate: 30)
- `advance` (growth_rate: 40, 50, or 60)

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_type": "basic",
  "status": "active",
  "initial_amount": "1000.00",
  "period_months": 6,
  "growth_rate": "20.00",
  "total_return": "1985.98",
  "final_amount": "2985.98",
  "monthly_growth": [
    {
      "month": 1,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 200.0,
      "ending_amount": 1200.0
    },
    {
      "month": 2,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 240.0,
      "ending_amount": 1440.0
    },
    {
      "month": 3,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 288.0,
      "ending_amount": 1728.0
    },
    {
      "month": 4,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 345.6,
      "ending_amount": 2073.6
    },
    {
      "month": 5,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 414.72,
      "ending_amount": 2488.32
    },
    {
      "month": 6,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 497.664,
      "ending_amount": 2985.984
    }
  ],
  "created_at": "2026-02-12T10:30:00Z",
  "start_date": "2026-02-12T10:30:00Z",
  "end_date": "2026-08-12T10:30:00Z",
  "completed_at": null,
  "updated_at": "2026-02-12T10:30:00Z"
}
```

---

### 2. List All Investment Plans
**GET** `/api/investments/investment-plans/`

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "plan_type": "basic",
      "status": "active",
      "initial_amount": "1000.00",
      "period_months": 6,
      "growth_rate": "20.00",
      "total_return": "1985.98",
      "final_amount": "2985.98",
      "monthly_growth": [...],
      "created_at": "2026-02-12T10:30:00Z",
      "start_date": "2026-02-12T10:30:00Z",
      "end_date": "2026-08-12T10:30:00Z",
      "completed_at": null,
      "updated_at": "2026-02-12T10:30:00Z"
    },
    ...
  ]
}
```

---

### 3. Get Investment Plan Details
**GET** `/api/investments/investment-plans/{id}/`

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_type": "basic",
  "status": "active",
  "initial_amount": "1000.00",
  "period_months": 6,
  "growth_rate": "20.00",
  "total_return": "1985.98",
  "final_amount": "2985.98",
  "monthly_breakdown": [
    {
      "month": 1,
      "starting_amount": 1000,
      "growth_rate": 20,
      "monthly_gain": 200.0,
      "ending_amount": 1200.0
    },
    ...
  ],
  "created_at": "2026-02-12T10:30:00Z",
  "start_date": "2026-02-12T10:30:00Z",
  "end_date": "2026-08-12T10:30:00Z",
  "completed_at": null
}
```

---

### 4. Get Active Plans
**GET** `/api/investments/investment-plans/active_plans/`

**Response (200 OK):**
```json
{
  "count": 2,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "plan_type": "basic",
      "status": "active",
      ...
    },
    ...
  ]
}
```

---

### 5. Get Completed Plans
**GET** `/api/investments/investment-plans/completed_plans/`

**Response (200 OK):**
```json
{
  "count": 1,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "plan_type": "standard",
      "status": "completed",
      ...
    }
  ]
}
```

---

### 6. Get Summary
**GET** `/api/investments/investment-plans/summary/`

**Response (200 OK):**
```json
{
  "total_invested": "5000.00",
  "total_returns": "8500.00",
  "total_final_amount": "13500.00",
  "active_plans_count": 2,
  "completed_plans_count": 1,
  "cancelled_plans_count": 0,
  "average_growth_rate": "36.67"
}
```

---

### 7. Complete Investment Plan
**POST** `/api/investments/investment-plans/{id}/complete/`

**Request:** (empty body)

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_type": "basic",
  "status": "completed",
  "initial_amount": "1000.00",
  "period_months": 6,
  "growth_rate": "20.00",
  "total_return": "1985.98",
  "final_amount": "2985.98",
  "monthly_growth": [...],
  "created_at": "2026-02-12T10:30:00Z",
  "start_date": "2026-02-12T10:30:00Z",
  "end_date": "2026-08-12T10:30:00Z",
  "completed_at": "2026-02-12T11:00:00Z",
  "updated_at": "2026-02-12T11:00:00Z"
}
```

---

### 8. Cancel Investment Plan
**POST** `/api/investments/investment-plans/{id}/cancel/`

**Request:** (empty body)

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_type": "basic",
  "status": "cancelled",
  "initial_amount": "1000.00",
  "period_months": 6,
  "growth_rate": "20.00",
  "total_return": "1985.98",
  "final_amount": "2985.98",
  "monthly_growth": [...],
  "created_at": "2026-02-12T10:30:00Z",
  "start_date": "2026-02-12T10:30:00Z",
  "end_date": "2026-08-12T10:30:00Z",
  "completed_at": null,
  "updated_at": "2026-02-12T11:00:00Z"
}
```

---

## 🧪 cURL Examples

### Create Basic Plan
```bash
curl -X POST http://localhost:8000/api/investments/investment-plans/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "basic",
    "initial_amount": 1000,
    "period_months": 6,
    "growth_rate": 20
  }'
```

### Create Advance Plan with 50% Rate
```bash
curl -X POST http://localhost:8000/api/investments/investment-plans/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "advance",
    "initial_amount": 5000,
    "period_months": 12,
    "growth_rate": 50
  }'
```

### List All Plans
```bash
curl -X GET http://localhost:8000/api/investments/investment-plans/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Plan Details
```bash
curl -X GET http://localhost:8000/api/investments/investment-plans/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Active Plans
```bash
curl -X GET http://localhost:8000/api/investments/investment-plans/active_plans/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Summary
```bash
curl -X GET http://localhost:8000/api/investments/investment-plans/summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Complete a Plan
```bash
curl -X POST http://localhost:8000/api/investments/investment-plans/550e8400-e29b-41d4-a716-446655440000/complete/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cancel a Plan
```bash
curl -X POST http://localhost:8000/api/investments/investment-plans/550e8400-e29b-41d4-a716-446655440000/cancel/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Validation Rules

### plan_type
- Required
- Must be: `basic`, `standard`, or `advance`

### initial_amount
- Required
- Must be > 0
- Decimal with max 12 digits, 2 decimal places

### period_months
- Required
- Must be between 1 and 60 (inclusive)
- Integer

### growth_rate
- Optional (auto-set based on plan_type if not provided)
- For `basic`: 20
- For `standard`: 30
- For `advance`: 40, 50, or 60
- Decimal with max 5 digits, 2 decimal places

---

## 📊 Status Values

- `active` - Plan is currently active
- `completed` - Plan has been completed
- `cancelled` - Plan has been cancelled

---

## 🔄 Monthly Growth Calculation

The `monthly_growth` array contains the breakdown for each month:

```json
{
  "month": 1,
  "starting_amount": 1000,
  "growth_rate": 20,
  "monthly_gain": 200.0,
  "ending_amount": 1200.0
}
```

- **month**: Month number (1 to period_months)
- **starting_amount**: Amount at start of month
- **growth_rate**: Growth rate percentage
- **monthly_gain**: Amount gained this month
- **ending_amount**: Amount at end of month (= starting_amount + monthly_gain)

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "plan_type": ["Invalid choice. Valid choices are: basic, standard, advance"],
  "period_months": ["Ensure this value is less than or equal to 60."],
  "growth_rate": ["Advance plan growth rate must be 40%, 50%, or 60%"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## 📝 Notes

1. All monetary values are returned as strings with 2 decimal places
2. Dates are in ISO 8601 format (UTC)
3. Monthly breakdown is calculated and stored when plan is created
4. End date is automatically calculated by adding months to start_date
5. All operations are scoped to the authenticated user
