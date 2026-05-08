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
from datetime import datetime

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
    
    # Include both regular deposits and admin credits as deposits
    deposits = Transaction.objects.filter(
        transaction_type__in=['deposit', 'admin_credit']
    ).select_related('user')
    
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
    """Get all investments (admin only) - includes crypto, capital plans, and real estate"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    data = []
    
    # Pre-fetch admin crypto prices to avoid N+1 queries
    admin_crypto_prices = {}
    try:
        from investments.admin_models import AdminCryptoPrice
        prices = AdminCryptoPrice.objects.filter(is_active=True).values('coin', 'price')
        admin_crypto_prices = {price['coin']: float(price['price']) for price in prices}
    except:
        pass
    
    # 1. Get crypto investments from Trade model
    from investments.models import Trade
    crypto_trades = Trade.objects.filter(status='open').select_related('user')
    
    for trade in crypto_trades:
        invested_amount = trade.entry_price * trade.quantity
        current_value = trade.quantity * (trade.current_price if trade.current_price else trade.entry_price)
        profit_loss = current_value - invested_amount
        profit_loss_percentage = (profit_loss / invested_amount * 100) if invested_amount > 0 else 0
        
        data.append({
            'id': str(trade.id),
            'user': trade.user.email,
            'user_id': trade.user.id,
            'type': 'crypto',
            'asset': trade.asset,
            'symbol': trade.asset,
            'amount': float(invested_amount),
            'quantity': float(trade.quantity),
            'price_at_purchase': float(trade.entry_price),
            'current_price': float(trade.current_price) if trade.current_price else float(trade.entry_price),
            'currentValue': float(current_value),
            'profit_loss': float(profit_loss),
            'profit_loss_percentage': float(profit_loss_percentage),
            'status': trade.status,
            'created_at': trade.created_at.isoformat()
        })
    
    # 2. Get crypto investments from Transaction model (investment type)
    crypto_investments = Transaction.objects.filter(
        transaction_type='investment',
        metadata__investment_type='crypto'
    ).select_related('user')
    
    for inv in crypto_investments:
        # Get metadata
        metadata = inv.metadata or {}
        asset = metadata.get('asset', 'BTC')
        quantity = float(metadata.get('quantity', 0))
        price_at_purchase = float(metadata.get('price_at_purchase', 0))
        
        # Use pre-fetched admin prices (no more N+1 queries!)
        current_price = admin_crypto_prices.get(asset, price_at_purchase)
        
        current_value = quantity * current_price
        profit_loss = current_value - float(inv.amount)
        profit_loss_percentage = (profit_loss / float(inv.amount) * 100) if inv.amount > 0 else 0
        
        data.append({
            'id': str(inv.id),
            'user': inv.user.email,
            'user_id': inv.user.id,
            'type': 'crypto',
            'asset': asset,
            'symbol': asset,
            'amount': float(inv.amount),
            'quantity': quantity,
            'price_at_purchase': price_at_purchase,
            'current_price': current_price,
            'currentValue': current_value,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'status': 'active',
            'created_at': inv.created_at.isoformat()
        })
    
    # 3. Get capital investment plans with optimized calculation
    from investments.models import CapitalInvestmentPlan
    from django.db.models import F, Case, When, Value, DecimalField
    from decimal import Decimal
    import math
    
    capital_plans = CapitalInvestmentPlan.objects.filter(status='active').select_related('user')
    
    for plan in capital_plans:
        # Calculate months elapsed more efficiently
        months_elapsed = 0
        if plan.start_date:
            from datetime import datetime
            current_date = timezone.now()
            months_elapsed = (current_date.year - plan.start_date.year) * 12 + (current_date.month - plan.start_date.month)
            months_elapsed = min(months_elapsed, plan.period_months)  # Cap at plan duration
        
        # Use compound interest formula instead of loop: A = P(1 + r)^t
        growth_rate = float(plan.growth_rate) / 100
        current_value = float(plan.initial_amount) * ((1 + growth_rate) ** months_elapsed)
        
        profit_loss = current_value - float(plan.initial_amount)
        profit_loss_percentage = (profit_loss / float(plan.initial_amount) * 100) if plan.initial_amount > 0 else 0
        
        data.append({
            'id': str(plan.id),
            'user': plan.user.email,
            'user_id': plan.user.id,
            'type': 'capital_plan',
            'asset': f"{plan.plan_type.title()} Plan",
            'symbol': plan.plan_type.upper(),
            'amount': float(plan.initial_amount),
            'quantity': 1,
            'price_at_purchase': float(plan.initial_amount),
            'current_price': current_value,
            'currentValue': current_value,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'status': plan.status,
            'created_at': plan.created_at.isoformat(),
            'plan_details': {
                'plan_type': plan.plan_type,
                'growth_rate': float(plan.growth_rate),
                'period_months': plan.period_months,
                'months_elapsed': months_elapsed
            }
        })
    
    # 4. Get real estate investments from transactions with optimized calculation
    real_estate_investments = Transaction.objects.filter(
        transaction_type='investment',
        metadata__investment_type='real_estate'
    ).select_related('user')
    
    for inv in real_estate_investments:
        metadata = inv.metadata or {}
        property_name = metadata.get('asset', 'Real Estate')
        
        # Calculate months elapsed
        months_elapsed = 0
        if inv.created_at:
            current_date = timezone.now()
            months_elapsed = (current_date.year - inv.created_at.year) * 12 + (current_date.month - inv.created_at.month)
        
        # Use compound interest formula: A = P(1 + r)^t
        growth_rate = 0.20  # 20% monthly for real estate
        current_value = float(inv.amount) * ((1 + growth_rate) ** months_elapsed)
        
        profit_loss = current_value - float(inv.amount)
        profit_loss_percentage = (profit_loss / float(inv.amount) * 100) if inv.amount > 0 else 0
        
        data.append({
            'id': str(inv.id),
            'user': inv.user.email,
            'user_id': inv.user.id,
            'type': 'real_estate',
            'asset': property_name,
            'symbol': 'RE',
            'amount': float(inv.amount),
            'quantity': 1,
            'price_at_purchase': float(inv.amount),
            'current_price': current_value,
            'currentValue': current_value,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'status': 'active',
            'created_at': inv.created_at.isoformat()
        })
    
    return Response({
        'data': data,
        'success': True,
        'total_investments': len(data),
        'summary': {
            'crypto_count': len([d for d in data if d['type'] == 'crypto']),
            'capital_plans_count': len([d for d in data if d['type'] == 'capital_plan']),
            'real_estate_count': len([d for d in data if d['type'] == 'real_estate']),
            'total_invested': sum(d['amount'] for d in data),
            'total_current_value': sum(d['currentValue'] for d in data),
            'total_profit_loss': sum(d['profit_loss'] for d in data)
        }
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
            'profit': 'Sell',
            'admin_credit': 'Admin Credit',
            'admin_debit': 'Admin Debit',
            'referral_bonus': 'Referral Bonus'
        }
        
        data.append({
            'id': txn.id,
            'user': txn.user.email,
            'user_id': txn.user.id,
            'type': type_mapping.get(txn.transaction_type, txn.transaction_type.title()),
            'amount': str(txn.amount),
            'asset': txn.metadata.get('asset') if txn.metadata else None,
            'method': txn.payment_method,
            'reference': txn.reference,
            'status': txn.status,
            'created_at': txn.created_at.isoformat()
        })
    
    return Response({
        'data': data,
        'success': True
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_edit_transaction(request, transaction_id):
    """Edit a transaction (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        old_amount = transaction.amount
        old_status = transaction.status
        
        # Get updated fields
        new_amount = request.data.get('amount')
        new_status = request.data.get('status')
        new_payment_method = request.data.get('payment_method')
        new_reference = request.data.get('reference')
        
        # Update amount if provided
        if new_amount is not None:
            new_amount = Decimal(str(new_amount))
            amount_difference = new_amount - old_amount
            
            # Adjust user balance based on transaction type and status
            if transaction.status == 'completed':
                if transaction.transaction_type in ['deposit', 'admin_credit', 'profit', 'referral_bonus']:
                    # For credit transactions, adjust balance by difference
                    transaction.user.balance += amount_difference
                elif transaction.transaction_type in ['withdrawal', 'investment', 'admin_debit']:
                    # For debit transactions, adjust balance by negative difference
                    transaction.user.balance -= amount_difference
                
                transaction.user.save()
            
            transaction.amount = new_amount
        
        # Update status if provided
        if new_status and new_status != old_status:
            transaction.status = new_status
            
            # If changing to completed, credit/debit user balance
            if new_status == 'completed' and old_status != 'completed':
                if transaction.transaction_type in ['deposit', 'admin_credit', 'profit', 'referral_bonus']:
                    transaction.user.balance += transaction.amount
                elif transaction.transaction_type in ['withdrawal', 'investment', 'admin_debit']:
                    transaction.user.balance -= transaction.amount
                transaction.user.save()
            
            # If changing from completed to pending/failed, reverse balance
            elif old_status == 'completed' and new_status != 'completed':
                if transaction.transaction_type in ['deposit', 'admin_credit', 'profit', 'referral_bonus']:
                    transaction.user.balance -= transaction.amount
                elif transaction.transaction_type in ['withdrawal', 'investment', 'admin_debit']:
                    transaction.user.balance += transaction.amount
                transaction.user.save()
        
        # Update payment method if provided
        if new_payment_method:
            transaction.payment_method = new_payment_method
        
        # Update reference if provided
        if new_reference:
            transaction.reference = new_reference
        
        transaction.save()
        
        return Response({
            'data': {
                'message': 'Transaction updated successfully',
                'transaction': {
                    'id': transaction.id,
                    'amount': str(transaction.amount),
                    'status': transaction.status,
                    'payment_method': transaction.payment_method,
                    'reference': transaction.reference,
                    'updated_at': transaction.updated_at.isoformat()
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_investment(request, investment_id):
    """Delete an investment (admin only) - handles Trade and CapitalInvestmentPlan"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from investments.models import Trade, CapitalInvestmentPlan
        
        # Try to find the investment in Trade model first
        investment = None
        investment_type = None
        
        try:
            investment = Trade.objects.get(id=investment_id)
            investment_type = 'trade'
        except Trade.DoesNotExist:
            pass
        
        # If not found in Trade, try CapitalInvestmentPlan
        if not investment:
            try:
                investment = CapitalInvestmentPlan.objects.get(id=investment_id)
                investment_type = 'capital_plan'
            except CapitalInvestmentPlan.DoesNotExist:
                pass
        
        # If still not found, try Transaction model (for old investment records)
        if not investment:
            try:
                investment = Transaction.objects.get(id=investment_id, transaction_type='investment')
                investment_type = 'transaction'
            except Transaction.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Investment not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Store details before deletion
        user = investment.user
        amount = investment.initial_amount if investment_type == 'capital_plan' else investment.amount if hasattr(investment, 'amount') else 0
        
        # If investment was active/completed, refund the user
        if hasattr(investment, 'status'):
            if investment.status in ['active', 'open', 'completed']:
                user.balance += Decimal(str(amount))
                user.save()
        
        # Store investment details before deletion
        investment_details = {
            'id': str(investment.id),
            'user': user.email,
            'type': investment_type,
            'amount': str(amount),
            'status': investment.status if hasattr(investment, 'status') else 'unknown'
        }
        
        # Delete the investment
        investment.delete()
        
        return Response({
            'data': {
                'message': 'Investment deleted successfully',
                'deleted_investment': investment_details
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_edit_investment(request, investment_id):
    """Edit an investment (admin only) - handles Trade and CapitalInvestmentPlan"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from investments.models import Trade, CapitalInvestmentPlan
        
        # Try to find the investment
        investment = None
        investment_type = None
        
        try:
            investment = Trade.objects.get(id=investment_id)
            investment_type = 'trade'
        except Trade.DoesNotExist:
            pass
        
        if not investment:
            try:
                investment = CapitalInvestmentPlan.objects.get(id=investment_id)
                investment_type = 'capital_plan'
            except CapitalInvestmentPlan.DoesNotExist:
                pass
        
        if not investment:
            try:
                investment = Transaction.objects.get(id=investment_id, transaction_type='investment')
                investment_type = 'transaction'
            except Transaction.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Investment not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Get updated fields
        new_amount = request.data.get('amount')
        new_status = request.data.get('status')
        
        old_amount = investment.initial_amount if investment_type == 'capital_plan' else investment.amount if hasattr(investment, 'amount') else 0
        old_status = investment.status if hasattr(investment, 'status') else None
        
        # Update amount if provided
        if new_amount is not None:
            new_amount = Decimal(str(new_amount))
            amount_difference = new_amount - Decimal(str(old_amount))
            
            # Adjust user balance if investment was active
            if old_status in ['active', 'open', 'completed']:
                # Refund old amount and charge new amount
                investment.user.balance += Decimal(str(old_amount))
                investment.user.balance -= new_amount
                investment.user.save()
            
            # Update the amount field
            if investment_type == 'capital_plan':
                investment.initial_amount = new_amount
            elif hasattr(investment, 'amount'):
                investment.amount = new_amount
        
        # Update status if provided
        if new_status and new_status != old_status:
            investment.status = new_status
        
        investment.save()
        
        return Response({
            'data': {
                'message': 'Investment updated successfully',
                'investment': {
                    'id': str(investment.id),
                    'amount': str(new_amount if new_amount else old_amount),
                    'status': investment.status if hasattr(investment, 'status') else 'unknown',
                    'updated_at': investment.updated_at.isoformat() if hasattr(investment, 'updated_at') else None
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_transaction(request, transaction_id):
    """Delete a transaction (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # If transaction was completed, reverse the balance change
        if transaction.status == 'completed':
            if transaction.transaction_type in ['deposit', 'admin_credit', 'profit', 'referral_bonus']:
                # Reverse credit
                transaction.user.balance -= transaction.amount
            elif transaction.transaction_type in ['withdrawal', 'investment', 'admin_debit']:
                # Reverse debit
                transaction.user.balance += transaction.amount
            
            transaction.user.save()
        
        # Store transaction details before deletion
        transaction_details = {
            'id': transaction.id,
            'user': transaction.user.email,
            'type': transaction.transaction_type,
            'amount': str(transaction.amount),
            'status': transaction.status
        }
        
        # Delete the transaction
        transaction.delete()
        
        return Response({
            'data': {
                'message': 'Transaction deleted successfully',
                'deleted_transaction': transaction_details
            },
            'success': True
        }, status=status.HTTP_200_OK)
    
    except Transaction.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
