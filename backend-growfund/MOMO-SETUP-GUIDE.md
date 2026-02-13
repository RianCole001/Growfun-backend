# MTN Mobile Money Integration Guide

## Overview
This integration supports:
- **Deposits** (Collection API) - Users can deposit money
- **Withdrawals** (Disbursement API) - Users can withdraw money
- **Status checking** - Check payment status
- **Webhooks** - Automatic status updates

## Step 1: Get MTN MoMo API Credentials

### For Sandbox (Testing)
1. Go to [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
2. Sign up and create an account
3. Subscribe to:
   - **Collection** product (for deposits)
   - **Disbursement** product (for withdrawals)
4. Get your subscription keys

### Create API User
```bash
# Use the MTN MoMo API to create an API user
# Or use their developer portal
```

## Step 2: Configure Environment Variables

Add these to your `.env` file or Back4app environment variables:

```env
# MTN MoMo Configuration
MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
MOMO_COLLECTION_SUBSCRIPTION_KEY=your_collection_key_here
MOMO_DISBURSEMENT_SUBSCRIPTION_KEY=your_disbursement_key_here
MOMO_API_USER=your_api_user_uuid
MOMO_API_KEY=your_api_key_here
MOMO_CALLBACK_URL=https://your-backend-url.com/api/transactions/momo/callback/
MOMO_ENVIRONMENT=sandbox
```

### For Production
Change:
- `MOMO_BASE_URL=https://momodeveloper.mtn.com`
- `MOMO_ENVIRONMENT=production`

## Step 3: Run Migrations

```bash
python manage.py makemigrations transactions
python manage.py migrate
```

## Step 4: API Endpoints

### Deposit Money
```
POST /api/transactions/momo/deposit/
Authorization: Bearer <access_token>

{
  "amount": 10000,
  "phone_number": "+256700000000"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment request sent. Please approve on your phone.",
  "transaction_id": 123,
  "reference": "DEP-ABC123XYZ",
  "momo_reference": "uuid-from-momo",
  "amount": "10000.00"
}
```

### Withdraw Money
```
POST /api/transactions/momo/withdrawal/
Authorization: Bearer <access_token>

{
  "amount": 5000,
  "phone_number": "+256700000000"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Withdrawal initiated successfully",
  "transaction_id": 124,
  "reference": "WTH-XYZ789ABC",
  "momo_reference": "uuid-from-momo",
  "amount": "5000.00",
  "fee": "100.00",
  "net_amount": "4900.00"
}
```

### Check Payment Status
```
POST /api/transactions/momo/status/
Authorization: Bearer <access_token>

{
  "reference_id": "uuid-from-momo"
}
```

**Response:**
```json
{
  "success": true,
  "status": "SUCCESSFUL",
  "transaction_status": "completed",
  "amount": "10000.00",
  "reference": "DEP-ABC123XYZ"
}
```

### List Transactions
```
GET /api/transactions/
Authorization: Bearer <access_token>
```

## Step 5: Testing

### Test Phone Numbers (Sandbox)
MTN provides test phone numbers for sandbox:
- `46733123450` - Will approve automatically
- `46733123451` - Will reject automatically
- `46733123452` - Will timeout

### Test Flow
1. User initiates deposit with test phone number
2. Check transaction status after a few seconds
3. Balance should be updated when status is SUCCESSFUL

## Step 6: Webhook Setup

Configure your callback URL in MTN MoMo dashboard:
```
https://your-backend-url.com/api/transactions/momo/callback/
```

This endpoint receives automatic notifications when payment status changes.

## Currency Configuration

Update currency in `momo_service.py`:
```python
'currency': 'UGX',  # Uganda Shillings
# or
'currency': 'GHS',  # Ghana Cedis
# or
'currency': 'ZAR',  # South African Rand
```

## Supported Countries
- Uganda (UGX)
- Ghana (GHS)
- South Africa (ZAR)
- Ivory Coast (XOF)
- Cameroon (XAF)
- Benin (XOF)
- Congo Brazzaville (XAF)
- Zambia (ZMW)
- Liberia (USD)
- eSwatini (SZL)

## Security Notes
1. Never commit API keys to git
2. Use environment variables
3. Enable HTTPS in production
4. Validate webhook signatures (implement in production)
5. Set up proper logging and monitoring

## Troubleshooting

### Error: "Failed to get access token"
- Check your API credentials
- Verify subscription keys are correct
- Ensure API user is created

### Error: "Payment request failed"
- Check phone number format
- Verify amount is within limits
- Check API user has sufficient permissions

### Payment stuck in "processing"
- Use status check endpoint
- Check MTN MoMo dashboard
- Verify webhook is configured

## Production Checklist
- [ ] Get production API credentials
- [ ] Update MOMO_BASE_URL to production
- [ ] Set MOMO_ENVIRONMENT=production
- [ ] Configure production callback URL
- [ ] Test with real phone numbers
- [ ] Set up monitoring and alerts
- [ ] Implement webhook signature verification
- [ ] Add rate limiting
- [ ] Set up proper error logging
