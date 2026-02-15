# Admin Approval System API Documentation

## Overview

Complete backend API for deposit and withdrawal approval system. All endpoints require admin authentication (is_staff or is_superuser).

## Authentication

All admin endpoints require:
```javascript
headers: {
  'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
  'Content-Type': 'application/json'
}
```

## Deposit Management

### 1. Get All Deposits

```
GET /api/transactions/admin/deposits/
```

**Query Parameters:**
- `status` (optional): Filter by status (pending, processing, completed, failed)
- `search` (optional): Search by email or reference

**Response:**
```json
{
  "success": true,
  "deposits": [
    {
      "id": 1,
      "user": {
        "id": 5,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "transaction_type": "deposit",
      "payment_method": "korapay",
      "amount": "1000.00",
      "fee": "0.00",
      "net_amount": "1000.00",
      "status": "pending",
      "reference": "DEP-ABC123XYZ",
      "phone_number": "+2348012345678",
      "description": "Korapay deposit of 1000",
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": null
    }
  ],
  "stats": {
    "total": 50,
    "pending": 10,
    "processing": 5,
    "completed": 30,
    "failed": 5,
    "total_amount": 50000.00,
    "pending_amount": 10000.00
  }
}
```

### 2. Approve Deposit

```
POST /api/transactions/admin/deposits/{transaction_id}/approve/
```

**Response:**
```json
{
  "success": true,
  "message": "Deposit of 1000.00 approved for user@example.com",
  "transaction": {
    "id": 1,
    "status": "completed",
    "completed_at": "2024-01-15T11:00:00Z",
    ...
  }
}
```

**What Happens:**
- Transaction status → `completed`
- User balance is credited with deposit amount
- `completed_at` timestamp is set

### 3. Reject Deposit

```
POST /api/transactions/admin/deposits/{transaction_id}/reject/
```

**Request Body:**
```json
{
  "reason": "Invalid payment proof"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deposit rejected for user@example.com",
  "transaction": {
    "id": 1,
    "status": "failed",
    "description": "Korapay deposit of 1000 - Rejected: Invalid payment proof",
    ...
  }
}
```

**What Happens:**
- Transaction status → `failed`
- Rejection reason added to description
- User balance is NOT credited

## Withdrawal Management

### 1. Get All Withdrawals

```
GET /api/transactions/admin/withdrawals/
```

**Query Parameters:**
- `status` (optional): Filter by status (pending, processing, completed, failed)
- `search` (optional): Search by email or reference

**Response:**
```json
{
  "success": true,
  "withdrawals": [
    {
      "id": 2,
      "user": {
        "id": 5,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "transaction_type": "withdrawal",
      "payment_method": "korapay",
      "amount": "500.00",
      "fee": "10.00",
      "net_amount": "490.00",
      "status": "pending",
      "reference": "WTH-XYZ789ABC",
      "phone_number": "+2348012345678",
      "description": "Bank withdrawal of 500",
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": null
    }
  ],
  "stats": {
    "total": 30,
    "pending": 8,
    "processing": 3,
    "completed": 15,
    "failed": 4,
    "total_amount": 15000.00,
    "pending_amount": 4000.00
  }
}
```

### 2. Process Withdrawal (Mark as In-Progress)

```
POST /api/transactions/admin/withdrawals/{transaction_id}/process/
```

**Response:**
```json
{
  "success": true,
  "message": "Withdrawal marked as processing for user@example.com",
  "transaction": {
    "id": 2,
    "status": "processing",
    ...
  }
}
```

**What Happens:**
- Transaction status: `pending` → `processing`
- Indicates admin is working on it

### 3. Complete Withdrawal

```
POST /api/transactions/admin/withdrawals/{transaction_id}/complete/
```

**Response:**
```json
{
  "success": true,
  "message": "Withdrawal of 500.00 completed for user@example.com",
  "transaction": {
    "id": 2,
    "status": "completed",
    "completed_at": "2024-01-15T11:30:00Z",
    ...
  }
}
```

