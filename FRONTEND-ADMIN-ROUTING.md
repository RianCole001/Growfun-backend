# Frontend Admin Panel Routing Guide

## The Problem

Your frontend is at: `https://growfund-dashboard.onrender.com`
Your backend is at: `https://growfun-backend.onrender.com`

When users go to `https://growfund-dashboard.onrender.com/admin`, they should see your React admin panel, which makes API calls to the backend.

## URLs Explained

### Frontend URLs (React Routes)
These are handled by your React app:
```
https://growfund-dashboard.onrender.com/          → Home page
https://growfund-dashboard.onrender.com/login     → Login page
https://growfund-dashboard.onrender.com/register  → Register page
https://growfund-dashboard.onrender.com/admin     → Admin panel (React component)
https://growfund-dashboard.onrender.com/admin/deposits     → Deposits page
https://growfund-dashboard.onrender.com/admin/withdrawals  → Withdrawals page
```

### Backend URLs (Django API)
These are API endpoints your frontend calls:
```
https://growfun-backend.onrender.com/admin/       → Django admin (for developers only)
https://growfun-backend.onrender.com/api/auth/login/
https://growfun-backend.onrender.com/api/transactions/admin/deposits/
https://growfun-backend.onrender.com/api/transactions/admin/withdrawals/
```

## Frontend Configuration

### 1. Environment Variables

Create `.env` in your frontend:
```env
REACT_APP_API_URL=https://growfun-backend.onrender.com/api
REACT_APP_BACKEND_URL=https://growfun-backend.onrender.com
```

### 2. API Configuration

Create `src/api/config.js`:
```javascript
export const API_URL = process.env.REACT_APP_API_URL || 'https://growfun-backend.onrender.com/api';
export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://growfun-backend.onrender.com';
```

### 3. Axios Setup

Create `src/api/axios.js`:
```javascript
import axios from 'axios';
import { API_URL } from './config';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(
          `${API_URL.replace('/api', '')}/api/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('accessToken', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### 4. Admin API Service

Create `src/api/adminService.js`:
```javascript
import api from './axios';

export const adminService = {
  // Deposits
  getDeposits: (params) 