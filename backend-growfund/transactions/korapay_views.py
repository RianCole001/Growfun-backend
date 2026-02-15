from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import uuid
import json

from .models import Transaction
from .korapay_service import KorapayService
from .serializers import (
    MoMoDepositSerializer, MoMoWithdrawalSerializer, 
    CheckPaymentStatusSerializer
)

korapay = KorapayService()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def korapay_deposit(request):
    """
    Initialize Korapay deposit
    Supports: mobile_money, bank_transfer, card
    """
    serializer = MoMoDepositSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    amount = serializer.validated_data['amount']
    phone_number = serializer.validated_data.get('phone_number')
    payment_method = request.data.get('payment_method', 'mobile_money')
    
    # Generate unique reference
    reference = f"DEP-{uuid.uuid4().hex[:12].upper()}"
    
    # Create transaction record
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='deposit',
        payment_method='korapay',
        amount=amount,
        fee=Decimal('0'),
        net_amount=amount,
        status='pending',
        reference=reference,
        phone_number=phone_number,
        description=f"Korapay deposit of {amount}",
        metadata={'payment_method': payment_method}
    )
    
    # Initialize payment with Korapay
    result = korapay.charge_customer(
        amount=amount,
        customer_email=request.user.email,
        customer_name=f"{request.user.first_name} {request.user.last_name}",
        reference=reference,
        payment_method=payment_method,
        phone_number=phone_number,
        currency='NGN'  # Change based on your country
    )
    
    if result['success']:
        transaction.external_reference = result['reference']
        transaction.status = 'processing'
        transaction.metadata['checkout_url'] = result.get('checkout_url')
        transaction.metadata['authorization_url'] = result.get('authorization_url')
        transaction.save()
        
        return Response({
            'success': True,
            'message': 'Payment initialized successfully',
            'transaction_id': transaction.id,
            'reference': reference,
            'checkout_url': result.get('checkout_url'),
            'authorization_url': result.get('authorization_url'),
            'amount': str(amount)
        }, status=status.HTTP_200_OK)
    else:
        transaction.status = 'failed'
        transaction.save()
        
        return Response({
            'success': False,
            'message': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def korapay_withdrawal_bank(request):
    """
    Withdraw to bank account
    """
    amount = Decimal(request.data.get('amount', 0))
    account_number = request.data.get('account_number')
    bank_code = request.data.get('bank_code')
    account_name = request.data.get('account_name')
    
    if not all([amount, account_number, bank_code, account_name]):
        return Response({
            'success': False,
            'message': 'Missing required fields'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check balance
    if request.user.balance < amount:
        return Response({
            'success': False,
            'message': 'Insufficient balance'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate fee
    fee = amount * Decimal('0.02')
    net_amount = amount - fee
    
    # Generate reference
    reference = f"WTH-{uuid.uuid4().hex[:12].upper()}"
    
    # Create transaction
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='withdrawal',
        payment_method='korapay',
        amount=amount,
        fee=fee,
        net_amount=net_amount,
        status='pending',
        reference=reference,
        description=f"Bank withdrawal of {amount}",
        metadata={
            'account_number': account_number,
            'bank_code': bank_code,
            'account_name': account_name
        }
    )
    
    # Initiate disbursement
    result = korapay.disburse_funds(
        amount=net_amount,
        account_number=account_number,
        bank_code=bank_code,
        account_name=account_name,
        reference=reference,
        narration=f"Withdrawal from GrowFund",
        currency='NGN'
    )
    
    if result['success']:
        transaction.external_reference = result['reference']
        transaction.status = 'processing'
        transaction.save()
        
        # Deduct from user balance
        request.user.balance -= amount
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Withdrawal initiated successfully',
            'transaction_id': transaction.id,
            'reference': reference,
            'amount': str(amount),
            'fee': str(fee),
            'net_amount': str(net_amount)
        }, status=status.HTTP_200_OK)
    else:
        transaction.status = 'failed'
        transaction.save()
        
        return Response({
            'success': False,
            'message': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def korapay_withdrawal_mobile(request):
    """
    Withdraw to mobile money
    """
    serializer = MoMoWithdrawalSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    amount = serializer.validated_data['amount']
    phone_number = serializer.validated_data['phone_number']
    provider = request.data.get('provider', 'mtn')  # mtn, airtel, vodafone
    
    # Calculate fee
    fee = amount * Decimal('0.02')
    net_amount = amount - fee
    
    # Generate reference
    reference = f"WTH-{uuid.uuid4().hex[:12].upper()}"
    
    # Create transaction
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='withdrawal',
        payment_method='korapay',
        amount=amount,
        fee=fee,
        net_amount=net_amount,
        status='pending',
        reference=reference,
        phone_number=phone_number,
        description=f"Mobile money withdrawal of {amount}",
        metadata={'provider': provider}
    )
    
    # Initiate mobile money disbursement
    result = korapay.disburse_mobile_money(
        amount=net_amount,
        phone_number=phone_number,
        provider=provider,
        reference=reference,
        customer_name=f"{request.user.first_name} {request.user.last_name}",
        currency='NGN'
    )
    
    if result['success']:
        transaction.external_reference = result['reference']
        transaction.status = 'processing'
        transaction.save()
        
        # Deduct from user balance
        request.user.balance -= amount
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Withdrawal initiated successfully',
            'transaction_id': transaction.id,
            'reference': reference,
            'amount': str(amount),
            'fee': str(fee),
            'net_amount': str(net_amount)
        }, status=status.HTTP_200_OK)
    else:
        transaction.status = 'failed'
        transaction.save()
        
        return Response({
            'success': False,
            'message': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def korapay_verify_transaction(request):
    """
    Verify transaction status
    """
    reference = request.data.get('reference')
    
    if not reference:
        return Response({
            'success': False,
            'message': 'Reference is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find transaction
    try:
        transaction = Transaction.objects.get(reference=reference, user=request.user)
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify with Korapay
    result = korapay.verify_transaction(reference)
    
    if result['success']:
        korapay_status = result['status']
        
        # Update transaction based on status
        if korapay_status == 'success' and transaction.status != 'completed':
            transaction.status = 'completed'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # Credit user balance for deposits
            if transaction.transaction_type == 'deposit':
                request.user.balance += transaction.amount
                request.user.save()
        
        elif korapay_status == 'failed':
            transaction.status = 'failed'
            transaction.save()
            
            # Refund for failed withdrawals
            if transaction.transaction_type == 'withdrawal' and transaction.status == 'processing':
                request.user.balance += transaction.amount
                request.user.save()
        
        return Response({
            'success': True,
            'status': korapay_status,
            'transaction_status': transaction.status,
            'amount': str(result.get('amount', transaction.amount)),
            'reference': transaction.reference
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def korapay_webhook(request):
    """
    Webhook endpoint for Korapay notifications
    """
    # Verify webhook signature
    signature = request.headers.get('X-Korapay-Signature')
    payload = request.body.decode('utf-8')
    
    if not korapay.verify_webhook_signature(payload, signature):
        return Response({'success': False}, status=status.HTTP_401_UNAUTHORIZED)
    
    data = json.loads(payload)
    event_type = data.get('event')
    event_data = data.get('data', {})
    
    reference = event_data.get('reference')
    
    try:
        transaction = Transaction.objects.get(reference=reference)
        
        if event_type == 'charge.success':
            if transaction.status != 'completed':
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                transaction.save()
                
                # Credit user balance for deposits
                if transaction.transaction_type == 'deposit':
                    transaction.user.balance += transaction.amount
                    transaction.user.save()
        
        elif event_type in ['charge.failed', 'transfer.failed']:
            transaction.status = 'failed'
            transaction.save()
            
            # Refund for failed withdrawals
            if transaction.transaction_type == 'withdrawal':
                transaction.user.balance += transaction.amount
                transaction.user.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def korapay_get_banks(request):
    """
    Get list of supported banks
    """
    country = request.query_params.get('country', 'NG')
    result = korapay.get_banks(country)
    
    if result['success']:
        return Response({
            'success': True,
            'banks': result['banks']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def korapay_resolve_account(request):
    """
    Verify bank account details
    """
    account_number = request.data.get('account_number')
    bank_code = request.data.get('bank_code')
    
    if not all([account_number, bank_code]):
        return Response({
            'success': False,
            'message': 'Account number and bank code are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = korapay.resolve_bank_account(account_number, bank_code)
    
    return Response(result, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)