**What Happens:**
- Transaction status → `completed`
- `completed_at` timestamp is set
- User balance already deducted (done during withdrawal request)

### 4. Reject Withdrawal

```
POST /api/transactions/admin/withdrawals/{transaction_id}/reject/
```

**Request Body:**
```json
{
  "reason": "Insufficient verification documents"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Withdrawal rejected and refunded for user@example.com",
  "transaction": {
    "id": 2,
    "status": "failed",
    "description": "Bank withdrawal of 500 - Rejected: Insufficient verification documents",
    ...
  }
}
```

**What Happens:**
- Transaction status → `failed`
- User balance is REFUNDED (amount added back)
- Rejection reason added to description

## Transaction Statistics

### Get Admin Dashboard Stats

```
GET /api/transactions/admin/stats/
```

**Response:**
```json
{
  "success": true,
  "deposits": {
    "total_count": 50,
    "pending_count": 10,
    "completed_count": 35,
    "total_amount": 50000.00,
    "pending_amount": 10000.00,
    "completed_amount": 35000.00
  },
  "withdrawals": {
    "total_count": 30,
    "pending_count": 8,
    "processing_count": 3,
    "completed_count": 15,
    "total_amount": 15000.00,
    "pending_amount": 4000.00,
    "completed_amount": 7500.00
  },
  "recent_transactions": [
    {
      "id": 10,
      "user": {...},
      "transaction_type": "deposit",
      "amount": "1000.00",
      "status": "pending",
      "created_at": "2024-01-15T12:00:00Z"
    },
    ...
  ]
}
```

## Frontend Integration

### Replace Mock Data with Real API

#### Deposits Component

```javascript
// AdminDeposits.js
import { useState, useEffect } from 'react';
import api from './api';

function AdminDeposits() {
  const [deposits, setDeposits] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchDeposits();
  }, [filter]);

  const fetchDeposits = async () => {
    try {
      const params = filter !== 'all' ? `?status=${filter}` : '';
      const response = await api.get(`/transactions/admin/deposits/${params}`);
      
      if (response.data.success) {
        setDeposits(response.data.deposits);
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error fetching deposits:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (transactionId) => {
    try {
      const response = await api.post(
        `/transactions/admin/deposits/${transactionId}/approve/`
      );
      
      if (response.data.success) {
        alert(response.data.message);
        fetchDeposits(); // Refresh list
      }
    } catch (error) {
      alert('Failed to approve deposit');
    }
  };

  const handleReject = async (transactionId) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      const response = await api.post(
        `/transactions/admin/deposits/${transactionId}/reject/`,
        { reason }
      );
      
      if (response.data.success) {
        alert(response.data.message);
        fetchDeposits(); // Refresh list
      }
    } catch (error) {
      alert('Failed to reject deposit');
    }
  };

  return (
    <div>
      <h2>Deposit Approvals</h2>
      
      {/* Stats */}
      <div className="stats">
        <div>Total: {stats.total}</div>
        <div>Pending: {stats.pending}</div>
        <div>Pending Amount: ${stats.pending_amount}</div>
      </div>

      {/* Filter */}
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="pending">Pending</option>
        <option value="completed">Completed</option>
        <option value="failed">Failed</option>
      </select>

      {/* Deposits List */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {deposits.map(deposit => (
              <tr key={deposit.id}>
                <td>{deposit.reference}</td>
                <td>{deposit.user.email}</td>
                <td>${deposit.amount}</td>
                <td>{deposit.payment_method}</td>
                <td>{deposit.status}</td>
                <td>{new Date(deposit.created_at).toLocaleDateString()}</td>
                <td>
                  {deposit.status === 'pending' && (
                    <>
                      <button onClick={() => handleApprove(deposit.id)}>
                        Approve
                      </button>
                      <button onClick={() => handleReject(deposit.id)}>
                        Reject
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AdminDeposits;
```

#### Withdrawals Component

