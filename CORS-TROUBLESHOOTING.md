# CORS Troubleshooting Guide

## Current Configuration ✅

Your `settings.py` already includes:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
]
CORS_ALLOW_CREDENTIALS = True
```

## Deployment Steps

### 1. Commit and Push Changes
```bash
git add backend-growfund/growfund/settings.py
git commit -m "Update CORS settings for localhost:3000"
git push
```

### 2. Redeploy on Render
- Go to your Render dashboard
- Click on your backend service
- Click "Manual Deploy" → "Deploy latest commit"
- Wait for deployment to complete

### 3. Verify Deployment
Check the logs to ensure no errors:
```
https://dashboard.render.com/
```

## Testing CORS

### Test 1: Browser Console
Open your React app at `http://localhost:3000` and run:

```javascript
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'http://localhost:3000',
    'Access-Control-Request-Method': 'POST'
  }
})
.then(response => {
  console.log('✅ CORS working!', response.status);
  console.log('Headers:', [...response.headers.entries()]);
})
.catch(error => console.error('❌ CORS error:', error));
```

### Test 2: Actual API Call
```javascript
fetch('https://growfun-backend.onrender.com/api/investments/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include'
})
.then(res => res.json())
.then(data => console.log('✅ API working:', data))
.catch(err => console.error('❌ API error:', err));
```

## If CORS Still Fails

### Option 1: Allow All Origins (Development Only)

In `settings.py`, temporarily replace CORS_ALLOWED_ORIGINS with:

```python
# TEMPORARY - For development only!
CORS_ALLOW_ALL_ORIGINS = True
```

⚠️ **Warning:** Only use this for testing. Remove before production!

### Option 2: Check Middleware Order

Ensure `corsheaders.middleware.CorsMiddleware` is at the top:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Must be here!
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]
```

✅ This is already correct in your settings.

### Option 3: Add More CORS Headers

If you need additional headers, add to `settings.py`:

```python
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

✅ This is already configured.

## Common CORS Errors

### Error: "No 'Access-Control-Allow-Origin' header"

**Cause:** Backend not allowing your origin

**Solution:**
1. Verify `http://localhost:3000` is in `CORS_ALLOWED_ORIGINS`
2. Redeploy to Render
3. Clear browser cache
4. Try in incognito mode

### Error: "CORS policy: credentials mode is 'include'"

**Cause:** Missing `CORS_ALLOW_CREDENTIALS`

**Solution:**
```python
CORS_ALLOW_CREDENTIALS = True  # ✅ Already set
```

### Error: "Method not allowed"

**Cause:** Missing HTTP method in CORS_ALLOW_METHODS

**Solution:**
```python
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
```

✅ This is already configured.

## React App Configuration

### Axios Setup (Recommended)

```javascript
// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://growfun-backend.onrender.com/api',
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

### Fetch Setup

```javascript
// src/api/config.js
export const API_URL = 'https://growfun-backend.onrender.com/api';

export const fetchWithAuth = async (endpoint, options = {}) => {
  const token = localStorage.getItem('accessToken');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    credentials: 'include',
  };
  
  const response = await fetch(`${API_URL}${endpoint}`, config);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
};
```

## Environment Variables

### Create `.env` in React app root

```env
REACT_APP_API_URL=https://growfun-backend.onrender.com/api
```

### Use in code

```javascript
const API_URL = process.env.REACT_APP_API_URL;

fetch(`${API_URL}/auth/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ email, password })
});
```

## Debugging Checklist

- [ ] `corsheaders` is installed: `pip list | grep django-cors-headers`
- [ ] `corsheaders` is in `INSTALLED_APPS`
- [ ] `CorsMiddleware` is in `MIDDLEWARE` (near the top)
- [ ] `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
- [ ] `CORS_ALLOW_CREDENTIALS = True` is set
- [ ] Changes are committed and pushed to Git
- [ ] Backend is redeployed on Render
- [ ] Browser cache is cleared
- [ ] Using `credentials: 'include'` in fetch requests
- [ ] No typos in URLs (http vs https, trailing slashes)

## Still Having Issues?

### Check Render Logs

1. Go to Render dashboard
2. Click your backend service
3. Click "Logs" tab
4. Look for CORS-related errors

### Test with cURL

```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     -v \
     https://growfun-backend.onrender.com/api/auth/login/
```

Look for these headers in response:
- `Access-Control-Allow-Origin: http://localhost:3000`
- `Access-Control-Allow-Credentials: true`

### Contact Support

If nothing works:
1. Share the exact error message from browser console
2. Share the Network tab details (Headers section)
3. Confirm the backend URL is correct
4. Verify you've redeployed after changes

## Quick Fix for Testing

If you need to test immediately and CORS is blocking you:

### Browser Extension (Chrome/Edge)
Install "CORS Unblock" extension (development only!)

### Proxy in React (package.json)
```json
{
  "proxy": "https://growfun-backend.onrender.com"
}
```

Then use relative URLs:
```javascript
fetch('/api/auth/login/', { ... })
```

⚠️ **Note:** Proxy only works in development mode!

## Production Considerations

When deploying your React app to production:

1. Add your production frontend URL to `CORS_ALLOWED_ORIGINS`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Development
    'https://your-frontend-domain.com',  # Production
]
```

2. Remove `CORS_ALLOW_ALL_ORIGINS = True` if you used it

3. Update `CSRF_TRUSTED_ORIGINS` to include production URLs

4. Set `DEBUG = False` in production

5. Use environment variables for URLs
