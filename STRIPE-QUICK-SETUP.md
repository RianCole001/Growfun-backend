# Stripe Card Integration - Quick Setup (30 Minutes)

## ⚡ 5-Step Quick Start

### Step 1: Create Stripe Account (5 min)
```bash
# Go to https://stripe.com
# Sign up for free
# Get API keys from Dashboard → API Keys
# Copy Publishable Key (pk_test_...)
# Copy Secret Key (sk_test_...)
```

### Step 2: Backend Setup (10 min)

```bash
# Install Stripe
cd backend-growfund
pip install stripe

# Create payments app
python manage.py startapp payments

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    ...
    'payments',
]

# Update .env
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Run migrations
python manage.py makemigrations payments
python manage.py migrate payments
```

### Step 3: Frontend Setup (5 min)

```bash
# Install Stripe React
cd Growfund-Dashboard/trading-dashboard
npm install @stripe/react-stripe-js @stripe/js

# Update .env
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key
```

### Step 4: Copy Code Files (5 min)

Copy these files from STRIPE-CARD-INTEGRATION.md:
- Backend: models.py, views.py, urls.py
- Frontend: DepositCard.js component

### Step 5: Test (5 min)

```bash
# Restart servers
# Test with card: 4242 4242 4242 4242
# Expiry: 12/25, CVC: 123
```

---

## 📝 Files to Create/Update

### Backend Files

**1. `backend-growfund/payments/models.py`**
- Payment model
- Deposit model

**2. `backend-growfund/payments/views.py`**
- StripePaymentViewSet
- stripe_webhook function

**3. `backend-growfund/payments/urls.py`**
- Payment routes
- Webhook route

**4. `backend-growfund/growfund/settings.py`**
- Add 'payments' to INSTALLED_APPS
- Add Stripe configuration

**5. `backend-growfund/growfund/urls.py`**
- Add payments URLs

### Frontend Files

**1. `Growfund-Dashboard/trading-dashboard/src/components/DepositCard.js`**
- Card payment form
- Stripe integration

**2. `Growfund-Dashboard/trading-dashboard/.env`**
- Add REACT_APP_STRIPE_PUBLIC_KEY

**3. Dashboard component**
- Import and use DepositCard

---

## 🧪 Test Cards

```
✅ Success
Card: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123

❌ Decline
Card: 4000 0000 0000 0002
Expiry: 12/25
CVC: 123
```

---

## 🔄 Payment Flow

```
1. User enters amount
   ↓
2. Frontend creates payment intent
   ↓
3. User enters card details
   ↓
4. Frontend confirms payment
   ↓
5. Backend verifies payment
   ↓
6. Balance updated
   ↓
7. Success message shown
```

---

## ✅ Checklist

- [ ] Create Stripe account
- [ ] Get API keys
- [ ] Install backend packages
- [ ] Create payments app
- [ ] Copy backend files
- [ ] Update settings.py
- [ ] Run migrations
- [ ] Install frontend packages
- [ ] Copy DepositCard component
- [ ] Update .env
- [ ] Add to dashboard
- [ ] Test with sandbox cards
- [ ] Restart servers

---

## 🚀 API Endpoints

### Create Payment Intent
```
POST /api/payments/stripe/create_payment_intent/
Body: { "amount": 100 }
```

### Confirm Payment
```
POST /api/payments/stripe/confirm_payment/
Body: { "payment_intent_id": "pi_..." }
```

---

## 📊 What Users Get

✅ Real card deposits
✅ Instant balance updates
✅ Transaction history
✅ Secure payment processing
✅ Multiple card support

---

## 🎯 Next Steps

1. Read STRIPE-CARD-INTEGRATION.md for detailed guide
2. Create Stripe account
3. Get API keys
4. Follow the 5 steps above
5. Test with sandbox cards
6. Deploy to production

---

## 💡 Pro Tips

1. **Test First** - Always test with sandbox cards
2. **Webhooks** - Set up webhooks for production
3. **HTTPS** - Required for production
4. **Error Handling** - Show user-friendly error messages
5. **Monitoring** - Monitor Stripe dashboard for issues

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Check .env has correct keys |
| "Card declined" | Use test card 4242 4242 4242 4242 |
| "CORS error" | Check CORS_ALLOWED_ORIGINS |
| "Payment failed" | Check Stripe dashboard for errors |

---

## ✨ You're Ready!

Real card deposits are now integrated! 🎉

See STRIPE-CARD-INTEGRATION.md for complete details.
