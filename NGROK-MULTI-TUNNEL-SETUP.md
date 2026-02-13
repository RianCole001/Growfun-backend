# Ngrok Multi-Tunnel Setup - Run Frontend & Backend Simultaneously

## The Problem

Ngrok free tier only allows **1 simultaneous agent session**. You can't run `ngrok http 3000` and `ngrok http 8000` at the same time.

## The Solution

Use ngrok's configuration file to define multiple endpoints and run them all from a single agent session.

---

## Step 1: Create Ngrok Configuration File

Create a file at: `C:\Users\b\.ngrok2\ngrok.yml`

**Windows Path:** `%USERPROFILE%\.ngrok2\ngrok.yml`

Add this content:

```yaml
version: 3
authtoken: YOUR_NGROK_AUTH_TOKEN

tunnels:
  frontend:
    proto: http
    addr: 3000
    
  backend:
    proto: http
    addr: 8000
```

### How to Get Your Auth Token

1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your auth token
3. Replace `YOUR_NGROK_AUTH_TOKEN` in the config file above

---

## Step 2: Start All Tunnels

Instead of running separate ngrok commands, run:

```bash
ngrok start --all
```

This will start BOTH tunnels from a single agent session.

**Output will look like:**

```
Session Status                online
Account                       [your-email]
Version                        3.x.x
Region                         us (United States)
Latency                        45ms
Web Interface                  http://127.0.0.1:4040

Forwarding                     https://1234-5678-abcd.ngrok-free.app -> http://localhost:3000
Forwarding                     https://5678-abcd-1234.ngrok-free.app -> http://localhost:8000

Connections                    ttl    opn    rt1    rt5    p50    p95
                               0      0      0.00   0.00   0.00   0.00
```

---

## Step 3: Update Your Configuration

### Frontend .env

```env
REACT_APP_API_URL=https://5678-abcd-1234.ngrok-free.app/api
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_id
```

(Use the backend ngrok URL from the output above)

### Backend settings.py

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '1234-5678-abcd.ngrok-free.app',  # Frontend ngrok URL
    '5678-abcd-1234.ngrok-free.app',  # Backend ngrok URL
]
```

---

## Step 4: Restart Services

1. **Stop any running ngrok sessions** (Ctrl+C)
2. **Start ngrok with config:**
   ```bash
   ngrok start --all
   ```
3. **In another terminal, start backend:**
   ```bash
   cd backend-growfund
   python manage.py runserver
   ```
4. **In another terminal, start frontend:**
   ```bash
   cd Growfund-Dashboard/trading-dashboard
   npm start
   ```

---

## Step 5: Test

1. Open frontend: `https://1234-5678-abcd.ngrok-free.app`
2. Try login/register
3. Should work now!

---

## Configuration File Location

| OS | Path |
|----|------|
| Windows | `C:\Users\[YourUsername]\.ngrok2\ngrok.yml` |
| macOS | `~/.ngrok2/ngrok.yml` |
| Linux | `~/.ngrok2/ngrok.yml` |

---

## Troubleshooting

**Error: "authtoken not set"**
- Add your auth token to the config file
- Get it from: https://dashboard.ngrok.com/get-started/your-authtoken

**Error: "tunnel not found"**
- Make sure you're running `ngrok start --all` (not just `ngrok http 3000`)
- Check that ngrok.yml is in the correct location

**Tunnels not starting**
- Make sure ports 3000 and 8000 are not already in use
- Check that your services are running on those ports

**Still getting CORS errors**
- Clear browser cache (Ctrl+Shift+Delete)
- Make sure both ngrok URLs are in ALLOWED_HOSTS
- Make sure frontend ngrok URL is in CORS_ALLOWED_ORIGINS

---

## Quick Reference

```bash
# Create config file
# C:\Users\b\.ngrok2\ngrok.yml

# Start all tunnels
ngrok start --all

# View tunnels
# Open http://127.0.0.1:4040 in browser

# Stop tunnels
# Ctrl+C
```

---

## Important Notes

- **Ngrok URLs change every time you restart** - update .env and settings.py each time
- **Free tier limit:** 1 simultaneous agent session (but can have multiple tunnels in that session)
- **Paid tier:** Allows multiple agent sessions if needed
- **Auth token:** Keep it secret, don't commit to git

---

## Next Steps

1. Create `C:\Users\b\.ngrok2\ngrok.yml` with the config above
2. Add your auth token to the config
3. Run `ngrok start --all`
4. Update frontend .env with backend ngrok URL
5. Update backend settings.py with both ngrok URLs
6. Restart backend and frontend
7. Test login via frontend ngrok URL
