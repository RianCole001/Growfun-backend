# Referral System Debug Guide

## Issue: "Failed to load referral data"

This guide helps diagnose why the Earn component is failing to load referral data.

---

## Step 1: Verify Backend is Running

```bash
# Check if Django server is running on port 8000
curl http://localhost:8000/api/auth/referral-stats/
```

Expected: Should return 401 Unauthorized (because no auth token)

---

## Step 2: Test API Endpoints Directly

### Get Authentication Token

1. Register a test user or login with existing credentials
2. Copy the access token from browser localStorage:
   - Open DevTools (F12)
   - Go to Application → Local Storage
   - Find `user_access_token`
   - Copy the token value

### Test Referral Stats Endpoint

```bash
# Replace TOKEN with actual access token
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/auth/referral-stats/
```

Expected response:
```json
{
  "referral_code": "ABC12345",
  "referral_link": "http://localhost:3000/register?ref=ABC12345",
  "total_referrals": 0,
  "active_referrals": 0,
  "pending_referrals": 0,
  "total_earned": 0,
  "pending_earnings": 0,
  "this_month_earnings": 0
}
```

### Test Referrals List Endpoint

```bash
# Replace TOKEN with actual access token
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/auth/referrals/
```

Expected response:
```json
{
  "referrals": []
}
```

---

## Step 3: Check Browser Console

1. Open DevTools (F12)
2. Go to Console tab
3. Look for error messages when Earn component loads
4. Check Network tab to see API requests:
   - Look for `/api/auth/referral-stats/` request
   - Look for `/api/auth/referrals/` request
   - Check response status (should be 200)
   - Check response body for errors

---

## Step 4: Verify Database Migration

```bash
cd backend-growfund

# Check if migration was applied
py manage.py showmigrations accounts

# Should show:
# [X] 0001_initial
# [X] 0002_referral

# If 0002_referral is not marked with [X], run:
py manage.py migrate accounts
```

---

## Step 5: Check User Has Referral Code

```bash
cd backend-growfund
py manage.py shell

# In Django shell:
from accounts.models import User

# Get current user
user = User.objects.get(email='your-email@example.com')

# Check referral code
print(user.referral_code)  # Should print something like "ABC12345"

# If empty, regenerate:
user.referral_code = None
user.save()
print(user.referral_code)  # Should now have a code
```

---

## Step 6: Check Authentication Token

1. Open DevTools (F12)
2. Go to Application → Local Storage
3. Verify `user_access_token` exists and is not empty
4. If missing, login again

---

## Step 7: Check API Service Configuration

File: `Growfund-Dashboard/trading-dashboard/src/services/api.js`

Verify these endpoints are correct:
```javascript
getReferrals: () => userApi.get('/auth/referrals/'),
getReferralStats: () => userApi.get('/auth/referral-stats/'),
```

Should be calling:
- `GET /api/auth/referrals/`
- `GET /api/auth/referral-stats/`

---

## Step 8: Enable Debug Logging

### Backend Debug

Add this to `backend-growfund/accounts/views.py` in `ReferralStatsView.get()`:

```python
def get(self, request):
    print(f"DEBUG: User: {request.user}")
    print(f"DEBUG: User referral_code: {request.user.referral_code}")
    
    user = request.user
    referrals = Referral.objects.filter(referrer=user)
    print(f"DEBUG: Referrals count: {referrals.count()}")
    
    # ... rest of code
```

Then check Django console output for debug messages.

### Frontend Debug

Add this to `Growfund-Dashboard/trading-dashboard/src/components/Earn.js`:

```javascript
const fetchReferralData = async () => {
  try {
    console.log('DEBUG: Starting to fetch referral data');
    
    const statsResponse = await userAuthAPI.getReferralStats();
    console.log('DEBUG: Stats response:', statsResponse);
    
    const referralsResponse = await userAuthAPI.getReferrals();
    console.log('DEBUG: Referrals response:', referralsResponse);
    
    // ... rest of code
  } catch (error) {
    console.error('DEBUG: Error details:', error.response?.data || error.message);
  }
};
```

Then check browser console for debug messages.

---

## Common Issues & Solutions

### Issue 1: 401 Unauthorized
**Cause**: User not authenticated or token expired
**Solution**: 
- Login again
- Check if `user_access_token` exists in localStorage
- Verify token is being sent in Authorization header

### Issue 2: 404 Not Found
**Cause**: Endpoint URL is wrong
**Solution**:
- Verify URLs in `api.js` match backend URLs
- Check Django URL configuration in `accounts/urls.py`
- Verify accounts app is included in main `urls.py` at `api/auth/`

### Issue 3: Empty Response
**Cause**: User has no referral code or referrals
**Solution**:
- Check if user has referral_code in database
- Create test referrals by registering with referral code
- Verify Referral records exist in database

### Issue 4: CORS Error
**Cause**: Frontend and backend on different origins
**Solution**:
- Verify CORS is configured in Django settings
- Check if `http://localhost:3000` is in CORS_ALLOWED_ORIGINS
- Restart Django server after changing settings

### Issue 5: TypeError: Cannot read property 'referrals'
**Cause**: API response format is different than expected
**Solution**:
- Check actual API response format
- Verify response has `referrals` key
- Add null checks in component

---

## Database Queries

### Check Referral Records

```bash
cd backend-growfund
py manage.py shell

from accounts.models import Referral, User

# View all referrals
Referral.objects.all()

# View referrals for specific user
user = User.objects.get(email='user@example.com')
user.referrals_made.all()

# Check referral details
referral = Referral.objects.first()
print(f"Referrer: {referral.referrer.email}")
print(f"Referred User: {referral.referred_user.email}")
print(f"Reward Amount: {referral.reward_amount}")
print(f"Reward Claimed: {referral.reward_claimed}")
print(f"Status: {referral.status}")
```

---

## Network Request Inspection

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by XHR/Fetch
4. Look for requests to:
   - `/api/auth/referral-stats/`
   - `/api/auth/referrals/`
5. Click on each request to see:
   - Request Headers (should have Authorization)
   - Response Status (should be 200)
   - Response Body (should have data)

---

## Quick Checklist

- [ ] Django server running on port 8000
- [ ] React app running on port 3000
- [ ] Database migration applied (`py manage.py migrate accounts`)
- [ ] User is logged in
- [ ] `user_access_token` exists in localStorage
- [ ] User has referral_code in database
- [ ] API endpoints return 200 status
- [ ] API response has correct format
- [ ] No CORS errors in console
- [ ] No 401 Unauthorized errors

---

## Still Having Issues?

1. Check Django console for error messages
2. Check browser console for error messages
3. Verify all files were saved correctly
4. Restart both Django and React servers
5. Clear browser cache and localStorage
6. Check database for Referral records
7. Verify user authentication is working
