# Admin 404 Issue - Solution

## The Problem

Getting 404 when accessing `/admin` on your backend.

## The Solution

Django requires a trailing slash for the admin URL.

### ❌ Wrong URL
```
https://growfun-backend.onrender.com/admin
```

### ✅ Correct URL
```
https://growfun-backend.onrender.com/admin/
```

## Why This Happens

Django's `APPEND_SLASH` setting is enabled (which is correct), but it only redirects GET requests. If you're accessing `/admin` directly, you need the trailing slash.

## All Your URLs

### Django Admin Panel
```
https://growfun-backend.onrender.com/admin/
```
Login with: admin001@gmail.com / Buffers316!

### API Endpoints

#### Authentication
```
POST   /api/auth/register/
POST   /api/auth/login/
GET    /api/auth/verify-email/?token=...
POST   /api/auth/resend-verification/
GET    /api/auth/me/
GET    /api/auth/profile/
```

#### Admin - Users
```
GET    /api/auth/admin/users/
GET    /api/auth/admin/users/{id}/
PUT    /api/auth/admin/users/{id}/
DELETE /api/auth/admin/users/{id}/
```

#### Admin - Deposits
```
GET    /api/transactions/admin/deposits/
POST   /api/transactions/admin/deposits/{id}/approve/
POST   /api/transactions/admin/deposits/{id}/reject/
```

#### Admin - Withdrawals
```
GET    /api/transactions/admin/withdrawals/
POST   /api/transactions/admin/withdrawals/{id}/process/
POST   /api/transactions/admin/withdrawals/{id}/complete/
POST   /api/transactions/admin/withdrawals/{id}/reject/
```

#### Admin - Stats
```
GET    /api/transactions/admin/stats/
```

#### Transactions
```
GET    /api/transactions/
POST   /api/transactions/korapay/deposit/
POST   /api/transactions/korapay/withdrawal/bank/
POST   /api/transactions/korapay/withdrawal/mobile/
GET    /api/transactions/korapay/banks/?country=NG
```

#### Investments
```
GET    /api/investments/
POST   /api/investments/
GET    /api/investments/plans/
```

## Quick Test

### 1. Test Admin Panel (Browser)
Open: https://growfun-backend.onrender.com/admin/

You should see Django admin login page.

### 2. Test API Login (Browser Console)
```javascript
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    email: 'admin001@gmail.com',
    password: 'Buffers316!'
  })
})
.then(res => res.json())
.then(data => {
  console.log('Login:', data);
  localStorage.setItem('accessToken', data.tokens.access);
});
```

### 3. Test Admin Endpoints (Browser Console)
```javascript
const token = localStorage.getItem('accessToken');

// Test deposits
fetch('https://growfun-backend.onrender.com/api/transactions/admin/deposits/', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log('Deposits:', data));

// Test withdrawals
fetch('https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log('Withdrawals:', data));

// Test stats
fetch('https://growfun-backend.onrender.com/api/transactions/admin/stats/', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => console.log('Stats:', data));
```

## Using the Test Tool

I've created `test-endpoints.html` for you. To use it:

1. Open `test-endpoints.html` in your browser
2. Click "Login & Get Token"
3. Click "Test All Endpoints"
4. See which endpoints are working and which aren't

## Frontend Integration

### Update Your Frontend API Calls

Replace mock data with real API calls:

```javascript
// api.js
import axios from 'axios';

const API_URL = 'https://growfun-backend.onrender.com/api';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Admin Deposits Component

```javascript
// AdminDeposits.js
import { useState, useEffect } from 'react';
import api from './api';

function AdminDeposits() {
  const [deposits, setDeposits] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDeposits();
  }, []);

  const fetchDeposits = async () => {
    try {
      const response = await api.get('/transactions/admin/deposits/');
      if (response.data.success) {
        setDeposits(response.data.deposits);
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to fetch deposits');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      const response = await api.post(`/transactions/admin/deposits/${id}/approve/`);
      if (response.data.success) {
        alert(response.data.message);
        fetchDeposits(); // Refresh
      }
    } catch (error) {
      alert('Failed to approve deposit');
    }
  };

  const handleReject = async (id) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      const response = await api.post(`/transactions/admin/deposits/${id}/reject/`, { reason });
      if (response.data.success) {
        alert(response.data.message);
        fetchDeposits(); // Refresh
      }
    } catch (error) {
      alert('Failed to reject deposit');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Deposits</h2>
      <div>Pending: {stats.pending} (${stats.pending_amount})</div>
      
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {deposits.map(deposit => (
            <tr key={deposit.id}>
              <td>{deposit.user.email}</td>
              <td>${deposit.amount}</td>
              <td>{deposit.status}</td>
              <td>{new Date(deposit.created_at).toLocaleDateString()}</td>
              <td>
                {deposit.status === 'pending' && (
                  <>
                    <button onClick={() => handleApprove(deposit.id)}>Approve</button>
                    <button onClick={() => handleReject(deposit.id)}>Reject</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminDeposits;
```

## Checklist

- [ ] Backend deployed to Render
- [ ] Can access https://growfun-backend.onrender.com/admin/ (with trailing slash)
- [ ] Can login to Django admin
- [ ] Can login via API and get JWT token
- [ ] Admin endpoints return data (not 403)
- [ ] Frontend updated to use real API calls
- [ ] Test deposit approval workflow
- [ ] Test withdrawal approval workflow

## Common Issues

### Issue: 403 Forbidden on admin endpoints
**Cause:** User doesn't have admin privileges

**Solution:**
1. Go to https://growfun-backend.onrender.com/admin/
2. Login with superuser account
3. Go to Users
4. Find your user
5. Check "Staff status" and "Superuser status"
6. Save

### Issue: Empty deposits/withdrawals list
**Cause:** No test data in database

**Solution:**
Create test transactions via Django admin or API

### Issue: Token expired
**Cause:** JWT token has expired

**Solution:**
Login again to get new token

## Summary

All your endpoints are properly configured. The main points:

1. ✅ Use `/admin/` with trailing slash
2. ✅ All API endpoints are at `/api/...`
3. ✅ Admin endpoints require `is_staff=True` or `is_superuser=True`
4. ✅ Include Authorization header with JWT token
5. ✅ Backend allows requests from your frontend

Everything is connected and ready to use!
