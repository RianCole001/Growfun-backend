# MTN Mobile Money - Quick Start

## ✅ What's Done
- Transaction models created
- MoMo API service integrated
- Payment endpoints ready
- Migrations completed locally

## 🚀 Next Steps

### 1. Add Environment Variables to Back4app

Go to Back4app → Settings → Environment Variables and add:

```
MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MOMO_COLLECTION_SUBSCRIPTION_KEY=your_key_here
MOMO_DISBURSEMENT_SUBSCRIPTION_KEY=your_key_here
MOMO_API_USER=your_uuid_here
MOMO_API_KEY=your_key_here
MOMO_CALLBACK_URL=http://growfund-6pu3fil9.b4a.run/api/transactions/momo/callback/
MOMO_ENVIRONMENT=sandbox
```

### 2. Get MTN MoMo Credentials

1. Visit: https://momodeveloper.mtn.com/
2. Sign up and create account
3. Subscribe to Collection and Disbursement products
4. Get your subscription keys
5. Create API user and get credentials

### 3. Commit and Push Changes

```powershell
git add .
git commit -m "Add MTN Mobile Money integration"
git push origin main
```

### 4. Test API Endpoints

**Deposit:**
```
POST http://growfund-6pu3fil9.b4a.run/api/transactions/momo/deposit/
Authorization: Bearer <token>

{
  "amount": 10000,
  "phone_number": "+256700000000"
}
```

**Withdrawal:**
```
POST http://growfund-6pu3fil9.b4a.run/api/transactions/momo/withdrawal/
Authorization: Bearer <token>

{
  "amount": 5000,
  "phone_number": "+256700000000"
}
```

**Check Status:**
```
POST http://growfund-6pu3fil9.b4a.run/api/transactions/momo/status/
Authorization: Bearer <token>

{
  "reference_id": "uuid-from-momo"
}
```

**List Transactions:**
```
GET http://growfund-6pu3fil9.b4a.run/api/transactions/
Authorization: Bearer <token>
```

## 📱 Test Phone Numbers (Sandbox)

- `46733123450` - Auto approve
- `46733123451` - Auto reject
- `46733123452` - Timeout

## 🔧 Currency Configuration

Edit `backend-growfund/transactions/momo_service.py` line 60 and 145:

```python
'currency': 'UGX',  # Uganda Shillings
# or 'GHS' for Ghana, 'ZAR' for South Africa, etc.
```

## 📚 Full Documentation

See `backend-growfund/MOMO-SETUP-GUIDE.md` for complete setup instructions.
