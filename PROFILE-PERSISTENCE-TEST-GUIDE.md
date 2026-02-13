# Profile Persistence - Testing Guide

## Quick Test (5 minutes)

### Step 1: Login
- Go to http://localhost:3000/login
- Email: silven@gmail.com (or any registered user)
- Password: (use the password you registered with)

### Step 2: Update Profile
- Click "Profile" in navigation
- Click "Edit" button
- Change name to "Test User"
- Change phone to "555-1234"
- Click "Save Changes"
- See green success toast

### Step 3: Logout
- Click "Log out" button
- Confirm logout

### Step 4: Login Again
- Login with same credentials
- Click "Profile"
- **VERIFY**: Name shows "Test User"
- **VERIFY**: Phone shows "555-1234"

✅ If both fields show updated values = **FIXED**
❌ If fields show old values = **ISSUE**

---

## Detailed Test (15 minutes)

### Test 1: All Fields Persist

**Setup**
1. Login to dashboard
2. Click Profile
3. Click Edit

**Update All Fields**
- Name: "Jane Smith"
- Email: (keep same)
- Phone: "555-9999"
- Location: "New York"
- Occupation: "Manager"
- Company: "Tech Corp"
- Website: "https://example.com"
- Bio: "Test bio"

**Save & Verify**
1. Click "Save Changes"
2. See success toast
3. Refresh page (Ctrl+R)
4. Click Profile
5. Verify all fields still show updated values

**Logout & Login**
1. Click Logout
2. Login again
3. Click Profile
4. **VERIFY ALL FIELDS PERSISTED**

### Test 2: Avatar Persists

**Setup**
1. Login to dashboard
2. Click Profile
3. Click Edit

**Upload Avatar**
1. Click file input under avatar
2. Select an image file
3. See preview in circle
4. Click "Save Changes"
5. See success toast

**Verify Avatar**
1. Refresh page
2. Avatar should still show
3. Logout
4. Login again
5. Click Profile
6. **VERIFY AVATAR STILL SHOWS**

### Test 3: Multiple Updates

**First Update**
1. Login
2. Profile → Edit
3. Change name to "Update 1"
4. Save
5. Logout & Login
6. Verify name is "Update 1"

**Second Update**
1. Profile → Edit
2. Change name to "Update 2"
3. Change phone to "111-2222"
4. Save
5. Logout & Login
6. Verify name is "Update 2"
7. Verify phone is "111-2222"

**Third Update**
1. Profile → Edit
2. Change location to "Boston"
3. Change company to "New Corp"
4. Save
5. Logout & Login
6. Verify location is "Boston"
7. Verify company is "New Corp"

### Test 4: Browser DevTools Check

**Check localStorage**
1. Open DevTools (F12)
2. Go to Application tab
3. Click Local Storage
4. Click http://localhost:3000
5. Find `user_profile` key
6. Click it to see value
7. Should show JSON with all profile fields

**Check Network**
1. Open DevTools (F12)
2. Go to Network tab
3. Click Profile
4. Click Edit
5. Make a change
6. Click Save
7. Find PUT request to `/api/auth/profile/`
8. Click it
9. Go to Response tab
10. Should show full user object with all fields

### Test 5: Error Scenarios

**Test Missing Required Fields**
1. Login
2. Profile → Edit
3. Clear name field
4. Try to save
5. See error: "Name is required"
6. Clear email field
7. Try to save
8. See error: "Email is required"

**Test Invalid File**
1. Profile → Edit
2. Try to upload non-image file
3. See error: "Please select an image file"

**Test Large File**
1. Profile → Edit
2. Try to upload file > 5MB
3. See error: "File size must be less than 5MB"

---

## Debugging Checklist

### If Profile Data NOT Persisting

**Check 1: Backend Response**
1. Open DevTools Network tab
2. Update profile
3. Find PUT `/api/auth/profile/` request
4. Click Response tab
5. Should show full user object
6. If not, backend needs fix

**Check 2: localStorage**
1. Open DevTools Console
2. Type: `localStorage.getItem('user_profile')`
3. Should show JSON with all fields
4. If empty or null, frontend not saving

**Check 3: API Response**
1. Open DevTools Console
2. Update profile
3. Check console for errors
4. Should see "Profile updated successfully"
5. If error, check error message

**Check 4: State Update**
1. Open React DevTools
2. Click AppNew component
3. Check `profile` state
4. Should have all fields
5. If missing fields, check handleUpdateProfile

### If Avatar NOT Persisting

**Check 1: File Upload**
1. Check file is image (JPG, PNG, GIF, WebP)
2. Check file size < 5MB
3. Check no error toast

**Check 2: API Response**
1. Network tab → PUT `/api/auth/profile/`
2. Response should include `avatar` field
3. Should have URL to uploaded file

**Check 3: localStorage**
1. Console: `localStorage.getItem('user_profile')`
2. Should have `avatar` field with URL

---

## Common Issues & Solutions

### Issue: "Profile updated successfully" but data not persisting

**Solution**:
1. Check backend is returning full user object
2. Check frontend is saving to localStorage
3. Check localStorage key is `user_profile`
4. Refresh page and check localStorage

### Issue: Avatar uploads but doesn't show after logout

**Solution**:
1. Check avatar URL in localStorage
2. Check avatar file exists on server
3. Check avatar path is correct
4. Try uploading different image

### Issue: Some fields persist, others don't

**Solution**:
1. Check all fields in handleUpdateProfile
2. Check all fields in profile fetch
3. Check backend serializer includes all fields
4. Check localStorage has all fields

### Issue: localStorage shows old data after update

**Solution**:
1. Check handleUpdateProfile saves to localStorage
2. Check profile fetch saves to localStorage
3. Check localStorage is being updated
4. Try clearing localStorage and logging in again

---

## Success Indicators

✅ Profile data persists after logout/login
✅ All fields (name, phone, location, etc.) persist
✅ Avatar persists after logout/login
✅ localStorage has `user_profile` key
✅ Backend returns full user object
✅ No console errors
✅ Success toast shows on save
✅ Multiple updates work correctly

---

## Test Results Template

```
Test Date: ___________
Tester: ___________

Test 1: All Fields Persist
- Name persists: [ ] Yes [ ] No
- Phone persists: [ ] Yes [ ] No
- Location persists: [ ] Yes [ ] No
- Occupation persists: [ ] Yes [ ] No
- Company persists: [ ] Yes [ ] No
- Website persists: [ ] Yes [ ] No
- Bio persists: [ ] Yes [ ] No

Test 2: Avatar Persists
- Avatar shows after refresh: [ ] Yes [ ] No
- Avatar shows after logout/login: [ ] Yes [ ] No

Test 3: Multiple Updates
- First update persists: [ ] Yes [ ] No
- Second update persists: [ ] Yes [ ] No
- Third update persists: [ ] Yes [ ] No

Test 4: localStorage
- user_profile key exists: [ ] Yes [ ] No
- Contains all fields: [ ] Yes [ ] No
- Updates on save: [ ] Yes [ ] No

Test 5: Error Handling
- Name required error: [ ] Yes [ ] No
- Email required error: [ ] Yes [ ] No
- File type error: [ ] Yes [ ] No
- File size error: [ ] Yes [ ] No

Overall Result: [ ] PASS [ ] FAIL

Notes:
_________________________________
_________________________________
```

---

**Quick Start**: Login → Profile → Edit → Change fields → Save → Logout → Login → Verify
