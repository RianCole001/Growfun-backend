# Payment Integration Guide - PayPal & Card Deposits

## 🎯 Overview

To integrate PayPal and card payments, you'll need:

1. **Backend Payment Processing**
   - Payment gateway integration (Stripe for cards, PayPal SDK)
   - Payment models and database schema
   - API endpoints for payment processing
   - Webhook handlers for payment confirmations

2. **Frontend Payment UI**
   - Payment method selection
   - Deposit form
   - Payment processing modal
   - Success/failure handling

3. **Third-Party Services**
   - Stripe account (for card payments)
   - PayPal Developer account (for PayPal payments)
   - API keys and credentials

---

## 📋 Step 1: Set Up Third-Party Accounts

### PayPal Setup
1. Go to https://developer.paypal.com
2. Create a Business account
3. Create an app in Sandbox mode
4. Get your:
   - Client ID
   - Secret Key
   - Webhook URL

### Stripe Setup
1. Go to https://stripe.com
2. Create an account
3. Get your:
   - Publishable Key
   - Secret Key
4. Set up webhook endpoint

---

## 🔧 Step 2: Backend Implementation

### 2.1 Install Required Packages

```bash
cd backend-growfund
pip install stripe paypalrestsdk django-cors-headers
```

### 2.2 Create Payment Models

Create `backend-growfund/payments/models.py`:

```python
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction IDs
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    reference_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
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
    
    # Deposit details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - Deposit ${self.amount}"
```

### 2.3 Create Payment Serializers

Create `backend-growfund/payments/serializers.py`:

```python
from rest_framework import serializers
from .models import Payment, Deposit

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'payment_method', 'status',
            'transaction_id', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'created_at', 'completed_at']


class CreatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=['paypal', 'stripe'])
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        if value < 10:
            raise serializers.ValidationError("Minimum deposit is $10")
        if value > 100000:
            raise serializers.ValidationError("Maximum deposit is $100,000")
        return value


class DepositSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Deposit
        fields = ['id', 'amount', 'balance_before', 'balance_after', 'payment', 'created_at']
        read_only_fields = ['id', 'balance_before', 'balance_after', 'created_at']
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
import paypalrestsdk
from .models import Payment, Deposit
from .serializers import PaymentSerializer, CreatePaymentSerializer, DepositSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_paypal_payment(self, request):
        """Create PayPal payment"""
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{settings.FRONTEND_URL}/payment/success",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": f"Deposit ${amount} to GrowFund account"
            }]
        })
        
        if payment.create():
            # Save payment record
            payment_obj = Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_method='paypal',
                status='pending',
                reference_id=payment.id
            )
            
            # Get approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return Response({
                'payment_id': payment_obj.id,
                'approval_url': approval_url,
                'reference_id': payment.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': payment.error['message']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def create_stripe_payment(self, request):
        """Create Stripe payment intent"""
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                metadata={
                    "user_id": request.user.id,
                    "user_email": request.user.email
                }
            )
            
            # Save payment record
            payment_obj = Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_method='stripe',
                status='pending',
                reference_id=intent.id
            )
            
            return Response({
                'payment_id': payment_obj.id,
                'client_secret': intent.client_secret,
                'reference_id': intent.id
            }, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def confirm_paypal_payment(self, request):
        """Confirm PayPal payment after user approval"""
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')
        
        try:
            payment_obj = Payment.objects.get(id=payment_id, user=request.user)
            
            # Execute PayPal payment
            payment = paypalrestsdk.Payment.find(payment_obj.reference_id)
            
            if payment.execute({"payer_id": payer_id}):
                # Update payment status
                payment_obj.status = 'completed'
                payment_obj.transaction_id = payment.id
                payment_obj.completed_at = timezone.now()
                payment_obj.save()
                
                # Create deposit and update user balance
                user_profile = request.user.userprofile
                balance_before = user_profile.balance
                user_profile.balance += payment_obj.amount
                user_profile.save()
                
                Deposit.objects.create(
                    user=request.user,
                    payment=payment_obj,
                    amount=payment_obj.amount,
                    balance_before=balance_before,
                    balance_after=user_profile.balance
                )
                
                return Response({
                    'status': 'success',
                    'message': f'Deposit of ${payment_obj.amount} completed',
                    'new_balance': user_profile.balance
                })
            else:
                payment_obj.status = 'failed'
                payment_obj.save()
                return Response({
                    'error': payment.error['message']
                }, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def confirm_stripe_payment(self, request):
        """Confirm Stripe payment"""
        payment_id = request.data.get('payment_id')
        
        try:
            payment_obj = Payment.objects.get(id=payment_id, user=request.user)
            
            # Retrieve payment intent
            intent = stripe.PaymentIntent.retrieve(payment_obj.reference_id)
            
            if intent.status == 'succeeded':
                # Update payment status
                payment_obj.status = 'completed'
                payment_obj.transaction_id = intent.charges.data[0].id
                payment_obj.completed_at = timezone.now()
                payment_obj.save()
                
                # Create deposit and update user balance
                user_profile = request.user.userprofile
                balance_before = user_profile.balance
                user_profile.balance += payment_obj.amount
                user_profile.save()
                
                Deposit.objects.create(
                    user=request.user,
                    payment=payment_obj,
                    amount=payment_obj.amount,
                    balance_before=balance_before,
                    balance_after=user_profile.balance
                )
                
                return Response({
                    'status': 'success',
                    'message': f'Deposit of ${payment_obj.amount} completed',
                    'new_balance': user_profile.balance
                })
            else:
                payment_obj.status = 'failed'
                payment_obj.save()
                return Response({
                    'error': 'Payment not completed'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)


class DepositViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user)
```

