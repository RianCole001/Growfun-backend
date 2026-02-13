# Separate Authentication Contexts - User vs Admin

## Overview

The application now has completely separate authentication systems for users and admins. This ensures that logging in as a user doesn't affect the admin portal, and vice versa.

## Architecture

### Storage Keys

**User Authentication:**
- `user_access_token` - User JWT access token
- `user_refresh_token` - User JWT refresh token
- `user_data` - User profile data

**Admin Authentication:**
- `admin_access_token` - Admin JWT access token
- `admin_refresh_token` - Admin JWT refresh token
- `admin_data` - Admin profile data

### API Instances

**User API (`userApi`):**
- Uses `user_access_token` for requests
- Redirects to `/login` on 401 error
- Used by user dashboard and pages

**Admin API (`adminApi`):**
- Uses `admin_access_token` for requests
- Redirects to `/admin` on 401 error
- Used by admin portal only

## Authentication Contexts

### UserAuthContext
```javascript
// Location: src/auth/UserAuthContext.js
// Manages user authentication state
// Methods: loginUser(), logoutUser()
// Usage: useUserAuth() hook
```

### AdminAuthContext
```javascript
// Location: src/auth/AdminAuthContext.js
// Manages admin authentication state
// Methods: loginAdmin(), logoutAdmin()
// Usage: useAdminAuth() hook
```

## API Endpoints

### User API (`userAuthAPI`)
```javascript
- register(data)
- login(email, password)
- verifyEmail(token)
- forgotPassword(email)
- resetPassword(token, password, password2)
- getCurrentUser()
- getProfile()
- updateProfile(data)
- getSettings()
- updateSettings(data)
- changePassword(oldPassword, newPassword, newPassword2)
- getBalance()
```

### Admin API (`adminAuthAPI`)
```javascript
- login(email, password)
- getCurrentUser()
- getAdminUsers()
```

## Data Flow

### User Login Flow
```
LoginPage
    ↓
userAuthAPI.login()
    ↓
userApi (with user_access_token)
    ↓
UserAuthContext.loginUser()
    ↓
AppNew (User Dashboard)
```

### Admin Login Flow
```
AdminApp (Login Gate)
    ↓
adminAuthAPI.login()
    ↓
adminApi (with admin_access_token)
    ↓
AdminAuthContext.loginAdmin()
    ↓
AdminApp (Admin Dashboard)
```

## Isolation Benefits

✅ **No Token Conflicts** - User and admin tokens are stored separately
✅ **Independent Sessions** - Logging in as user doesn't affect admin session
✅ **Separate Redirects** - User redirects to `/login`, admin redirects to `/admin`
✅ **Different API Instances** - Each uses its own axios instance
✅ **Isolated State** - Each has its own React context

## Usage Examples

### In User Components
```javascript
import { useUserAuth } from '../auth/UserAuthContext';
import { userAuthAPI } from '../services/api';

function MyComponent() {
  const { userAuth, loginUser, logoutUser } = useUserAuth();
  
  // Use userAuthAPI for API calls
  const data = await userAuthAPI.getProfile();
}
```

### In Admin Components
```javascript
import { useAdminAuth } from '../auth/AdminAuthContext';
import { adminAuthAPI } from '../services/api';

function AdminComponent() {
  const { adminAuth, loginAdmin, logoutAdmin } = useAdminAuth();
  
  // Use adminAuthAPI for API calls
  const users = await adminAuthAPI.getAdminUsers();
}
```

## Testing Scenarios

### Scenario 1: User Login Doesn't Affect Admin
1. Login as user: `user@example.com`
2. Go to `/admin`
3. Admin portal should show login gate (not logged in)
4. Login as admin: `admin001@gmail.com`
5. User dashboard should still be accessible at `/app`

### Scenario 2: Admin Login Doesn't Affect User
1. Login as admin: `admin001@gmail.com`
2. Go to `/app`
3. User dashboard should show login gate (not logged in)
4. Login as user: `user@example.com`
5. Admin portal should still be accessible at `/admin`

### Scenario 3: Separate Tokens
1. Login as user
2. Check `localStorage.getItem('user_access_token')` - should exist
3. Check `localStorage.getItem('admin_access_token')` - should be null
4. Logout user
5. Check `localStorage.getItem('user_access_token')` - should be null
6. Check `localStorage.getItem('admin_access_token')` - should still be null

### Scenario 4: Independent Logouts
1. Login as user
2. Login as admin (in different tab or after user logout)
3. Logout user
4. Admin should still be logged in
5. Logout admin
6. Both should be logged out

## Files Modified

### New Files
- `src/auth/UserAuthContext.js` - User authentication context
- `src/auth/AdminAuthContext.js` - Admin authentication context

### Modified Files
- `src/services/api.js` - Separate API instances and endpoints
- `src/index.js` - Added both auth providers
- `src/AppNew.js` - Uses userAuthAPI and UserAuthContext
- `src/AdminApp.js` - Uses adminAuthAPI and AdminAuthContext
- `src/pages/LoginPage.js` - Uses userAuthAPI and UserAuthContext
- `src/admin/AdminUsers.js` - Uses adminAuthAPI

## Migration Guide

If you have existing code using the old `authAPI`:

### Before
```javascript
import { authAPI } from '../services/api';
const response = await authAPI.login(email, password);
```

### After (User)
```javascript
import { userAuthAPI } from '../services/api';
const response = await userAuthAPI.login(email, password);
```

### After (Admin)
```javascript
import { adminAuthAPI } from '../services/api';
const response = await adminAuthAPI.login(email, password);
```

## Backward Compatibility

The old `authAPI` is still available as an alias to `userAuthAPI` for backward compatibility:

```javascript
import { authAPI } from '../services/api';
// authAPI === userAuthAPI
```

## Security Considerations

✅ Tokens are stored separately in localStorage
✅ Each API instance has its own interceptors
✅ Token refresh is independent for each role
✅ Logout clears only the relevant tokens
✅ 401 errors redirect to appropriate login page

## Future Enhancements

- Add role-based route protection
- Implement token expiration warnings
- Add session timeout for each role
- Implement concurrent session limits
- Add audit logging for admin actions
