# Admin Dashboard Stats Not Updating - Debug Guide

## Problem
Admin dashboard shows "Total Users: 2" instead of "Total Users: 7"

## Root Cause
The API response might not be parsed correctly, or the data isn't being fetched on page load.

## How to Debug

### Step 1: Check Browser Console
1. Go to `http://localhost:3000/admin`
2. Login as admin
3. Open DevTools (F12)
4. Go to Console tab
5. Look for logs like:
   - `API Response: {...}`
   - `Formatted users count: 7`
   - `Final formatted users: 7`

### Step 2: Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Refresh the page
4. Look for request to `http://localhost:8000/api/auth/admin/users/`
5. Click on it and check Response tab
6. Should show array of users

**Expected Response:**
```json
{
  "data": [
    {
      "id": 1,
      "email": "user1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_verified": true,
      ...
    },
    ...
  ],
  "count": 7
}
```

### Step 3: Manual API Test
Open browser console and run:
```javascript
const token = localStorage.getItem('admin_access_token');
fetch('http://localhost:8000/api/auth/admin/users/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => {
  console.log('Users count:', data.data ? data.data.length : data.length);
  console.log('Full response:', data);
})
.catch(e => console.error('Error:', e));
```

## Solutions

### Solution 1: Click Refresh Button
1. Go to User Management page
2. Click "↻ Refresh" button
3. Stats should update to show 7 users

### Solution 2: Clear Cache and Reload
1. Press `Ctrl+Shift+Delete`
2. Clear all data
3. Refresh page (F5)
4. Login again
5. Stats should update

### Solution 3: Check Backend Response
If API returns wrong data, check backend:

```bash
cd backend-growfund
py manage.py shell
```

Then:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"Total users: {User.objects.count()}")
print(f"Admin users: {User.objects.filter(is_staff=True).count()}")

# List all users
for user in User.objects.all():
    print(f"  {user.email} - verified: {user.is_verified}")
```

Exit:
```python
exit()
```

### Solution 4: Restart Servers
```bash
# Stop Django (Ctrl+C)
# Restart Django
cd backend-growfund
py manage.py runserver

# In another terminal, restart frontend
cd Growfund-Dashboard/trading-dashboard
npm start
```

## What Changed

Added debugging logs to AdminUsers component:
- Logs API response
- Logs formatted users count
- Logs final users count
- Shows info toast if no users found

These logs help identify where the issue is:
- If "API Response" shows 7 users but "Final formatted users" shows 2, there's a parsing issue
- If "API Response" shows 2 users, the backend is returning wrong data
- If no logs appear, the API call isn't being made

## Verification Steps

1. **Check Console Logs**
   - Open DevTools (F12)
   - Go to Console
   - Should see logs with user counts

2. **Check Network Request**
   - Open DevTools (F12)
   - Go to Network tab
   - Refresh page
   - Look for `/api/auth/admin/users/` request
   - Response should show 7 users

3. **Click Refresh Button**
   - Should update stats to 7

4. **Check Backend**
   - Run `py manage.py shell`
   - Check `User.objects.count()` returns 7+

## Expected Behavior

After fix:
- ✅ Admin dashboard loads
- ✅ Console shows "Formatted users count: 7"
- ✅ Stats show "Total Users: 7"
- ✅ Table shows all 7 users
- ✅ Refresh button works
- ✅ Search and filter work

## Still Not Working?

1. Check if admin is actually logged in
2. Check if `admin_access_token` exists in localStorage
3. Check if API endpoint returns data (test in console)
4. Check Django logs for errors
5. Verify 7 users exist in database
6. Try clearing all browser data and logging in again
