# Payment Integration - File Structure

## 📁 Backend Files to Create/Modify

```
backend-growfund/
├── payments/                          # NEW APP
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py           # Auto-generated
│   ├── __init__.py
│   ├── admin.py                       # Register models in admin
│   ├── apps.py
│   ├── models.py                      # Payment & Deposit models
│   ├── serializers.py                 # Payment serializers
│   ├── views.py                       # Payment viewsets
│   ├── urls.py                        # Payment URLs
│   └── tests.py
├── growfund/
│   ├── settings.py                    # MODIFY: Add payment config
│   ├── urls.py                        # MODIFY: Add payment URLs
│   └── wsgi.py
├── .env                               # MODIFY: Add API keys
└── requirements.txt                   # MODIFY: Add stripe, paypalrestsdk
```

## 📁 Frontend Files to Create/Modify

```
Growfund-Dashboard/trading-dashboard/src/
├── components/
│   ├── Deposit.js                     # NEW: Deposit component
│   ├── Dashboard.js                   # MODIFY: Add Deposit component
│   └── ...
├── pages/
│   ├── PaymentSuccess.js              # NEW: Success page
│   ├── PaymentCancel.js               # NEW: Cancel page
│   └── ...
├── .env                               # MODIFY: Add Stripe public key
└── package.json                       # MODIFY: Add stripe packages
```

---

## 📝 File Contents Summary

### Backend Files

#### 1. `payments/models.py`
```python
- Payment model (payment records)
- Deposit model (deposit records)
```

#### 2. `payments/serializers.py`
```python
- PaymentSerializer
- CreatePaymentSerializer
- DepositSerializer
```

#### 3. `payments/views.py`
```python
- PaymentViewSet
  - create_paypal_payment()
  - create_stripe_payment()
  - confirm_paypal_payment()
  - confirm_stripe_payment()
- DepositViewSet
- stripe_webhook()
- paypal_webhook()
```

#### 4. `payments/urls.py`
```python
- router.register('payments', PaymentViewSet)
- router.register('deposits', DepositViewSet)
- path('webhooks/stripe/', stripe_webhook)
- path('webhooks/paypal/', paypal_webhook)
```

#### 5. `payments/admin.py`
```python
- Register Payment model
- Register Deposit model
```

#### 6. `growfund/settings.py` (MODIFICATIONS)
```python
- Add 'payments' to INSTALLED_APPS
- Add STRIPE_PUBLIC_KEY
- Add STRIPE_SECRET_KEY
- Add STRIPE_WEBHOOK_SECRET
- Add PAYPAL_MODE
- Add PAYPAL_CLIENT_ID
- Add PAYPAL_CLIENT_SECRET
- Add FRONTEND_URL
```

#### 7. `growfund/urls.py` (MODIFICATIONS)
```python
- Include payments URLs
- Include payment webhooks
```

#### 8. `.env` (MODIFICATIONS)
```
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
FRONTEND_URL=http://localhost:3000
```

#### 9. `requirements.txt` (MODIFICATIONS)
```
stripe==5.x.x
paypalrestsdk==1.x.x
```

---

### Frontend Files

#### 1. `components/Deposit.js` (NEW)
```javascript
- Deposit component
- Amount input
- Payment method selection (PayPal/Stripe)
- Deposit button
- Error handling
- Loading state
```

#### 2. `pages/PaymentSuccess.js` (NEW)
```javascript
- Success page after payment
- Show confirmation message
- Display transaction details
- Redirect to dashboard
```

#### 3. `pages/PaymentCancel.js` (NEW)
```javascript
- Cancel page if user cancels payment
- Show cancellation message
- Redirect to deposit page
```

#### 4. `components/Dashboard.js` (MODIFICATIONS)
```javascript
- Import Deposit component
- Add Deposit component to dashboard
- Pass balance and onDepositSuccess props
```

#### 5. `.env` (MODIFICATIONS)
```
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_...
REACT_APP_PAYPAL_CLIENT_ID=...
```

#### 6. `package.json` (MODIFICATIONS)
```json
- Add @stripe/stripe-js
- Add @stripe/react-stripe-js
```

