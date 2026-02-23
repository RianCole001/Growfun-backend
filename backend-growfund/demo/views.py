from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal
from .models import DemoAccount, DemoInvestment, DemoTransaction
from .serializers import DemoAccountSerializer, DemoInvestmentSerializer, DemoTransactionSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def demo_account(request):
    """Get or create demo account for user"""
    demo_account, created = DemoAccount.objects.get_or_create(
        user=request.user,
        defaults={'balance': Decimal('10000.00')}
    )
    
    if request.method == 'GET':
        serializer = DemoAccountSerializer(demo_account)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'POST':
        # Reset demo account
        demo_account.balance = Decimal('10000.00')
        demo_account.save()
        
        # Clear all demo data
        demo_account.investments.all().delete()
        demo_account.transactions.all().delete()
        
        # Add initial deposit transaction
        DemoTransaction.objects.create(
            demo_account=demo_account,
            transaction_type='deposit',
            amount=Decimal('10000.00'),
            description='Initial demo balance'
        )
        
        return Response({
            'success': True,
            'message': 'Demo account reset successfully',
            'data': DemoAccountSerializer(demo_account).data
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_balance(request):
    """Get demo account balance"""
    try:
        demo_account = DemoAccount.objects.get(user=request.user)
        return Response({
            'success': True,
            'data': {'balance': demo_account.balance}
        })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_deposit(request):
    """Demo deposit"""
    amount = Decimal(str(request.data.get('amount', 0)))
    
    if amount <= 0:
        return Response({
            'success': False,
            'error': 'Invalid amount'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.get(user=request.user)
            demo_account.balance += amount
            demo_account.save()
            
            # Create transaction record
            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='deposit',
                amount=amount,
                description=f'Demo deposit of ${amount}'
            )
            
            return Response({
                'success': True,
                'data': {
                    'new_balance': demo_account.balance,
                    'transaction': DemoTransactionSerializer(demo_transaction).data
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_withdraw(request):
    """Demo withdrawal"""
    amount = Decimal(str(request.data.get('amount', 0)))
    
    if amount <= 0:
        return Response({
            'success': False,
            'error': 'Invalid amount'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.get(user=request.user)
            
            if demo_account.balance < amount:
                return Response({
                    'success': False,
                    'error': 'Insufficient balance'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            demo_account.balance -= amount
            demo_account.save()
            
            # Create transaction record
            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='withdrawal',
                amount=amount,
                description=f'Demo withdrawal of ${amount}'
            )
            
            return Response({
                'success': True,
                'data': {
                    'new_balance': demo_account.balance,
                    'transaction': DemoTransactionSerializer(demo_transaction).data
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_buy_crypto(request):
    """Demo crypto purchase"""
    coin = request.data.get('coin')
    amount = Decimal(str(request.data.get('amount', 0)))
    price = Decimal(str(request.data.get('price', 0)))
    
    if not coin or amount <= 0 or price <= 0:
        return Response({
            'success': False,
            'error': 'Invalid parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    quantity = amount / price
    
    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.get(user=request.user)
            
            if demo_account.balance < amount:
                return Response({
                    'success': False,
                    'error': 'Insufficient balance'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            demo_account.balance -= amount
            demo_account.save()
            
            # Create investment record
            investment = DemoInvestment.objects.create(
                demo_account=demo_account,
                investment_type='crypto',
                asset_name=coin,
                amount=amount,
                quantity=quantity,
                price_at_purchase=price
            )
            
            # Create transaction record
            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='crypto_buy',
                amount=amount,
                asset=coin,
                quantity=quantity,
                price=price,
                description=f'Demo purchase of {quantity:.6f} {coin}'
            )
            
            return Response({
                'success': True,
                'data': {
                    'new_balance': demo_account.balance,
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(demo_transaction).data
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_sell_crypto(request):
    """Demo crypto sale"""
    coin = request.data.get('coin')
    quantity = Decimal(str(request.data.get('quantity', 0)))
    price = Decimal(str(request.data.get('price', 0)))
    
    if not coin or quantity <= 0 or price <= 0:
        return Response({
            'success': False,
            'error': 'Invalid parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    sell_amount = quantity * price
    
    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.get(user=request.user)
            
            # Find active crypto investments for this coin
            investments = demo_account.investments.filter(
                investment_type='crypto',
                asset_name=coin,
                status='active'
            ).order_by('created_at')
            
            total_available = sum(inv.quantity for inv in investments)
            
            if total_available < quantity:
                return Response({
                    'success': False,
                    'error': f'Insufficient {coin} holdings. Available: {total_available}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Sell from oldest investments first (FIFO)
            remaining_to_sell = quantity
            for investment in investments:
                if remaining_to_sell <= 0:
                    break
                
                if investment.quantity <= remaining_to_sell:
                    # Sell entire investment
                    remaining_to_sell -= investment.quantity
                    investment.status = 'completed'
                    investment.save()
                else:
                    # Partial sell
                    investment.quantity -= remaining_to_sell
                    investment.amount = investment.quantity * investment.price_at_purchase
                    investment.save()
                    remaining_to_sell = 0
            
            # Add to balance
            demo_account.balance += sell_amount
            demo_account.save()
            
            # Create transaction record
            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='crypto_sell',
                amount=sell_amount,
                asset=coin,
                quantity=quantity,
                price=price,
                description=f'Demo sale of {quantity:.6f} {coin}'
            )
            
            return Response({
                'success': True,
                'data': {
                    'new_balance': demo_account.balance,
                    'transaction': DemoTransactionSerializer(demo_transaction).data
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_invest(request):
    """Demo investment (capital plans, real estate)"""
    investment_type = request.data.get('type', 'capital_plan')
    asset_name = request.data.get('name', 'Investment')
    amount = Decimal(str(request.data.get('amount', 0)))
    monthly_rate = request.data.get('rate')
    duration_months = request.data.get('months')
    
    if amount <= 0:
        return Response({
            'success': False,
            'error': 'Invalid amount'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.get(user=request.user)
            
            if demo_account.balance < amount:
                return Response({
                    'success': False,
                    'error': 'Insufficient balance'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            demo_account.balance -= amount
            demo_account.save()
            
            # Create investment record
            investment = DemoInvestment.objects.create(
                demo_account=demo_account,
                investment_type=investment_type,
                asset_name=asset_name,
                amount=amount,
                monthly_rate=monthly_rate,
                duration_months=duration_months
            )
            
            # Create transaction record
            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='investment',
                amount=amount,
                asset=asset_name,
                description=f'Demo investment in {asset_name}'
            )
            
            return Response({
                'success': True,
                'data': {
                    'new_balance': demo_account.balance,
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(demo_transaction).data
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_investments(request):
    """Get demo investments"""
    try:
        demo_account = DemoAccount.objects.get(user=request.user)
        investments = demo_account.investments.filter(status='active')
        serializer = DemoInvestmentSerializer(investments, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_transactions(request):
    """Get demo transaction history"""
    try:
        demo_account = DemoAccount.objects.get(user=request.user)
        transactions = demo_account.transactions.all()[:50]  # Last 50 transactions
        serializer = DemoTransactionSerializer(transactions, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except DemoAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Demo account not found'
        }, status=status.HTTP_404_NOT_FOUND)