```javascript
// AdminWithdrawals.js
import { useState, useEffect } from 'react';
import api from './api';

function AdminWithdrawals() {
  const [withdrawals, setWithdrawals] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchWithdrawals();
  }, [filter]);

  const fetchWithdrawals = async () => {
    try {
      const params = filter !== 'all' ? `?status=${filter}` : '';
      const response = await api.get(`/transactions/admin/withdrawals/${params}`);
      
      if (response.data.success) {
        setWithdrawals(response.data.withdrawals);
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error fetching withdrawals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async (transactionId) => {
    try {
      const response = await api.post(
        `/transactions/admin/withdrawals/${transactionId}/process/`
      );
      
      if (response.data.success) {
        alert(response.data.message);
        fetchWithdrawals();
      }
    } catch (error) {
      alert('Failed to process withdrawal');
    }
  };

  const handleComplete = async (transactionId) => {
    try {
      const response = await api.post(
        `/transactions/admin/withdrawals/${transactionId}/complete/`
      );
      
      if (response.data.success) {
        alert(response.data.message);
        fetchWithdrawals();
      }
    } catch (error) {
      alert('Failed to complete withdrawal');
    }
  };

  const handleReject = async (transactionId) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      const response = await api.post(
        `/transactions/admin/withdrawals/${transactionId}/reject/`,
        { reason }
      );
      
      if (response.data.success) {
        alert(response.data.message);
        fetchWithdrawals();
      }
    } catch (error) {
      alert('Failed to reject withdrawal');
    }
  };

  return (
    <div>
      <h2>Withdrawal Approvals</h2>
      
      {/* Stats */}
      <div className="stats">
        <div>Total: {stats.total}</div>
        <div>Pending: {stats.pending}</div>
        <div>Processing: {stats.processing}</div>
        <div>Pending Amount: ${stats.pending_amount}</div>
      </div>

      {/* Filter */}
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="pending">Pending</option>
        <option value="processing">Processing</option>
        <option value="completed">Completed</option>
        <option value="failed">Failed</option>
      </select>

      {/* Withdrawals List */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Amount</th>
              <th>Fee</th>
              <th>Net Amount</th>
              <th>Method</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {withdrawals.map(withdrawal => (
              <tr key={withdrawal.id}>
                <td>{withdrawal.reference}</td>
                <td>{withdrawal.user.email}</td>
                <td>${withdrawal.amount}</td>
                <td>${withdrawal.fee}</td>
                <td>${withdrawal.net_amount}</td>
                <td>{withdrawal.payment_method}</td>
                <td>{withdrawal.status}</td>
                <td>{new Date(withdrawal.created_at).toLocaleDateString()}</td>
                <td>
                  {withdrawal.status === 'pending' && (
                    <>
                      <button onClick={() => handleProcess(withdrawal.id)}>
                        Process
                      </button>
                      <button onClick={() => handleReject(withdrawal.id)}>
                        Reject
                      </button>
                    </>
                  )}
                  {withdrawal.status === 'processing' && (
                    <button onClick={() => handleComplete(withdrawal.id)}>
                      Complete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AdminWithdrawals;
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Admin access required"
}
```

```json
{
  "success": false,
  "message": "Deposit already approved"
}
```

```json
{
  "success": false,
  "error": "Deposit not found"
}
```

## Security Features

1. ✅ Admin role verification on every request
2. ✅ JWT token authentication required
3. ✅ User balance automatically updated
4. ✅ Transaction status validation
5. ✅ Audit trail (timestamps, descriptions)
6. ✅ Refund on rejection (withdrawals)

## Testing

### Test with cURL

```bash
# Get deposits
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://growfun-backend.onrender.com/api/transactions/admin/deposits/

# Approve deposit
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  https://growfun-backend.onrender.com/api/transactions/admin/deposits/1/approve/

# Reject withdrawal
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Invalid account"}' \
  https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/2/reject/
```

## Deployment

1. Deploy updated backend to Render
2. Update frontend API calls (remove mock data)
3. Test with admin account
4. Monitor logs for errors

## Support

If you encounter issues:
- Check admin user has `is_staff=True` or `is_superuser=True`
- Verify JWT token is valid
- Check transaction exists and has correct type
- Review backend logs on Render