---

## 🔄 Data Flow

### Payment Creation Flow
```
Frontend (Deposit.js)
    ↓
POST /api/payments/create_paypal_payment/
    ↓
Backend (PaymentViewSet.create_paypal_payment)
    ↓
Create Payment record (status: pending)
    ↓
Create PayPal payment
    ↓
Return approval_url
    ↓
Frontend redirects to PayPal
    ↓
User approves payment
    ↓
PayPal redirects back to app
```

### Payment Confirmation Flow
```
Frontend (PaymentSuccess.js)
    ↓
POST /api/payments/confirm_paypal_payment/
    ↓
Backend (PaymentViewSet.confirm_paypal_payment)
    ↓
Verify payment with PayPal
    ↓
Update Payment record (status: completed)
    ↓
Create Deposit record
    ↓
Update user balance
    ↓
Return success response
    ↓
Frontend shows success message
```

---

## 🗄️ Database Schema

### Payment Table
```sql
CREATE TABLE payments_payment (
    id UUID PRIMARY KEY,
    user_id INT FOREIGN KEY,
    amount DECIMAL(12, 2),
    currency VARCHAR(3),
    payment_method VARCHAR(20),
    status VARCHAR(20),
    transaction_id VARCHAR(255),
    reference_id VARCHAR(255),
    created_at DATETIME,
    completed_at DATETIME,
    updated_at DATETIME
);
```

### Deposit Table
```sql
CREATE TABLE payments_deposit (
    id UUID PRIMARY KEY,
    user_id INT FOREIGN KEY,
    payment_id UUID FOREIGN KEY,
    amount DECIMAL(12, 2),
    balance_before DECIMAL(12, 2),
    balance_after DECIMAL(12, 2),
    created_at DATETIME
);
```

---

## 🔐 Environment Variables

### Backend (.env)
```
# Stripe
STRIPE_PUBLIC_KEY=pk_test_51234567890...
STRIPE_SECRET_KEY=sk_test_51234567890...
STRIPE_WEBHOOK_SECRET=whsec_1234567890...

# PayPal
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AXxxx...
PAYPAL_CLIENT_SECRET=EJxxx...

# Frontend
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)
```
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_51234567890...
REACT_APP_PAYPAL_CLIENT_ID=AXxxx...
REACT_APP_API_URL=http://localhost:8000
```

---

## 📦 Dependencies

### Backend
```
stripe==5.x.x
paypalrestsdk==1.x.x
django-cors-headers==4.x.x
```

### Frontend
```
@stripe/stripe-js
@stripe/react-stripe-js
```

---

## 🚀 Deployment Checklist

- [ ] Create payments app
- [ ] Create models
- [ ] Create serializers
- [ ] Create views
- [ ] Create URLs
- [ ] Update settings.py
- [ ] Update .env
- [ ] Run migrations
- [ ] Create Deposit component
- [ ] Create success/cancel pages
- [ ] Update Dashboard component
- [ ] Test PayPal flow
- [ ] Test Stripe flow
- [ ] Set up webhooks
- [ ] Deploy to production

---

## 📞 Quick Reference

### Create Payment
```bash
POST /api/payments/create_paypal_payment/
POST /api/payments/create_stripe_payment/
```

### Confirm Payment
```bash
POST /api/payments/confirm_paypal_payment/
POST /api/payments/confirm_stripe_payment/
```

### List Deposits
```bash
GET /api/deposits/
```

### List Payments
```bash
GET /api/payments/
```

---

## 💡 Tips

1. **Start Simple**: Implement one payment method first (Stripe), then add PayPal
2. **Test Thoroughly**: Use sandbox credentials for testing
3. **Error Handling**: Handle all error cases gracefully
4. **Security**: Never store card details, use tokenization
5. **Monitoring**: Log all payment transactions for debugging

---

## 🎯 Next Steps

1. Create the payments app
2. Create models and migrations
3. Create serializers and views
4. Update settings and URLs
5. Create frontend components
6. Test with sandbox credentials
7. Deploy to production

Good luck! 🚀
