from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
import uuid

from .models import Transaction, MoMoPayment
from .serializers import (
    TransactionSerializer, MoMoDepositSerializer,
    MoMoWithdrawalSerializer, CheckPaymentStatusSerializer
)
from .momo_service import MoMoAPIService

momo_service = MoMoAPIService()


class TransactionListView(generics.ListAPIView):
    """List all transactions for authenticated user"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def momo_deposit(request):
    """
    Initiate MoMo deposit
    """
    serializer = MoMoDepositSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    amount = serializer.validated_data['amount']
    phone_number = serializer.validated_data['phone_number']
    
    # Generate unique reference
    reference = f"DEP-{uuid.uuid4().hex[:12].upper()}"
    
    # Create transaction record
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='deposit',
        payment_method='momo',
        amount=amount,
        fee=Decimal('0'),  # No fee for deposits
        net_amount=amount,
        status='pending',
        reference=reference,
        phone_number=phone_number,
        description=f"MoMo deposit of {amount}"
    )
    
    # Create MoMo payment record
    momo_payment = MoMoPayment.objects.create(
        transaction=transaction,
        phone_number=phone_number,
        network='MTN'
    )
    
    # Request payment from MoMo API
    result = momo_service.request_to_pay(
        amount=amount,
        phone_number=phone_number,
        reference=reference,
        description=f"Deposit to GrowFund"
    )
    
    if result['success']:
        # Update transaction with MoMo reference
        transaction.external_reference = result['reference_id']
        transaction.status = 'processing'
        transaction.save()
        
        momo_payment.momo_reference = result['reference_id']
        momo_payment.save()
        
        return Response({
            'success': True,
            'message': 'Payment request sent. Please approve on your phone.',
            'transaction_id': transaction.id,
            'reference': reference,
            'momo_reference': result['reference_id'],
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
def momo_withdrawal(request):
    """
    Initiate MoMo withdrawal
    """
    serializer = MoMoWithdrawalSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    amount = serializer.validated_data['amount']
    phone_number = serializer.validated_data['phone_number']
    
    # Calculate fee (2% withdrawal fee)
    fee = amount * Decimal('0.02')
    net_amount = amount - fee
    
    # Check if user has sufficient balance
    if request.user.balance < amount:
        return Response({
            'success': False,
            'message': 'Insufficient balance'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate unique reference
    reference = f"WTH-{uuid.uuid4().hex[:12].upper()}"
    
    # Create transaction record
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='withdrawal',
        payment_method='momo',
        amount=amount,
        fee=fee,
        net_amount=net_amount,
        status='pending',
        reference=reference,
        phone_number=phone_number,
        description=f"MoMo withdrawal of {amount}"
    )
    
    # Create MoMo payment record
    momo_payment = MoMoPayment.objects.create(
        transaction=transaction,
        phone_number=phone_number,
        network='MTN'
    )
    
    # Initiate transfer via MoMo API
    result = momo_service.transfer(
        amount=net_amount,
        phone_number=phone_number,
        reference=reference,
        description=f"Withdrawal from GrowFund"
    )
    
    if result['success']:
        # Update transaction
        transaction.external_reference = result['reference_id']
        transaction.status = 'processing'
        transaction.save()
        
        momo_payment.momo_reference = result['reference_id']
        momo_payment.save()
        
        # Deduct from user balance
        request.user.balance -= amount
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Withdrawal initiated successfully',
            'transaction_id': transaction.id,
            'reference': reference,
            'momo_reference': result['reference_id'],
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
def check_payment_status(request):
    """
    Check status of MoMo payment
    """
    serializer = CheckPaymentStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    reference_id = serializer.validated_data['reference_id']
    
    # Find transaction
    try:
        momo_payment = MoMoPayment.objects.get(momo_reference=reference_id)
        transaction = momo_payment.transaction
        
        # Check if transaction belongs to user
        if transaction.user != request.user:
            return Response({
                'success': False,
                'message': 'Unauthorized'
            }, status=status.HTTP_403_FORBIDDEN)
        
    except MoMoPayment.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check status from MoMo API
    if transaction.transaction_type == 'deposit':
        result = momo_service.check_payment_status(reference_id)
    else:
        result = momo_service.check_transfer_status(reference_id)
    
    if result['success']:
        momo_status = result['status']
        
        # Update transaction status
        if momo_status == 'SUCCESSFUL' and transaction.status != 'completed':
            transaction.status = 'completed'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # For deposits, credit user balance
            if transaction.transaction_type == 'deposit':
                request.user.balance += transaction.amount
                request.user.save()
        
        elif momo_status == 'FAILED':
            transaction.status = 'failed'
            transaction.save()
            
            # For withdrawals, refund if failed
            if transaction.transaction_type == 'withdrawal' and transaction.status == 'processing':
                request.user.balance += transaction.amount
                request.user.save()
        
        return Response({
            'success': True,
            'status': momo_status,
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
@permission_classes([IsAuthenticated])
def momo_callback(request):
    """
    Webhook callback from MoMo API
    """
    # This endpoint receives notifications from MoMo when payment status changes
    data = request.data
    
    reference_id = data.get('referenceId')
    status_value = data.get('status')
    
    try:
        momo_payment = MoMoPayment.objects.get(momo_reference=reference_id)
        transaction = momo_payment.transaction
        
        if status_value == 'SUCCESSFUL' and transaction.status != 'completed':
            transaction.status = 'completed'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # Credit user balance for deposits
            if transaction.transaction_type == 'deposit':
                transaction.user.balance += transaction.amount
                transaction.user.save()
        
        elif status_value == 'FAILED':
            transaction.status = 'failed'
            transaction.save()
            
            # Refund for failed withdrawals
            if transaction.transaction_type == 'withdrawal':
                transaction.user.balance += transaction.amount
                transaction.user.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)
    
    except MoMoPayment.DoesNotExist:
        return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)
