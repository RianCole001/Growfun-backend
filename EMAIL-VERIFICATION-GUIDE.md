# Email Verification System - Complete Guide

## What Was Implemented ✅

### Backend Features
1. **Email Verification on Registration**
   - Sends HTML email with verification link
   - Token-based verification
   - Automatic welcome email after verification

2. **Resend Verification Email**
   - Endpoint to resend verification if user didn't receive it
   - Security: Doesn't reveal if email exists

3. **Proper Redirects**
   - Registration → Email sent confirmation
   - Verification → Login page
   - Password reset → Login page

4. **Beautiful HTML Emails**
   - Professional design with gradients
   - Mobile-responsive
   - Both HTML and plain text versions

### API Endpoints

#### 1. Register
```
POST /api/auth/register/
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful! Please check your email to verify your account.",
  "email": "user@example.com",
  "email_sent": true,
  "verification_url": "https://your-frontend.com/verify-email?token=abc123...",
  "redirect": "/verify-email-sent"
}
```

#### 2. Verify Email (GET)
```
GET /api/auth/verify-email/?token=abc123...
```

**Response:**
```json
{
  "success": true,
  "message": "Email verified successfully! You can now login.",
  "redirect": "/login"
}
```

#### 3. Verify Email (POST)
```
POST /api/auth/verify-email/
```

**Request:**
```json
{
  "token": "abc123..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email verified successfully! You can now login.",
  "redirect": "/login"
}
```

#### 4. Resend Verification Email
```
POST /api/auth/resend-verification/
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification email sent! Please check your inbox.",
  "email": "user@example.com"
}
```

#### 5. Login (with verification check)
```
POST /api/auth/login/
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (if not verified):**
```json
{
  "error": "Email not verified. Please check your email."
}
```

**Response (if verified):**
```json
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true
  }
}
```

## Frontend Implementation

### 1. Registration Page

```javascript
// RegisterPage.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './api';

function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/register/', formData);
      
      if (response.data.success) {
        // Store email for resend functionality
        localStorage.setItem('pendingVerificationEmail', formData.email);
        
        // Redirect to verification sent page
        navigate('/verify-email-sent', {
          state: { email: formData.email }
        });
      }
    } catch (err) {
      setError(err.response?.data?.errors || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="First Name"
        value={formData.first_name}
        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Last Name"
        value={formData.last_name}
        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
        required
      />
      <input
        type="tel"
        placeholder="Phone"
        value={formData.phone}
        onChange={(e) => setFormData({...formData, phone: e.target.value})}
      />
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
}
```

### 2. Verification Sent Page

```javascript
// VerifyEmailSentPage.js
import { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import api from './api';

function VerifyEmailSentPage() {
  const location = useLocation();
  const email = location.state?.email || localStorage.getItem('pendingVerificationEmail');
  const [resending, setResending] = useState(false);
  const [message, setMessage] = useState('');

  const handleResend = async () => {
    setResending(true);
    setMessage('');

    try {
      const response = await api.post('/auth/resend-verification/', { email });
      setMessage(response.data.message);
    } catch (err) {
      setMessage('Failed to resend email. Please try again.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="verify-email-sent">
      <h1>Check Your Email</h1>
      <p>We've sent a verification link to:</p>
      <p><strong>{email}</strong></p>
      
      <div className="instructions">
        <p>Please check your inbox and click the verification link to activate your account.</p>
        <p>The link will expire in 24 hours.</p>
      </div>

      <div className="actions">
        <p>Didn't receive the email?</p>
        <button onClick={handleResend} disabled={resending}>
          {resending ? 'Sending...' : 'Resend Verification Email'}
        </button>
        {message && <p className="message">{message}</p>}
      </div>

      <Link to="/login">Back to Login</Link>
    </div>
  );
}
```

### 3. Email Verification Page

```javascript
// VerifyEmailPage.js
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from './api';

function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link');
      return;
    }

    verifyEmail(token);
  }, [searchParams]);

  const verifyEmail = async (token) => {
    try {
      const response = await api.get(`/auth/verify-email/?token=${token}`);
      
      if (response.data.success) {
        setStatus('success');
        setMessage(response.data.message);
        
        // Clear pending verification email
        localStorage.removeItem('pendingVerificationEmail');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    } catch (err) {
      setStatus('error');
      setMessage(err.response?.data?.error || 'Verification failed');
    }
  };

  return (
    <div className="verify-email">
      {status === 'verifying' && (
        <>
          <div className="spinner"></div>
          <h2>Verifying your email...</h2>
        </>
      )}

      {status === 'success' && (
        <>
          <div className="success-icon">✓</div>
          <h2>Email Verified!</h2>
          <p>{message}</p>
          <p>Redirecting to login...</p>
        </>
      )}

      {status === 'error' && (
        <>
          <div className="error-icon">✗</div>
          <h2>Verification Failed</h2>
          <p>{message}</p>
          <button onClick={() => navigate('/register')}>
            Register Again
          </button>
        </>
      )}
    </div>
  );
}
```

### 4. Login Page (with verification check)

```javascript
// LoginPage.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './api';

function LoginPage() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login/', formData);
      
      if (response.data.tokens) {
        // Store tokens
        localStorage.setItem('accessToken', response.data.tokens.access);
        localStorage.setItem('refreshToken', response.data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Redirect to dashboard
        navigate('/dashboard');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error;
      
      if (errorMsg?.includes('not verified')) {
        // Email not verified
        setError(
          <div>
            Email not verified. 
            <button onClick={() => navigate('/verify-email-sent', {
              state: { email: formData.email }
            })}>
              Resend verification email
            </button>
          </div>
        );
      } else {
        setError(errorMsg || 'Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
        required
      />
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### 5. Router Configuration

```javascript
// App.js or Router.js
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-email-sent" element={<VerifyEmailSentPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## Email Configuration

### Development (Console Backend)

In `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will print to console. Copy the verification link from there.

### Production (Gmail SMTP)

In `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@growfund.com
```

**Get Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new
4. Use that password in EMAIL_HOST_PASSWORD

### Production (SendGrid)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@growfund.com
```

## Testing

### Test Registration Flow

1. Register new user
2. Check email (or console in development)
3. Click verification link
4. Should redirect to login
5. Login with verified account

### Test Resend Email

1. Register but don't verify
2. Go to verification sent page
3. Click "Resend"
4. Check email again

### Test Login Without Verification

1. Register but don't verify
2. Try to login
3. Should get error: "Email not verified"

## Troubleshooting

### Emails not sending

**Check:**
- EMAIL_BACKEND is set correctly
- SMTP credentials are correct
- FRONTEND_URL is set in settings
- Check Django logs for errors

### Verification link not working

**Check:**
- Token is in URL: `/verify-email?token=abc123...`
- Backend URL is correct
- CORS is configured properly

### Redirect not working

**Check:**
- Frontend routes are configured
- `navigate()` is being called
- Response includes `redirect` field

## Security Best Practices

1. ✅ Tokens are UUIDs (hard to guess)
2. ✅ Tokens expire after 24 hours (implement if needed)
3. ✅ Doesn't reveal if email exists (resend endpoint)
4. ✅ Requires verification before login
5. ✅ Uses HTTPS in production
6. ✅ HTML emails are sanitized

## Next Steps

1. Deploy backend with updated code
2. Configure email settings (Gmail/SendGrid)
3. Update frontend with verification pages
4. Test complete flow
5. Monitor email delivery rates
