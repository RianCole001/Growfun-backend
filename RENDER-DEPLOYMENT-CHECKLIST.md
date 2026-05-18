# Render Deployment Quick Checklist

## 🗄️ Step 1: Create Database (5 min)
- [ ] Go to Render Dashboard → New + → PostgreSQL
- [ ] Name: `growfund-database`
- [ ] Region: Choose closest to users
- [ ] Plan: Free or Starter
- [ ] **Copy Internal Database URL** (save for Step 3)

---

## 🌐 Step 2: Create Web Service (2 min)
- [ ] Render Dashboard → New + → Web Service
- [ ] Connect GitHub: `RianCole001/Growfun-backend`
- [ ] Branch: `main`
- [ ] **Root Directory**: `backend-growfund` ⚠️ IMPORTANT
- [ ] Runtime: Python 3
- [ ] **Build Command**: `bash build.sh`
- [ ] **Start Command**: `bash start.sh`
- [ ] Plan: Free or Starter

---

## 🔐 Step 3: Environment Variables (5 min)

Click **Advanced** and add these:

### Minimum Required:
```bash
SECRET_KEY=<generate-with-django-command>
DEBUG=False
ALLOWED_HOSTS=*
DATABASE_URL=<paste-from-step-1>
FRONTEND_URL=https://growfundapp.us
BACKEND_URL=https://your-service-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-service-name.onrender.com,https://growfundapp.us
```

### Generate SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🚀 Step 4: Deploy (10 min)
- [ ] Click **Create Web Service**
- [ ] Wait for build to complete
- [ ] Check logs for success messages

---

## ✅ Step 5: Verify (2 min)
- [ ] Service shows "Live" status
- [ ] Logs show: "Starting Gunicorn server..."
- [ ] Visit: `https://your-service-name.onrender.com/admin/`

---

## 👤 Step 6: Create Admin (2 min)
Go to Shell tab and run:
```bash
cd backend-growfund
python create_tabby_admin.py
```

---

## 🎯 Expected Results

### Build Logs Should Show:
```
📦 Installing dependencies...
📁 Collecting static files...
✅ Build completed successfully!
```

### Runtime Logs Should Show:
```
🔄 Running database migrations...
⚙️ Setting up platform settings...
💰 Setting up crypto prices...
🚀 Starting Gunicorn server...
[INFO] Listening at: http://0.0.0.0:10000
```

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **Forgetting Root Directory**: Must be `backend-growfund`
2. ❌ **Wrong Start Command**: Must be `bash start.sh` (not gunicorn directly)
3. ❌ **Missing DATABASE_URL**: Copy from database Internal URL
4. ❌ **Short SECRET_KEY**: Must be 50+ characters
5. ❌ **Wrong Build Command**: Must be `bash build.sh`

---

## 📝 Configuration Summary

| Setting | Value |
|---------|-------|
| Root Directory | `backend-growfund` |
| Build Command | `bash build.sh` |
| Start Command | `bash start.sh` |
| Runtime | Python 3 |
| Branch | `main` |

---

## 🔗 Your Service URLs

After deployment:
- **Service**: `https://your-service-name.onrender.com`
- **Admin**: `https://your-service-name.onrender.com/admin/`
- **API**: `https://your-service-name.onrender.com/api/`

---

## 🔄 Auto-Deployment

Every push to `main` branch triggers automatic redeployment:
```bash
git push origin main
```

---

## 📞 Need Help?

See detailed guide: `RENDER-FRESH-DEPLOYMENT-GUIDE.md`

---

**Total Time: ~25 minutes** ⏱️
