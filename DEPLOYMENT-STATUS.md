# Deployment Status & Next Steps

## Current Backend URL
`https://growfund-g5r8eu3x.b4a.run`

## Current Ngrok URL
`https://de0b-105-160-0-247.ngrok-free.app`

## ⚠️ Issues to Fix

### 1. Git Merge Conflict
There's a stuck merge in git. To fix:
```powershell
# Delete the stuck merge file manually
Remove-Item -Force .git/MERGE_MSG
# Then commit
git add .
git commit -m "Update CORS and ALLOWED_HOSTS"
git push origin main
```

### 2. Back4app Environment Variables Needed

Add these in Back4app → Settings → Environment Variables:

| Name | Value |
|------|-------|
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,growfund-g5r8eu3x.b4a.run,node360a.containers.back4app.com` |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:3001,https://de0b-105-160-0-247.ngrok-free.app` |
| `DEBUG` | `False` |

### 3. MTN MoMo Environment Variables (When Ready)

| Name | Value |
|------|-------|
| `MOMO_BASE_URL` | `https://sandbox.momodeveloper.mtn.com` |
| `MOMO_COLLECTION_SUBSCRIPTION_KEY` | `10907975a7a8481cba8ddd10776d29d1` |
| `MOMO_DISBURSEMENT_SUBSCRIPTION_KEY` | `10907975a7a8481cba8ddd10776d29d1` |
| `MOMO_API_USER` | `(get from MTN portal)` |
| `MOMO_API_KEY` | `(get from MTN portal)` |
| `MOMO_CALLBACK_URL` | `https://growfund-g5r8eu3x.b4a.run/api/transactions/momo/callback/` |
| `MOMO_ENVIRONMENT` | `sandbox` |

## Frontend Configuration

Update `.env` in your frontend:
```env
REACT_APP_API_URL=https://growfund-g5r8eu3x.b4a.run/api/
```

## Quick Fix for CORS (Immediate)

If Back4app deployment is taking too long:

1. Go to Back4app Dashboard
2. Click "Redeploy" button
3. Wait 2-3 minutes
4. Check logs to confirm deployment completed
5. Test the ngrok URL again

## Verification Steps

1. Check Back4app logs show: `[INFO] Listening at: http://0.0.0.0:8000`
2. Visit: `https://growfund-g5r8eu3x.b4a.run/api/` (should show API root)
3. Test login from ngrok URL
4. Check browser console for CORS errors

## MTN MoMo Setup (Pending)

Still need to:
1. Create API user successfully (getting 401 errors)
2. Generate API key
3. Add credentials to Back4app
4. Test deposit/withdrawal endpoints

## Current Status

✅ Backend deployed to Back4app  
✅ MoMo integration code complete  
✅ Migrations run successfully  
⚠️ CORS configuration pending deployment  
⚠️ MTN MoMo credentials pending  
❌ Git merge conflict blocking commits  

## Next Action

**Priority 1:** Fix the CORS issue by ensuring Back4app has redeployed with the environment variables.

**Priority 2:** Fix git merge conflict to enable future deployments.

**Priority 3:** Complete MTN MoMo API user creation.
