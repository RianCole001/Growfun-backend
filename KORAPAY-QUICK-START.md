# Korapay Quick Start Guide

## What Was Fixed

✅ Added Korapay configuration to `settings.py`
✅ Updated `.env.example` with Korapay variables
✅ All endpoints are already configured
✅ Service layer is ready

## Next Steps

### 1. Get Your API Keys

1. Sign up at [Korapay Dashboard](https://dashboard.korapay.com/)
2. Complete KYC verification
3. Go to Settings → API Keys
4. Copy your keys:
   - Secret Key (starts with `sk_test_` or `sk_live_`)
   - Public Key (starts with `pk_test_` or `pk_live_`)
   - Encryption Key (optional)

### 2. Configure Environment Variables

Create or update your `.env` file:

```env
# Korapay Configuration
KORAPAY_BASE_URL=https://api.korapay.com/merchant/api/v1
KORAPAY_SECRET_KEY=sk_test_your_actual_secret_key
KORAPAY_PUBLIC_KEY=pk_test_your_actual_public_key
KORAPAY_ENCRYPTION_KEY=your_actual_encryption_key
KORAPAY_WEBHOOK_URL=https://your-backend-url.com/api/transactions/korapay/webhook/
```

### 3. Test the Integration

Start your server:
```bash
cd backend-growfund
python manage.py runserver
```

Test deposit endpoint:
```bash
curl -X POST http://localhost:8000/api/transactions/korapay/deposit/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "phone_number": "+2348012345678",
    "payment_method": "mobile_money"
  }'
```

### 4. Available Endpoints

All endpoints are at `/api/transactions/korapay/`:

- `POST /deposit/` - Initialize deposit
- `POST /withdrawal/bank/` - Withdraw to bank
- `POST /withdrawal/mobile/` - Withdraw to mobile money
- `POST /verify/` - Verify transaction
- `GET /banks/?country=NG` - Get supported banks
- `POST /resolve-account/` - Verify bank account
- `POST /webhook/` - Webhook handler (for Korapay)

### 5. Configure Webhook

1. Go to Korapay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://your-backend-url.com/api/transactions/korapay/webhook/`
3. Select events:
   - charge.success
   - charge.failed
   - transfer.success
   - transfer.failed

### 6. Supported Countries & Currencies

- 🇳🇬 Nigeria (NGN)
- 🇬🇭 Ghana (GHS)
- 🇰🇪 Kenya (KES)
- 🇺🇬 Uganda (UGX)
- 🇹🇿 Tanzania (TZS)

To change currency, update in `korapay_views.py`:
```python
currency='NGN'  # Change to GHS, KES, UGX, etc.
```

## Common Issues

### Issue: "KORAPAY_SECRET_KEY not set"
**Solution:** Add the keys to your `.env` file

### Issue: "Invalid API key"
**Solution:** Make sure you're using the correct environment (test vs live)

### Issue: "Webhook not receiving events"
**Solution:** 
- Check webhook URL is publicly accessible
- Verify webhook is configured in Korapay dashboard
- Check webhook signature verification

## Testing

### Test Cards (Sandbox)
- Success: `5060990580000217999` (CVV: 123)
- Insufficient Funds: `5060990580000217998`
- Declined: `5060990580000217997`

### Test Phone Numbers
Use any valid phone number format for your country

## Production Checklist

- [ ] Get live API keys from Korapay
- [ ] Update environment variables with live keys
- [ ] Change `KORAPAY_BASE_URL` if needed
- [ ] Configure webhook URL
- [ ] Test with small real transactions
- [ ] Set up error monitoring
- [ ] Configure transaction limits
- [ ] Enable 2FA on Korapay dashboard

## Support

- Full Guide: `KORAPAY-SETUP-GUIDE.md`
- Korapay Docs: https://docs.korapay.com/
- Support: support@korapay.com
