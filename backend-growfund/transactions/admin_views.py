"""
Admin views for managing deposits, withdrawals, and transactions
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import Transaction
from .serializers import TransactionSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_deposits(request):
    """Get all deposit transactions (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    deposits = Transaction.objects.filter(transaction_type='deposit').select_related('user')
    
    data = []
    for deposit in deposits:
        data.append({
            'id': deposit.id,
            'user': deposit.user.email,
            'user_id': deposit.user.id,
            'amount': str(deposit.amount),
            'method': deposit.payment_method or 'bank_transfer',
            'reference': deposit.reference,
            'status': deposit.status,
            'created_at': deposit.created_at.isoformat(),
            'updated_at': deposit.updated_at.isoformat()
        })
    
    return Response({
        'data': data,
        'success': True
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_approve_deposit(request, deposit_id):
    """Approve a deposit (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        deposit = Transaction.objects.get(id=deposit_id, transaction_type='deposit')
        
        if deposit.status == 'completed':
            return Response({
                'success': False,
                'error': 'Deposit already approved'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update deposit status
        deposit.status = 'completed'
        deposit.completed_at = timezone.now()
        deposit.save()
        
        # Credit user balance
        user = deposit.user
        user.balance += deposit.net_amount
        user.save()
        
        # Create notification
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=user,
                title='Deposit Approved',
                message=f'Your deposit of ${deposit.amount} has been approved and credited to your account.',
                notification_type='success'
            )
        except Exception as e:
            print(f"Warning: Could not create notification: {e}")
        
        return Response({
            'data': {
                'message': 'Deposit approved successfully',
                'deposit': {
                    'id': deposit.id,
                    'status': deposit.status,
                    'updated_at': deposit.updated_at.isoformat()
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Deposit not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_reject_deposit(request, deposit_id):
    """Reject a deposit (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    reason = request.data.get('reason', 'No reason provided')
    
    try:
        deposit = Transaction.objects.get(id=deposit_id, transaction_type='deposit')
        
        if deposit.status == 'completed':
            return Response({
                'success': False,
                'error': 'Cannot reject completed deposit'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update deposit status
        deposit.status = 'failed'
        deposit.metadata['rejection_reason'] = reason
        deposit.save()
        
        # Create notification
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=deposit.user,
                title='Deposit Rejected',
                message=f'Your deposit of ${deposit.amount} has been rejected. Reason: {reason}',
                notification_type='error'
            )
        except Exception as e:
            print(f"Warning: Could not create notification: {e}")
        
        return Response({
            'data': {
                'message': 'Deposit rejected successfully',
                'deposit': {
                    'id': deposit.id,
                    'status': deposit.status,
                    'rejection_reason': reason,
                    'updated_at': deposit.updated_at.isoformat()
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Deposit not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_withdrawals(request):
    """Get all withdrawal transactions (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    withdrawals = Transaction.objects.filter(transaction_type='withdrawal').select_related('user')
    
    data = []
    for withdrawal in withdrawals:
        # Get bank details from metadata
        bank_details = withdrawal.metadata.get('bank_details', {})
        
        data.append({
            'id': withdrawal.id,
            'user': withdrawal.user.email,
            'user_id': withdrawal.user.id,
            'amount': str(withdrawal.amount),
            'method': withdrawal.payment_method or 'bank_transfer',
            'bank_details': bank_details,
            'reference': withdrawal.reference,
            'status': withdrawal.status,
            'created_at': withdrawal.created_at.isoformat(),
            'updated_at': withdrawal.updated_at.isoformat()
        })
    
    return Response({
        'data': data,
        'success': True
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_approve_withdrawal(request, withdrawal_id):
    """Approve a withdrawal (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        withdrawal = Transaction.objects.get(id=withdrawal_id, transaction_type='withdrawal')
        
        if withdrawal.status == 'completed':
            return Response({
                'success': False,
                'error': 'Withdrawal already approved'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update withdrawal status
        withdrawal.status = 'completed'
        withdrawal.completed_at = timezone.now()
        withdrawal.save()
        
        # Create notification
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=withdrawal.user,
                title='Withdrawal Approved',
                message=f'Your withdrawal of ${withdrawal.amount} has been approved and processed.',
                notification_type='success'
            )
        except Exception as e:
            print(f"Warning: Could not create notification: {e}")
        
        return Response({
            'data': {
                'message': 'Withdrawal approved successfully',
                'withdrawal': {
                    'id': withdrawal.id,
                    'status': withdrawal.status,
                    'updated_at': withdrawal.updated_at.isoformat()
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Withdrawal not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_reject_withdrawal(request, withdrawal_id):
    """Reject a withdrawal (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    reason = request.data.get('reason', 'No reason provided')
    
    try:
        withdrawal = Transaction.objects.get(id=withdrawal_id, transaction_type='withdrawal')
        
        if withdrawal.status == 'completed':
            return Response({
                'success': False,
                'error': 'Cannot reject completed withdrawal'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update withdrawal status
        withdrawal.status = 'failed'
        withdrawal.metadata['rejection_reason'] = reason
        withdrawal.save()
        
        # Refund user balance
        user = withdrawal.user
        user.balance += withdrawal.amount
        user.save()
        
        # Create notification
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=user,
                title='Withdrawal Rejected',
                message=f'Your withdrawal of ${withdrawal.amount} has been rejected and refunded. Reason: {reason}',
                notification_type='warning'
            )
        except Exception as e:
            print(f"Warning: Could not create notification: {e}")
        
        return Response({
            'data': {
                'message': 'Withdrawal rejected successfully',
                'withdrawal': {
                    'id': withdrawal.id,
                    'status': withdrawal.status,
                    'rejection_reason': reason,
                    'updated_at': withdrawal.updated_at.isoformat()
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Withdrawal not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_investments(request):
    """Get all investments (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    from investments.models import Trade
    
    investments = Trade.objects.filter(status='open').select_related('user')
    
    data = []
    for investment in investments:
        invested_amount = investment.entry_price * investment.quantity
        current_value = investment.quantity * (investment.current_price if investment.current_price else investment.entry_price)
        profit_loss = current_value - invested_amount
        profit_loss_percentage = (profit_loss / invested_amount * 100) if invested_amount > 0 else 0
        
        data.append({
            'id': str(investment.id),
            'user': investment.user.email,
            'user_id': investment.user.id,
            'type': 'crypto',
            'asset': investment.asset,
            'symbol': investment.asset,
            'amount': f"{invested_amount:.2f}",
            'quantity': f"{investment.quantity:.8f}",
            'price_at_purchase': f"{investment.entry_price:.2f}",
            'current_price': f"{investment.current_price:.2f}" if investment.current_price else f"{investment.entry_price:.2f}",
            'current_value': f"{current_value:.2f}",
            'profit_loss': f"{profit_loss:.2f}",
            'profit_loss_percentage': float(f"{profit_loss_percentage:.2f}"),
            'status': investment.status,
            'created_at': investment.created_at.isoformat()
        })
    
    return Response({
        'data': data,
        'success': True
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_get_transactions(request):
    """Get all transactions (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    transactions = Transaction.objects.all().select_related('user').order_by('-created_at')[:100]
    
    data = []
    for txn in transactions:
        # Map transaction types to frontend format
        type_mapping = {
            'deposit': 'Deposit',
            'withdrawal': 'Withdraw',
            'investment': 'Invest',
            'profit': 'Sell'
        }
        
        data.append({
            'id': txn.id,
            'user': txn.user.email,
            'user_id': txn.user.id,
            'type': type_mapping.get(txn.transaction_type, txn.transaction_type.title()),
            'amount': str(txn.amount),
            'asset': txn.metadata.get('asset'),
            'method': txn.payment_method,
            'reference': txn.reference,
            'status': txn.status,
            'created_at': txn.created_at.isoformat()
        })
    
    return Response({
        'data': data,
        'success': True
    }, status=status.HTTP_200_OK)
