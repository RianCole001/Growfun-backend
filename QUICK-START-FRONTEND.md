# Quick Start - Frontend Implementation

## What You Need to Build

### 1. Admin Balance Credit Form
Shows a form where admin can:
- Enter user ID
- Enter amount to credit
- Add optional note
- Submit to credit the account

### 2. Balance Display Widget
Shows:
- Current user balance
- Refresh button
- Updates when balance changes

### 3. Transaction History Table
Shows:
- All transactions including admin credits
- Filter by type (All, Admin Credits, Deposits, Withdrawals)
- Columns: Type, Amount, Status, Date, Description

### 4. Admin Dashboard Page
Combines:
- User ID input
- Balance credit form
- Current balance display
- Transaction history

### 5. User Dashboard Page
Shows:
- Current balance
- Transaction history

---

## API Endpoints to Call

### Credit User (Admin Only)
```
POST /api/accounts/admin/users/{userId}/balance/
Headers: Authorization: Bearer {token}
Body: {
  "action": "credit",
  "amount": 100.00,
  "note": "Bonus"
}
```

### Get Balance
```
GET /api/accounts/profile/
Headers: Authorization: Bearer {token}
Response: { data: { balance: 500.00 } }
```

### Get Transactions
```
GET /api/transactions/
Headers: Authorization: Bearer {token}
Response: { results: [ { transaction_type, amount, status, created_at, description } ] }
```

### Get Transaction Summary
```
GET /api/transactions/summary/
Headers: Authorization: Bearer {token}
Response: { data: { total_deposits, current_balance, recent_transactions } }
```

---

## Key Features

✅ **Admin can credit users** - Balance updates immediately
✅ **Transaction recorded** - Shows in user's transaction history
✅ **Live balance display** - Shows current balance
✅ **Transaction filtering** - Filter by type
✅ **Edit in admin panel** - Can edit amount and description
✅ **Bulk credit** - Credit multiple users at once

---

## Testing Workflow

1. **Admin logs in** → Goes to Admin Dashboard
2. **Enters user ID** → Selects which user to credit
3. **Enters amount** → e.g., $100
4. **Adds note** → e.g., "Promotional bonus"
5. **Clicks Credit** → Balance updates
6. **User sees transaction** → In their transaction history
7. **Admin can edit** → In Django admin panel

---

## Response Examples

### Credit Success
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "new_balance": 500.00,
    "transaction": {
      "id": 123,
      "type": "admin_credit",
      "amount": 100.00,
      "status": "completed"
    }
  }
}
```

### Transaction History
```json
{
  "results": [
    {
      "id": 123,
      "transaction_type": "admin_credit",
      "amount": "100.00",
      "status": "completed",
      "description": "Promotional bonus",
      "created_at": "2026-04-26T10:30:00Z"
    }
  ]
}
```

---

## Component Structure

```
AdminDashboard
├── UserSelector (input for user ID)
├── AdminBalanceCredit
│   ├── AmountInput
│   ├── NoteInput
│   └── SubmitButton
├── BalanceDisplay
│   ├── BalanceAmount
│   └── RefreshButton
└── TransactionHistory
    ├── FilterButtons
    └── TransactionTable

UserDashboard
├── BalanceDisplay
└── TransactionHistory
```

---

## State Management

```javascript
// Admin Dashboard State
const [selectedUserId, setSelectedUserId] = useState('');
const [refreshTrigger, setRefreshTrigger] = useState(0);

// Balance Display State
const [balance, setBalance] = useState(0);
const [loading, setLoading] = useState(true);

// Transaction History State
const [transactions, setTransactions] = useState([]);
const [filter, setFilter] = useState('all');

// Form State
const [amount, setAmount] = useState('');
const [note, setNote] = useState('');
const [submitting, setSubmitting] = useState(false);
```

---

## Error Handling

Handle these errors:
- "Admin access required" (403) - User not admin
- "User not found" (404) - Invalid user ID
- "Amount must be greater than 0" (400) - Invalid amount
- "Insufficient balance" (400) - Can't debit more than balance
- Network errors - Show retry button

---

## Real-Time Updates (Optional)

For live updates without refresh:
1. Poll balance every 5 seconds
2. Or use WebSocket for real-time updates
3. Or use React Query for automatic refetching

---

## Testing Checklist

- [ ] Admin can credit user
- [ ] Balance updates immediately
- [ ] Transaction appears in history
- [ ] Can filter transactions
- [ ] Error messages show correctly
- [ ] Loading states work
- [ ] Refresh button works
- [ ] Form validation works
- [ ] Success messages show
- [ ] Can edit transaction in admin panel

---

## Files to Create

1. `src/components/AdminBalanceCredit.jsx` - Credit form
2. `src/components/BalanceDisplay.jsx` - Balance widget
3. `src/components/TransactionHistory.jsx` - Transaction table
4. `src/pages/AdminDashboard.jsx` - Admin page
5. `src/pages/UserDashboard.jsx` - User page
6. `src/styles/balance-management.css` - Styling
7. `src/api/balanceApi.js` - API calls
8. `src/hooks/useBalance.js` - Custom hook (optional)

---

## Backend Status

✅ All endpoints working
✅ Admin credit functional
✅ Transaction recording working
✅ Balance updates working
✅ Transaction history includes admin credits
✅ Admin panel editing working
✅ Database migrations applied

Ready for frontend integration!