### 2.5 Update Settings

Add to `backend-growfund/growfund/settings.py`:

```python
# Payment Gateway Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', '')

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'payments',
]
```

### 2.6 Update URLs

Add to `backend-growfund/growfund/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, DepositViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'deposits', DepositViewSet, basename='deposit')

urlpatterns = [
    ...
    path('api/', include(router.urls)),
]
```

### 2.7 Update .env

Add to `backend-growfund/.env`:

```
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here

PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here

FRONTEND_URL=http://localhost:3000
```

---

## 🎨 Step 3: Frontend Implementation

### 3.1 Create Deposit Component

Create `Growfund-Dashboard/trading-dashboard/src/components/Deposit.js`:

```javascript
import React, { useState } from 'react';
import { CreditCard, DollarSign, Loader } from 'lucide-react';
import { loadStripe } from '@stripe/js';
import { CardElement, Elements, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

export default function Deposit({ balance = 0, onDepositSuccess = () => {} }) {
  const [amount, setAmount] = useState(100);
  const [paymentMethod, setPaymentMethod] = useState('stripe');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDeposit = async () => {
    setLoading(true);
    setError('');

    try {
      if (paymentMethod === 'paypal') {
        // PayPal flow
        const response = await fetch('/api/payments/create_paypal_payment/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ amount, payment_method: 'paypal' })
        });

        const data = await response.json();
        if (data.approval_url) {
          window.location.href = data.approval_url;
        }
      } else {
        // Stripe flow
        const response = await fetch('/api/payments/create_stripe_payment/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ amount, payment_method: 'stripe' })
        });

        const data = await response.json();
        // Handle Stripe payment (requires Stripe Elements)
        console.log('Stripe payment intent created:', data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg text-white">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <DollarSign className="w-6 h-6 mr-2" />
        Deposit Funds
      </h2>

      <div className="space-y-4">
        {/* Amount Input */}
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

        {/* Payment Method Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">Payment Method</label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setPaymentMethod('stripe')}
              className={`p-3 rounded border-2 transition ${
                paymentMethod === 'stripe'
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-600 bg-gray-700'
              }`}
            >
              <CreditCard className="w-5 h-5 mx-auto mb-1" />
              <span className="text-sm">Card</span>
            </button>
            <button
              onClick={() => setPaymentMethod('paypal')}
              className={`p-3 rounded border-2 transition ${
                paymentMethod === 'paypal'
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-600 bg-gray-700'
              }`}
            >
              <span className="text-sm">PayPal</span>
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500 p-3 rounded text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Deposit Button */}
        <button
          onClick={handleDeposit}
          disabled={loading || amount < 10}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 p-3 rounded font-semibold flex items-center justify-center gap-2"
        >
          {loading && <Loader className="w-4 h-4 animate-spin" />}
          Deposit ${amount}
        </button>
      </div>
    </div>
  );
}
```

### 3.2 Install Frontend Dependencies

```bash
cd Growfund-Dashboard/trading-dashboard
npm install @stripe/stripe-js @stripe/react-stripe-js
```

---

## 🔗 Step 4: Webhook Handlers

### 4.1 Stripe Webhook

Add to `backend-growfund/payments/views.py`:

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

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
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Handle successful payment
        
    return JsonResponse({'status': 'success'})
```

---

## 📝 API Endpoints

### Create PayPal Payment
```
POST /api/payments/create_paypal_payment/
{
  "amount": 100,
  "payment_method": "paypal"
}
```

### Create Stripe Payment
```
POST /api/payments/create_stripe_payment/
{
  "amount": 100,
  "payment_method": "stripe"
}
```

### Confirm PayPal Payment
```
POST /api/payments/confirm_paypal_payment/
{
  "payment_id": "uuid",
  "payer_id": "paypal_payer_id"
}
```

### Confirm Stripe Payment
```
POST /api/payments/confirm_stripe_payment/
{
  "payment_id": "uuid"
}
```

### List Deposits
```
GET /api/deposits/
```

---

## ✅ Checklist

- [ ] Create PayPal Developer account
- [ ] Create Stripe account
- [ ] Install backend packages (stripe, paypalrestsdk)
- [ ] Create payments app
- [ ] Create Payment and Deposit models
- [ ] Create serializers and views
- [ ] Update settings.py with API keys
- [ ] Create payment URLs
- [ ] Update .env with credentials
- [ ] Install frontend packages (@stripe/stripe-js)
- [ ] Create Deposit component
- [ ] Test PayPal flow
- [ ] Test Stripe flow
- [ ] Set up webhooks
- [ ] Test deposit balance updates

---

## 🚀 Testing

### Test PayPal (Sandbox)
1. Use sandbox credentials
2. Test account: sb-xxxxx@personal.example.com
3. Password: 123456

### Test Stripe (Test Mode)
1. Card: 4242 4242 4242 4242
2. Expiry: 12/25
3. CVC: 123

---

## 📚 Resources

- [Stripe Documentation](https://stripe.com/docs)
- [PayPal SDK Documentation](https://developer.paypal.com/docs)
- [Django REST Framework](https://www.django-rest-framework.org)
- [React Stripe Elements](https://stripe.com/docs/stripe-js/react)
