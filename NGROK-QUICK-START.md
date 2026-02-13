# Ngrok Quick Start - 5 Minutes

## 1️⃣ Install Ngrok

```bash
# Windows (Chocolatey)
choco install ngrok

# Mac
brew install ngrok

# Linux
snap install ngrok
```

## 2️⃣ Get Auth Token

1. Go to https://ngrok.com
2. Sign up (free)
3. Copy auth token from dashboard
4. Run:
```bash
ngrok config add-authtoken YOUR_TOKEN
```

## 3️⃣ Start Your Services

**Terminal 1 - Backend:**
```bash
cd backend-growfund
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd Growfund-Dashboard/trading-dashboard
npm start
```

## 4️⃣ Share with Ngrok

**Terminal 3 - Backend Tunnel:**
```bash
ngrok http 8000
```

Copy the URL: `https://xxxx-xxxx-xxxx.ngrok.io`

**Terminal 4 - Frontend Tunnel:**
```bash
ngrok http 3000
```

Copy the URL: `https://yyyy-yyyy-yyyy.ngrok.io`

## 5️⃣ Update Configuration

### Backend (settings.py)
```python
ALLOWED_HOSTS = ['localhost', 'xxxx-xxxx-xxxx.ngrok.io']
CORS_ALLOWED_ORIGINS = ['https://yyyy-yyyy-yyyy.ngrok.io']
```

### Frontend (.env)
```
REACT_APP_API_URL=https://xxxx-xxxx-xxxx.ngrok.io
```

## 6️⃣ Share URLs

Send to others:
- **Frontend:** https://yyyy-yyyy-yyyy.ngrok.io
- **Backend:** https://xxxx-xxxx-xxxx.ngrok.io

## 7️⃣ Monitor Traffic

Open: http://localhost:4040

---

## 🎯 Done! Your project is now shareable!
