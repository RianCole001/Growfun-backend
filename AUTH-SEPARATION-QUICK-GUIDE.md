# Authentication Separation - Quick Guide

## What Changed

User and admin authentication are now completely separate. They don't interfere with each other.

## Key Points

### Storage
- **User tokens**: `user_access_token`, `user_refresh_token`
- **Admin tokens**: `admin_access_token`, `admin_refresh_token`

### API Instances
- **User API**: Uses `userAuthAPI` and `userApi`
- **Admin API**: Uses `adminAuthAPI` and `adminApi`

### Contexts
- **User**: `UserAuthContext` with `useUserAuth()` hook
- **Admin**: `AdminAuthContext` with `useAdminAuth()` hook

## Testing

### Test 1: User Login Doesn't Affect Admin
```
1. Login as user at /login
2. Go to /admin
3. Should see admin login gate (not logged in)
4. Login as admin
5. User dashboard still works at /app
```

### Test 2: Admin Login Doesn't Affect User
```
1. Login as admin at /admin
2. Go to /app
3. Should see user login gate (not logged in)
4. Login as user
5. Admin portal still works at /admin
```

### Test 3: Separate Tokens
```
1. Login as user
2. Open DevTools Console
3. Type: localStorage.getItem('user_access_token')
   → Should show token
4. Type: localStorage.getItem('admin_access_token')
   → Should show null
```

## Usage in Code

### User Component
```javascript
import { useUserAuth } from '../auth/UserAuthContext';
import { userAuthAPI } from '../services/api';

function UserDashboard() {
  const { userAuth, logoutUser } = useUserAuth();
  const profile = await userAuthAPI.getProfile();
}
```

### Admin Component
```javascript
import { useAdminAuth } from '../auth/AdminAuthContext';
import { adminAuthAPI } from '../services/api';

function AdminDashboard() {
  const { adminAuth, logoutAdmin } = useAdminAuth();
  const users = await adminAuthAPI.getAdminUsers();
}
```

## Files to Know

| File | Purpose |
|------|---------|
| `src/auth/UserAuthContext.js` | User auth state management |
| `src/auth/AdminAuthContext.js` | Admin auth state management |
| `src/services/api.js` | Separate API instances |
| `src/index.js` | Both providers wrapped |
| `src/AppNew.js` | User dashboard |
| `src/AdminApp.js` | Admin portal |

## Common Issues

### Issue: User login affects admin
**Cause**: Using wrong API instance
**Fix**: Use `userAuthAPI` for users, `adminAuthAPI` for admins

### Issue: Tokens getting mixed up
**Cause**: Using old `authAPI`
**Fix**: Use `userAuthAPI` or `adminAuthAPI` explicitly

### Issue: Logout doesn't work
**Cause**: Not using the context's logout function
**Fix**: Use `logoutUser()` or `logoutAdmin()` from context

## Checklist

- ✅ User and admin have separate storage keys
- ✅ User and admin have separate API instances
- ✅ User and admin have separate contexts
- ✅ User redirects to `/login` on 401
- ✅ Admin redirects to `/admin` on 401
- ✅ Logging in as user doesn't affect admin
- ✅ Logging in as admin doesn't affect user
- ✅ Logout clears only relevant tokens

## Next Steps

1. Test user login/logout
2. Test admin login/logout
3. Test switching between user and admin
4. Test token refresh for each role
5. Test 401 error handling for each role
