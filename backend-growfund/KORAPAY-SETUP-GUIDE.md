# Korapay Integration Guide

## Overview
Korapay integration supports:
- **Deposits**: Mobile Money, Bank Transfer, Cards
- **Withdrawals**: Bank accounts, Mobile Money
- **Multi-country**: Nigeria, Ghana, Kenya, Uganda, and more
- **Webhooks**: Automatic payment notifications

## Step 1: Get Korapay API Keys

1. Go to [Korapay Dashboard](https://dashboard.korapay.com/)
2. Sign up and complete KYC
3. Navigate to Settings → API Keys
4. Copy your:
   - **Public Key** (for frontend)
   - **Secret Key** (for backend)
   - **Encryption Key** (optional)

## Step 2: Configure Environment Variables

Add to `.env` or Back4app environment variables:

```env
# Korapay Configuration
KORAPAY_BASE_URL=https://api.korapay.com/merchant/api/v1
KORAPAY_SECRET_KEY=sk_test_your_secret_key_here
KORAPAY_PUBLIC_KEY=pk_test_your_public_key_here
KORAPAY_ENCRYPTION_KEY=your_encryption_key_here
KORAPAY_WEBHOOK_URL=https://your-backend-url.com/api/transactions/korapay/webhook/
```

### For Production
Change to live keys:
- `sk_live_...` for secret key
- `pk_live_...` for public key

## Step 3: API Endpoints

### 1. Deposit Money
```
POST /api/transactions/korapay/deposit/
Authorization: Bearer <access_token>

{
  "amount": 10000,
  "phone_number": "+2348012345678",
  "payment_method": "mobile_money"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment initialized successfully",
  "transaction_id": 123,
  "reference": "DEP-ABC123XYZ",
  "checkout_url": "https://checkout.korapay.com/...",
  "authorization_url": "https://...",
  "amount": "10000.00"
}
```

### 2. Withdraw to Bank Account
```
POST /api/transactions/korapay/withdrawal/bank/
Authorization: Bearer <access_token>

{
  "amount": 5000,
  "account_number": "0123456789",
  "bank_code": "058",
  "account_name": "John Doe"
}
```

### 3. Withdraw to Mobile Money
```
POST /api/transactions/korapay/withdrawal/mobile/
Authorization: Bearer <access_token>

{
  "amount": 5000,
  "phone_number": "+2348012345678",
  "provider": "mtn"
}
```

### 4. Verify Transaction
```
POST /api/transactions/korapay/verify/
Authorization: Bearer <access_token>

{
  "reference": "DEP-ABC123XYZ"
}
```

### 5. Get Supported Banks
```
GET /api/transactions/korapay/banks/?country=NG
Authorization: Bearer <access_token>
```

**Countries:**
- `NG` - Nigeria
- `GH` - Ghana
- `KE` - Kenya
- `UG` - Uganda
- `TZ` - Tanzania

### 6. Verify Bank Account
```
POST /api/transactions/korapay/resolve-account/
Authorization: Bearer <access_token>

{
  "account_number": "0123456789",
  "bank_code": "058"
}
```

**Response:**
```json
{
  "success": true,
  "account_name": "JOHN DOE",
  "account_number": "0123456789",
  "bank_code": "058"
}
```

## Step 4: Webhook Setup

1. Go to Korapay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://your-backend-url.com/api/transactions/korapay/webhook/`
3. Select events:
   - `charge.success`
   - `charge.failed`
   - `transfer.success`
   - `transfer.failed`

## Step 5: Currency Configuration

Update currency in `korapay_views.py`:

```python
currency='NGN'  # Nigeria Naira
# or
currency='GHS'  # Ghana Cedis
# or
currency='KES'  # Kenya Shillings
# or
currency='UGX'  # Uganda Shillings
```

## Supported Payment Methods

### Deposits
- **Mobile Money**: MTN, Airtel, Vodafone, Tigo, etc.
- **Bank Transfer**: All major banks
- **Cards**: Visa, Mastercard, Verve

### Withdrawals
- **Bank Transfer**: All supported banks
- **Mobile Money**: MTN, Airtel, Vodafone, etc.

## Testing

### Test Cards (Sandbox)
- **Success**: `5060990580000217999` (CVV: 123, Expiry: any future date)
- **Insufficient Funds**: `5060990580000217998`
- **Declined**: `5060990580000217997`

### Test Mobile Money
Use any valid phone number format for your country

### Test Bank Accounts
Use any valid account number with correct bank code

## Common Bank Codes (Nigeria)

| Bank | Code |
|------|------|
| GTBank | 058 |
| Access Bank | 044 |
| Zenith Bank | 057 |
| First Bank | 011 |
| UBA | 033 |
| Ecobank | 050 |

Get full list via `/api/transactions/korapay/banks/` endpoint

## Error Handling

### Common Errors
- `insufficient_funds` - User has insufficient balance
- `invalid_account` - Bank account doesn't exist
- `transaction_limit_exceeded` - Amount exceeds limits
- `duplicate_reference` - Reference already used

## Security Best Practices

1. Never expose secret key in frontend
2. Verify webhook signatures
3. Use HTTPS in production
4. Validate all user inputs
5. Set transaction limits
6. Monitor for suspicious activity

## Production Checklist

- [ ] Get live API keys from Korapay
- [ ] Update environment variables with live keys
- [ ] Configure webhook URL
- [ ] Test with real transactions (small amounts)
- [ ] Set up proper error logging
- [ ] Configure transaction limits
- [ ] Enable 2FA on Korapay dashboard
- [ ] Set up balance alerts
- [ ] Test webhook handling
- [ ] Document customer support process

## Advantages over MTN MoMo

✅ Single API for multiple countries  
✅ Supports multiple payment methods  
✅ Better documentation  
✅ Easier integration  
✅ Unified webhook system  
✅ Bank transfers included  
✅ Card payments supported  
✅ Better error handling  
✅ Account verification built-in  

## Support

- Documentation: https://docs.korapay.com/
- Support: support@korapay.com
- Dashboard: https://dashboard.korapay.com/
