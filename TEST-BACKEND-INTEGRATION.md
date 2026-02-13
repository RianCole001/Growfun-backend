# GrowFund Platform - Backend Integration Testing

## ✅ Integration Ready for Testing

Both servers are running and connected. Test the integration with these steps.

---

## 🚀 Quick Test (5 minutes)

### Step 1: Login with Backend
1. Open http://localhost:3000
2. Click "Go to Login Page"
3. Login with:
   - Email: `admin@growfund.com`
   - Password: `Admin123!`
4. **Expected**: Dashboard loads with real data from backend

### Step 2: Check Profile Data
1. Click "Profile" in sidebar
2. **Expected**: Profile shows real data from backend
   - Name: Admin (from first_name + last_name)
   - Email: admin@growfund.com
   - Phone, location, occupation, etc. (if set)

### Step 3: Check Balance
1. Look at "Account Balances" section
2. **Expected**: Shows balance from backend (should be 0.00 for new user)

### Step 4: Update Profile
1. Click "Edit" in Profile
2. Change phone number to: `+1234567890`
3. Click "Save Changes"
4. **Expected**: 
   - Toast notification: "Profile updated successfully"
   - Data saved to backend
   - Refresh page - data persists

### Step 5: Check Settings
1. Click "Settings" in sidebar
2. Go to "General" tab
3. **Expected**: Settings loaded from backend
   - Theme: dark
   - Currency: USD
   - Language: en
   - Timezone: UTC

### Step 6: Change Settings
1. Change currency to "EUR"
2. **Expected**: 
   - Toast notification: "Settings updated successfully"
   - Data saved to backend

### Step 7: Check Referral Code
1. Click "Earn" in sidebar
2. **Expected**: Referral code displays (from backend)
3. Copy referral link
4. **Expected**: Toast notification: "Referral link copied to clipboard"

---

## 🧪 Detailed Testing

### Test: Login Flow
```
1. Open http://localhost:3000
2. Click "Go to Login Page"
3. Enter credentials:
   Email: admin@growfund.com
   Password: Admin123!
4. Click "Login"

Expected:
✓ Success toast notification
✓ Redirected to dashboard
✓ Profile data loaded
✓ Balance displayed
✓ Tokens in localStorage
```

### Test: Profile Update
```
1. Login as admin
2. Click "Profile"
3. Click "Edit"
4. Change fields:
   - Phone: +1234567890
   - Location: New York
   - Occupation: Developer
5. Click "Save Changes"

Expected:
✓ Success toast notification
✓ Data saved to backend
✓ Refresh page - data persists
✓ No errors in console
```

### Test: Settings Update
```
1. Login as admin
2. Click "Settings"
3. Change settings:
   - Currency: EUR
   - Language: es
   - Timezone: Europe/London
4. Each change should save automatically

Expected:
✓ Success toast notification
✓ Data saved to backend
✓ Settings persist after refresh
✓ No errors in console
```

### Test: Password Change
```
1. Login as admin
2. Click "Settings"
3. Go to "Security" tab
4. Enter:
   - Current password: Admin123!
   - New password: NewPass456!
   - Confirm password: NewPass456!
5. Click "Update Password"

Expected:
✓ Success toast notification
✓ Password changed in backend
✓ Can login with new password
✓ Old password no longer works
```

### Test: Referral System
```
1. Login as admin
2. Click "Earn"
3. Check referral code displays
4. Copy referral link
5. Check referral stats

Expected:
✓ Referral code from backend
✓ Referral link copied to clipboard
✓ Stats displayed (0 referrals for new user)
✓ No errors in console
```

---

## 🔍 Verification Checklist

### Authentication
- [ ] Can login with backend credentials
- [ ] Tokens stored in localStorage
- [ ] Can access protected routes
- [ ] Logout clears tokens
- [ ] Can login again after logout

### Profile
- [ ] Profile data loads from backend
- [ ] Can edit profile
- [ ] Changes save to backend
- [ ] Data persists after refresh
- [ ] Toast notifications show

### Settings
- [ ] Settings load from backend
- [ ] Can change settings
- [ ] Changes save to backend
- [ ] Data persists after refresh
- [ ] Toast notifications show

### Password
- [ ] Can change password
- [ ] New password works
- [ ] Old password doesn't work
- [ ] Toast notifications show
- [ ] No errors in console

### Referral
- [ ] Referral code displays
- [ ] Can copy referral link
- [ ] Stats display correctly
- [ ] No errors in console

### Error Handling
- [ ] Invalid credentials show error
- [ ] Network errors handled
- [ ] Validation errors shown
- [ ] Loading states display
- [ ] Toast notifications work

