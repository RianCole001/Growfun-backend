from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal
from .models import DemoAccount, DemoInvestment, DemoTransaction
from .serializers import DemoAccountSerializer, DemoInvestmentSerializer, DemoTransactionSerializer


def _get_live_crypto_price(coin: str):
    """
    Fetch live price for a coin.
    Admin-controlled coins (EXACOIN, OPTCOIN, etc.) → AdminCryptoPrice table.
    Market coins (BTC, ETH, etc.) → CoinGecko API.
    Returns Decimal or None on failure.
    """
    import requests

    # Check admin-controlled coins first
    try:
        from investments.admin_models import AdminCryptoPrice
        admin_price = AdminCryptoPrice.objects.get(coin=coin, is_active=True)
        return admin_price.buy_price
    except Exception:
        pass

    # CoinGecko for market coins
    COINGECKO_IDS = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
        'ADA': 'cardano', 'SOL': 'solana', 'DOT': 'polkadot', 'USDT': 'tether',
    }
    gecko_id = COINGECKO_IDS.get(coin)
    if gecko_id:
        try:
            resp = requests.get(
                'https://api.coingecko.com/api/v3/simple/price',
                params={'ids': gecko_id, 'vs_currencies': 'usd'},
                timeout=8,
            )
            if resp.status_code == 200:
                data = resp.json()
                price = data.get(gecko_id, {}).get('usd')
                if price:
                    return Decimal(str(price))
        except Exception:
            pass

    return None

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
def demo_buy_crypto(request):
    """Demo crypto purchase — price is always fetched server-side, never trusted from client."""
    coin = request.data.get('coin', '').upper()
    amount = Decimal(str(request.data.get('amount', 0)))

    if not coin or amount <= 0:
        return Response({'success': False, 'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch live price server-side
    price = _get_live_crypto_price(coin)
    if price is None or price <= 0:
        return Response({'success': False, 'error': f'Unable to fetch live price for {coin}'}, status=status.HTTP_400_BAD_REQUEST)

    quantity = amount / price

    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.select_for_update().get(user=request.user)

            if demo_account.balance < amount:
                return Response({'success': False, 'error': 'Insufficient demo balance'}, status=status.HTTP_400_BAD_REQUEST)

            demo_account.balance -= amount
            demo_account.save(update_fields=['balance'])

            investment = DemoInvestment.objects.create(
                demo_account=demo_account,
                investment_type='crypto',
                asset_name=coin,
                amount=amount,
                quantity=quantity,
                price_at_purchase=price,
                current_price=price,
            )

            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='crypto_buy',
                amount=amount,
                asset=coin,
                quantity=quantity,
                price=price,
                description=f'Demo purchase of {quantity:.6f} {coin} at ${price:.2f}',
            )

            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_account.balance),
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(demo_transaction).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_sell_crypto(request):
    """Demo crypto sale — price is always fetched server-side."""
    coin = request.data.get('coin', '').upper()
    quantity = Decimal(str(request.data.get('quantity', 0)))

    if not coin or quantity <= 0:
        return Response({'success': False, 'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch live price server-side
    price = _get_live_crypto_price(coin)
    if price is None or price <= 0:
        return Response({'success': False, 'error': f'Unable to fetch live price for {coin}'}, status=status.HTTP_400_BAD_REQUEST)

    sell_amount = quantity * price

    try:
        with transaction.atomic():
            demo_account = DemoAccount.objects.select_for_update().get(user=request.user)

            investments = demo_account.investments.filter(
                investment_type='crypto',
                asset_name=coin,
                status='active'
            ).order_by('created_at')

            total_available = sum(inv.quantity for inv in investments)

            if total_available < quantity:
                return Response({
                    'success': False,
                    'error': f'Insufficient {coin} holdings. Available: {total_available:.6f}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # FIFO sell
            remaining_to_sell = quantity
            for investment in investments:
                if remaining_to_sell <= 0:
                    break
                if investment.quantity <= remaining_to_sell:
                    remaining_to_sell -= investment.quantity
                    investment.status = 'completed'
                    investment.current_price = price
                    investment.save()
                else:
                    investment.quantity -= remaining_to_sell
                    investment.amount = investment.quantity * investment.price_at_purchase
                    investment.current_price = price
                    investment.save()
                    remaining_to_sell = Decimal('0')

            demo_account.balance += sell_amount
            demo_account.save(update_fields=['balance'])

            demo_transaction = DemoTransaction.objects.create(
                demo_account=demo_account,
                transaction_type='crypto_sell',
                amount=sell_amount,
                asset=coin,
                quantity=quantity,
                price=price,
                description=f'Demo sale of {quantity:.6f} {coin} at ${price:.2f}',
            )

            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_account.balance),
                    'transaction': DemoTransactionSerializer(demo_transaction).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)

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
    """Get demo investments with live prices updated on each fetch."""
    try:
        demo_account = DemoAccount.objects.get(user=request.user)
        investments = list(demo_account.investments.filter(status='active'))

        # Update current_price for crypto holdings
        coins = set(inv.asset_name for inv in investments if inv.investment_type == 'crypto')
        live_prices = {}
        for coin in coins:
            p = _get_live_crypto_price(coin)
            if p:
                live_prices[coin] = p

        for inv in investments:
            if inv.investment_type == 'crypto' and inv.asset_name in live_prices:
                inv.current_price = live_prices[inv.asset_name]
                inv.save(update_fields=['current_price'])

        serializer = DemoInvestmentSerializer(investments, many=True)
        return Response({'success': True, 'data': serializer.data})
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)

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