# Frontend Issues & Solutions

## Issues Found

### 1. ❌ Login 401 Unauthorized
```
POST https://growfun-backend.onrender.com/api/auth/login/ 401 (Unauthorized)
```

**Cause:** Invalid credentials or wrong endpoint

**Solutions:**

#### A) Check Login Credentials
Make sure you're using correct email/password:
```javascript
// Test with known credentials
{
  email: 'admin@growfund.com',  // or your registered email
  password: 'your-password'
}
```

#### B) Check API Call Format
Your `api.js` should look like this:

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

export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login/', {
      email,
      password
    });
    return response.data;
  } catch (error) {
    console.error('Login error:', error.response?.data);
    throw error;
  }
};
```

#### C) Test Login Directly
Open browser console and test:

```javascript
fetch('https://growfun-backend.onrender.com/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'testpassword123'
  })
})
.then(res => res.json())
.then(data => console.log('Response:', data))
.catch(err => console.error('Error:', err));
```

### 2. ❌ CoinGecko CORS Errors
```
Access to fetch at 'https://api.coingecko.com/...' has been blocked by CORS policy
```

**Cause:** CoinGecko API doesn't allow direct browser calls (CORS policy)

**Solution:** Proxy CoinGecko calls through your backend

#### Backend Solution (Recommended)

Create a new endpoint in your Django backend:

**File: `backend-growfund/investments/views.py`**

Add this view:

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
from django.conf import settings

@api_view(['GET'])
@permission_classes([AllowAny])
def get_crypto_prices(request):
    """
    Proxy endpoint for CoinGecko API to avoid CORS issues
    """
    coin_ids = request.query_params.get('ids', 'bitcoin,ethereum,binancecoin,cardano,solana,polkadot')
    vs_currency = request.query_params.get('vs_currency', 'usd')
    
    try:
        # Call CoinGecko API from backend (no CORS issues)
        url = f'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': vs_currency,
            'ids': coin_ids,
            'price_change_percentage': '24h,7d,30d'
        }
        
        # Add API key if available
        api_key = settings.COINGECKO_API_KEY
        if api_key:
            headers = {'x-cg-demo-api-key': api_key}
            response = requests.get(url, params=params, headers=headers)
        else:
            response = requests.get(url, params=params)
        
        response.raise_for_status()
        return Response(response.json())
    
    except requests.exceptions.RequestException as e:
        return Response({
            'error': str(e),
            'message': 'Failed to fetch crypto prices'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_simple_prices(request):
    """
    Get simple price data from CoinGecko
    """
    coin_ids = request.query_params.get('ids', 'bitcoin,ethereum,binancecoin,cardano,solana,polkadot')
    vs_currencies = request.query_params.get('vs_currencies', 'usd')
    
    try:
        url = f'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': coin_ids,
            'vs_currencies': vs_currencies
        }
        
        api_key = settings.COINGECKO_API_KEY
        if api_key:
            headers = {'x-cg-demo-api-key': api_key}
            response = requests.get(url, params=params, headers=headers)
        else:
            response = requests.get(url, params=params)
        
        response.raise_for_status()
        return Response(response.json())
    
    except requests.exceptions.RequestException as e:
        return Response({
            'error': str(e),
            'message': 'Failed to fetch simple prices'
        }, status=500)
```

**File: `backend-growfund/investments/urls.py`**

Add these URLs:

```python
from django.urls import path
from . import views

app_name = 'investments'

urlpatterns = [
    # ... existing URLs ...
    
    # CoinGecko proxy endpoints
    path('crypto/prices/', views.get_crypto_prices, name='crypto-prices'),
    path('crypto/simple-prices/', views.get_simple_prices, name='simple-prices'),
]
```

#### Frontend Solution

Update your `coingecko.js` to use your backend:

```javascript
// coingecko.js
const API_URL = 'https://growfun-backend.onrender.com/api';

export const fetchPricesUSD = async (coinIds) => {
  try {
    const ids = coinIds.join(',');
    const response = await fetch(
      `${API_URL}/investments/crypto/simple-prices/?ids=${ids}&vs_currencies=usd`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching prices:', error);
    return null;
  }
};

export const fetchMarketData = async (coinIds) => {
  try {
    const ids = coinIds.join(',');
    const response = await fetch(
      `${API_URL}/investments/crypto/prices/?ids=${ids}&vs_currency=usd`
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching market data:', error);
    return null;
  }
};
```

### 3. ⚠️ Rate Limiting (429 Too Many Requests)

**Cause:** Too many requests to CoinGecko API

**Solutions:**

#### A) Add Caching in Backend

```python
from django.core.cache import cache

@api_view(['GET'])
@permission_classes([AllowAny])
def get_crypto_prices(request):
    coin_ids = request.query_params.get('ids', 'bitcoin,ethereum')
    
    # Check cache first (cache for 5 minutes)
    cache_key = f'crypto_prices_{coin_ids}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    # Fetch from API if not cached
    try:
        url = f'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'ids': coin_ids,
            'price_change_percentage': '24h,7d,30d'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

#### B) Reduce Polling Frequency in Frontend

In `AppNew.js`, increase the interval:

```javascript
useEffect(() => {
  fetchWatchlist();
  
  // Poll every 5 minutes instead of frequently
  const interval = setInterval(fetchWatchlist, 5 * 60 * 1000); // 5 minutes
  
  return () => clearInterval(interval);
}, []);
```

#### C) Get CoinGecko API Key

1. Sign up at https://www.coingecko.com/en/api
2. Get free API key (higher rate limits)
3. Add to backend `.env`:
   ```
   COINGECKO_API_KEY=your_api_key_here
   ```

### 4. ⚠️ React Router Warnings

**Not critical** - Just deprecation warnings for React Router v7

**Optional Fix:** Update your router configuration:

```javascript
// In your router setup
import { createBrowserRouter } from 'react-router-dom';

const router = createBrowserRouter(routes, {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
});
```

## Quick Fix Summary

### Backend Changes Needed:

1. Add CoinGecko proxy endpoints to `investments/views.py`
2. Add URLs to `investments/urls.py`
3. Add caching to reduce API calls
4. Deploy to Render

### Frontend Changes Needed:

1. Update `coingecko.js` to use backend proxy
2. Reduce polling frequency in `AppNew.js`
3. Fix login credentials or endpoint
4. Add error handling for API calls

## Testing After Fixes

### Test 1: Login
```javascript
// Should return access and refresh tokens
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John"
  }
}
```

### Test 2: Crypto Prices
```javascript
fetch('https://growfun-backend.onrender.com/api/investments/crypto/prices/?ids=bitcoin,ethereum')
  .then(res => res.json())
  .then(data => console.log('Prices:', data));
```

### Test 3: No More CORS Errors
Check browser console - should see no CORS errors

## Priority Order

1. **Fix CoinGecko CORS** (High) - Add backend proxy
2. **Fix Login 401** (High) - Check credentials
3. **Add Rate Limiting** (Medium) - Add caching
4. **React Router Warnings** (Low) - Optional

## Need Help?

If you need me to create the backend files for the CoinGecko proxy, let me know!