---

## 📊 Browser Console Checks

### Check Tokens
```javascript
// In browser console:
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
localStorage.getItem('user')
```

### Check API Calls
1. Open DevTools (F12)
2. Go to Network tab
3. Perform action (login, update profile, etc.)
4. Check requests:
   - URL: http://localhost:8000/api/...
   - Method: POST, GET, PUT
   - Status: 200, 201, 400, 401
   - Headers: Authorization: Bearer {token}

### Check Errors
1. Open DevTools (F12)
2. Go to Console tab
3. Look for errors (red text)
4. Check error messages
5. Verify they're handled gracefully

---

## 🐛 Common Issues & Solutions

### Issue: "CORS error"
```
Error: Access to XMLHttpRequest blocked by CORS policy
```
**Solution:**
- Ensure Django running on port 8000
- Check CORS_ALLOWED_ORIGINS in settings.py
- Clear browser cache
- Restart both servers

### Issue: "Token is invalid or expired"
```
Error: Token is invalid or expired
```
**Solution:**
- Clear localStorage: `localStorage.clear()`
- Login again
- Check token expiration in settings.py

### Issue: "Failed to fetch user data"
```
Error: Failed to fetch user data
```
**Solution:**
- Check Django console for errors
- Verify token is valid
- Check API endpoint is correct
- Verify backend is running

### Issue: "Profile not updating"
```
Error: Failed to update profile
```
**Solution:**
- Check browser console for errors
- Verify token is in localStorage
- Check Django console for validation errors
- Verify all required fields are filled

### Issue: "Settings not saving"
```
Error: Failed to update settings
```
**Solution:**
- Check all required fields are filled
- Verify token is valid
- Check Django console for errors
- Clear browser cache

---

## 📈 Performance Testing

### Measure Response Times
1. Open DevTools (F12)
2. Go to Network tab
3. Perform action
4. Check response time in "Time" column

### Expected Times
- Login: 100-200ms
- Get user: 50-100ms
- Update profile: 100-150ms
- Get settings: 50-100ms
- Update settings: 100-150ms

### Optimization
- Tokens cached in localStorage
- Automatic token refresh
- Minimal API calls
- Efficient state management

---

## 🔐 Security Testing

### Test: Token Security
```
1. Login as admin
2. Open DevTools
3. Check localStorage for tokens
4. Verify tokens are JWT format
5. Logout
6. Verify tokens cleared
```

### Test: Password Security
```
1. Change password
2. Try old password - should fail
3. Try new password - should work
4. Verify password hashed in backend
```

### Test: CORS Protection
```
1. Try accessing API from different origin
2. Should get CORS error
3. Verify only localhost:3000 allowed
```

---

## 📝 Test Results Template

### Test Date: ___________
### Tester: ___________

#### Authentication
- [ ] Login works
- [ ] Tokens stored
- [ ] Protected routes work
- [ ] Logout works

#### Profile
- [ ] Data loads
- [ ] Can edit
- [ ] Changes save
- [ ] Data persists

#### Settings
- [ ] Data loads
- [ ] Can change
- [ ] Changes save
- [ ] Data persists

#### Password
- [ ] Can change
- [ ] New password works
- [ ] Old password fails

#### Referral
- [ ] Code displays
- [ ] Link copies
- [ ] Stats show

#### Errors
- [ ] Handled gracefully
- [ ] Toast notifications
- [ ] No console errors

#### Performance
- [ ] Response times acceptable
- [ ] No lag
- [ ] Smooth interactions

#### Overall
- [ ] All tests passed
- [ ] No critical issues
- [ ] Ready for production

---

## 🎯 Next Steps

### If All Tests Pass
1. ✅ Integration complete
2. ✅ Ready for Phase 2
3. ✅ Create investment APIs
4. ✅ Create transaction APIs

### If Issues Found
1. Check error messages
2. Review console logs
3. Check Django console
4. Verify configuration
5. Fix and retest

---

## 📞 Support

### For API Issues
- Check Django console
- Check browser Network tab
- Verify tokens in localStorage
- Check CORS configuration

### For Frontend Issues
- Check browser console
- Check React DevTools
- Verify API service configuration
- Check component props

### For Backend Issues
- Check Django logs
- Run `py manage.py check`
- Check database migrations
- Verify settings.py

---

## ✅ Integration Testing Complete!

All components are connected and ready for testing.

**Start testing now:**
1. Open http://localhost:3000
2. Login with admin@growfund.com / Admin123!
3. Follow the test scenarios above
4. Report any issues

