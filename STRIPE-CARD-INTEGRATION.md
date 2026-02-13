# Stripe Card Integration - Real Debit/Credit Card Deposits

## 🎯 Overview

Integrate Stripe to accept real debit/credit card payments for deposits. Users can deposit funds directly using their cards.

---

## 📋 Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Sign up for free account
3. Go to Dashboard → API Keys
4. Copy:
   - **Publishable Key** (starts with `pk_`)
   - **Secret Key** (starts with `sk_`)

---

## 🔧 Step 2: Backend Setup

### 2.1 Install Stripe Package

```bash
cd backend-growfund
pip install stripe
```

### 2.2 Update .env

```
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 2.3 Update settings.py

Add to `backend-growfund/growfund/settings.py`:

```python
import os

# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
```

### 2.4 Create Payment Views

Create `backend-growfund/payments/views.py`:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        """Create Stripe payment intent for card payment"""
        try:
            amount = request.data.get('amount')
            
            if not amount or amount < 10:
                return Response(
                    {'error': 'Minimum deposit is $10'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if amount > 100000:
                return Response(
                    {'error': 'Maximum deposit is $100,000'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'user_id': request.user.id,
                    'user_email': request.user.email,
                    'deposit_amount': amount
                }
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm payment and update user balance"""
        try:
            payment_intent_id = request.data.get('payment_intent_id')
            
            # Retrieve payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status != 'succeeded':
                return Response(
                    {'error': 'Payment not completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get deposit amount from metadata
            amount = float(intent.metadata.get('deposit_amount', 0))
            
            # Update user balance
            user_profile = request.user.userprofile
            balance_before = user_profile.balance
            user_profile.balance += amount
            user_profile.save()
            
            # Create deposit record
            from .models import Deposit, Payment
            
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_method='stripe',
                status='completed',
                transaction_id=intent.charges.data[0].id if intent.charges.data else intent.id,
                reference_id=payment_intent_id
            )
            
            Deposit.objects.create(
                user=request.user,
                payment=payment,
                amount=amount,
                balance_before=balance_before,
                balance_after=user_profile.balance
            )
            
            return Response({
                'status': 'success',
                'message': f'Deposit of ${amount} completed successfully',
                'new_balance': float(user_profile.balance),
                'transaction_id': payment.id
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Payment already handled in confirm_payment
        pass
    
    # Handle payment_intent.payment_failed event
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Handle failed payment
        pass
    
    return JsonResponse({'status': 'success'})
```

### 2.5 Create Payment Models

Create `backend-growfund/payments/models.py`:

```python
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe Card'),
        ('paypal', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    reference_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"


class Deposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='deposit')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - Deposit ${self.amount}"
```

### 2.6 Create URLs

Create `backend-growfund/payments/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StripePaymentViewSet, stripe_webhook

router = DefaultRouter()
router.register(r'stripe', StripePaymentViewSet, basename='stripe-payment')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
```

### 2.7 Update Main URLs

Add to `backend-growfund/growfund/urls.py`:

```python
path('api/payments/', include('payments.urls')),
```

### 2.8 Create Payments App

```bash
cd backend-growfund
python manage.py startapp payments
```

### 2.9 Add to INSTALLED_APPS

Update `backend-growfund/growfund/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'payments',
]
```

### 2.10 Run Migrations

```bash
python manage.py makemigrations payments
python manage.py migrate payments
```

---

## 🎨 Step 3: Frontend Setup

### 3.1 Install Stripe React Package

```bash
cd Growfund-Dashboard/trading-dashboard
npm install @stripe/react-stripe-js @stripe/js
```

### 3.2 Update .env

Add to `Growfund-Dashboard/trading-dashboard/.env`:

```
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_your_key_here
```

### 3.3 Create Deposit Component

Create `Growfund-Dashboard/trading-dashboard/src/components/DepositCard.js`:

```javascript
import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import { DollarSign, Loader, AlertCircle, CheckCircle } from 'lucide-react';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

function CardPaymentForm({ amount, onSuccess, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const token = localStorage.getItem('user_access_token');

      // Step 1: Create payment intent
      const intentResponse = await fetch(
        `${process.env.REACT_APP_API_URL}/payments/stripe/create_payment_intent/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ amount }),
        }
      );

      const intentData = await intentResponse.json();

      if (!intentResponse.ok) {
        throw new Error(intentData.error || 'Failed to create payment intent');
      }

      // Step 2: Confirm payment with card
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(
        intentData.client_secret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
            billing_details: {
              email: localStorage.getItem('user_email'),
            },
          },
        }
      );

      if (stripeError) {
        throw new Error(stripeError.message);
      }

      // Step 3: Confirm payment on backend
      const confirmResponse = await fetch(
        `${process.env.REACT_APP_API_URL}/payments/stripe/confirm_payment/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            payment_intent_id: paymentIntent.id,
          }),
        }
      );

      const confirmData = await confirmResponse.json();

      if (!confirmResponse.ok) {
        throw new Error(confirmData.error || 'Payment confirmation failed');
      }

      setSuccess(true);
      elements.getElement(CardElement).clear();
      onSuccess(confirmData);
    } catch (err) {
      setError(err.message);
      onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Card Details
        </label>
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#fff',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
              invalid: {
                color: '#fa755a',
              },
            },
          }}
          className="p-3 bg-gray-800 rounded"
        />
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500 p-3 rounded flex items-center gap-2 text-red-400">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-500/10 border border-green-500 p-3 rounded flex items-center gap-2 text-green-400">
          <CheckCircle className="w-5 h-5" />
          Deposit successful! Your balance has been updated.
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || loading || success}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 p-3 rounded font-semibold flex items-center justify-center gap-2 text-white"
      >
        {loading && <Loader className="w-4 h-4 animate-spin" />}
        {success ? 'Deposit Completed' : `Deposit $${amount}`}
      </button>
    </form>
  );
}

export default function DepositCard({ balance = 0, onDepositSuccess = () => {} }) {
  const [amount, setAmount] = useState(100);
  const [showForm, setShowForm] = useState(false);

  const handleSuccess = (data) => {
    onDepositSuccess(data);
    setTimeout(() => {
      setShowForm(false);
      setAmount(100);
    }, 2000);
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg text-white">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <DollarSign className="w-6 h-6 mr-2" />
        Deposit with Card
      </h2>

      {!showForm ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Amount (USD)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              min="10"
              max="100000"
              className="w-full bg-gray-700 rounded p-3 text-white"
              placeholder="Enter amount"
            />
            <p className="text-xs text-gray-400 mt-1">Min: $10 | Max: $100,000</p>
          </div>

          <div className="grid grid-cols-4 gap-2">
            {[50, 100, 500, 1000].map((val) => (
              <button
                key={val}
                onClick={() => setAmount(val)}
                className="bg-gray-700 hover:bg-blue-600 p-2 rounded text-sm font-bold transition"
              >
                ${val}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowForm(true)}
            className="w-full bg-green-600 hover:bg-green-700 p-3 rounded font-semibold"
          >
            Continue to Payment
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <Elements stripe={stripePromise}>
            <CardPaymentForm
              amount={amount}
              onSuccess={handleSuccess}
              onError={() => {}}
            />
          </Elements>

          <button
            onClick={() => setShowForm(false)}
            className="w-full bg-gray-700 hover:bg-gray-600 p-3 rounded font-semibold"
          >
            Back
          </button>
        </div>
      )}
    </div>
  );
}
```

### 3.4 Add to Dashboard

Update your dashboard component to include the deposit card:

```javascript
import DepositCard from './DepositCard';

// In your dashboard JSX
<DepositCard 
  balance={balance} 
  onDepositSuccess={(data) => {
    // Refresh balance
    fetchBalance();
    // Show success message
    showNotification('Deposit successful!');
  }}
/>
```

---

## 🧪 Step 4: Testing

### Test Cards (Stripe Sandbox)

```
Success:
Card: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123

Decline:
Card: 4000 0000 0000 0002
Expiry: 12/25
CVC: 123
```

### Test Flow

1. Open deposit component
2. Enter amount (e.g., $50)
3. Click "Continue to Payment"
4. Enter test card details
5. Click "Deposit $50"
6. Should see success message
7. Balance should update

---

## 🔐 Step 5: Security

### PCI Compliance

- ✅ Never store card details
- ✅ Use Stripe Elements (handles PCI)
- ✅ Use HTTPS only
- ✅ Validate on backend

### Environment Variables

```bash
# Never commit these!
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## 📊 API Endpoints

### Create Payment Intent
```
POST /api/payments/stripe/create_payment_intent/
{
  "amount": 100
}

Response:
{
  "client_secret": "pi_..._secret_...",
  "payment_intent_id": "pi_...",
  "amount": 100
}
```

### Confirm Payment
```
POST /api/payments/stripe/confirm_payment/
{
  "payment_intent_id": "pi_..."
}

Response:
{
  "status": "success",
  "message": "Deposit of $100 completed successfully",
  "new_balance": 1100,
  "transaction_id": "uuid"
}
```

---

## 📋 Checklist

- [ ] Create Stripe account
- [ ] Get API keys
- [ ] Install backend packages
- [ ] Create payments app
- [ ] Create models
- [ ] Create views
- [ ] Create URLs
- [ ] Update settings.py
- [ ] Run migrations
- [ ] Install frontend packages
- [ ] Create DepositCard component
- [ ] Add to dashboard
- [ ] Test with sandbox cards
- [ ] Set up webhooks
- [ ] Go live with production keys

---

## 🚀 Production Deployment

1. Get live Stripe keys
2. Update .env with live keys
3. Set up webhook endpoint
4. Enable HTTPS
5. Test thoroughly
6. Deploy

---

## 📞 Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe React](https://stripe.com/docs/stripe-js/react)
- [Stripe Testing](https://stripe.com/docs/testing)

---

## ✨ You're Ready!

Users can now make real card deposits! 🎉
