# Ngrok CORS Solution

## Problem
Ngrok URLs change every time you restart ngrok, requiring constant updates to CORS settings.

## Current Fix ✅
Added your current ngrok URL: `https://f9ce-41-81-28-77.ngrok-free.app`

## Better Solutions

### Option 1: Allow All Origins (Development Only)

In `settings.py`, replace the CORS_ALLOWED_ORIGINS with:

```python
# For development with ngrok - allows any origin
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

⚠️ **Important:** Only use this in development! Remove before production.

### Option 2: Use Ngrok Pattern Matching

```python
import re

# Custom CORS origin checker
def cors_allow_ngrok(origin):
    if origin in [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]:
        return True
    # Allow any ngrok URL
    if re.match(r'https://[a-z0-9-]+\.ngrok-free\.app', origin):
        return True
    return False

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://[a-z0-9-]+\.ngrok-free\.app$",
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]
```

### Option 3: Environment Variable (Recommended)

Update `settings.py`:

```python
# Get additional CORS origins from environment
additional_origins = config('ADDITIONAL_CORS_ORIGINS', default='').split(',')
additional_origins = [origin.strip() for origin in additional_origins if origin.strip()]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
] + additional_origins
```

Then on Render, set environment variable:
```
ADDITIONAL_CORS_ORIGINS=https://f9ce-41-81-28-77.ngrok-free.app,https://your-other-url.com
```

## Quick Fix for Now

### Step 1: Update settings.py

Choose one approach:

**A) Allow all origins (easiest for development):**
```python
# Comment out CORS_ALLOWED_ORIGINS
# CORS_ALLOWED_ORIGINS = [...]

# Add this instead
CORS_ALLOW_ALL_ORIGINS = True
```

**B) Use regex pattern (more secure):**
```python
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://[a-z0-9-]+\.ngrok-free\.app$",
    r"^http://localhost:\d+$",
]
```

### Step 2: Deploy to Render

```bash
git add backend-growfund/growfund/settings.py
git commit -m "Fix CORS for ngrok URLs"
git push
```

Then redeploy on Render dashboard.

### Step 3: Test

From your React app console:
```javascript
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123'
  })
})
.then(res => res.json())
.then(data => console.log('✅ Success:', data))
.catch(err => console.error('❌ Error:', err));
```

## Recommended Approach for Development

Edit `settings.py` and add this at the end of CORS section:

```python
# CORS Settings
if DEBUG:
    # Allow all origins in development
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Restrict origins in production
    CORS_ALLOWED_ORIGINS = [
        'https://your-production-frontend.com',
    ]

CORS_ALLOW_CREDENTIALS = True
```

This way:
- ✅ Development: Works with any ngrok URL or localhost
- ✅ Production: Secure with specific allowed origins
- ✅ No need to update settings every time ngrok restarts

## Implementation

I'll create a better settings configuration for you:
