from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal, InvalidOperation
from .models import DemoAccount, DemoInvestment, DemoTransaction
from .serializers import DemoAccountSerializer, DemoInvestmentSerializer, DemoTransactionSerializer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_demo_account(user):
    demo_acc, created = DemoAccount.objects.get_or_create(
        user=user,
        defaults={'balance': Decimal('10000.00')}
    )
    if created:
        DemoTransaction.objects.create(
            demo_account=demo_acc,
            transaction_type='deposit',
            amount=Decimal('10000.00'),
            description='Initial demo balance',
        )
    return demo_acc


def _to_decimal(value, default=Decimal('0')):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def _has_current_price_column():
    """Check if the current_price column exists (migration may not have run yet)."""
    from django.db import connection
    columns = [col.name for col in connection.introspection.get_table_description(
        connection.cursor(), 'demo_demoinvestment'
    )]
    return 'current_price' in columns


def _safe_save_current_price(inv, price):
    """Save current_price only if the column exists in the DB."""
    try:
        inv.current_price = price
        inv.save(update_fields=['current_price'])
    except Exception:
        pass  # Column doesn't exist yet — migration pending


def _get_live_crypto_price(coin: str):
    import requests
    try:
        from investments.admin_models import AdminCryptoPrice
        admin_price = AdminCryptoPrice.objects.get(coin=coin, is_active=True)
        return admin_price.buy_price
    except Exception:
        pass

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


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def demo_account(request):
    """GET — return account (auto-creates). POST — reset to $10,000."""
    demo_acc = _get_or_create_demo_account(request.user)

    if request.method == 'GET':
        return Response({'success': True, 'data': DemoAccountSerializer(demo_acc).data})

    with transaction.atomic():
        demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
        demo_acc.balance = Decimal('10000.00')
        demo_acc.save(update_fields=['balance'])
        demo_acc.investments.all().delete()
        demo_acc.transactions.all().delete()
        DemoTransaction.objects.create(
            demo_account=demo_acc,
            transaction_type='deposit',
            amount=Decimal('10000.00'),
            description='Demo account reset',
        )

    return Response({
        'success': True,
        'message': 'Demo account reset to $10,000',
        'data': DemoAccountSerializer(demo_acc).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_balance(request):
    demo_acc = _get_or_create_demo_account(request.user)
    return Response({'success': True, 'data': {'balance': str(demo_acc.balance)}})


# ---------------------------------------------------------------------------
# Crypto
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_buy_crypto(request):
    """Buy crypto. Body: { coin, amount }"""
    coin = request.data.get('coin', '').upper().strip()
    amount = _to_decimal(request.data.get('amount'))

    if not coin:
        return Response({'success': False, 'error': 'coin is required'}, status=status.HTTP_400_BAD_REQUEST)
    if amount <= 0:
        return Response({'success': False, 'error': 'amount must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

    price = _get_live_crypto_price(coin)
    if not price or price <= 0:
        return Response({'success': False, 'error': f'Unable to fetch live price for {coin}'}, status=status.HTTP_400_BAD_REQUEST)

    quantity = amount / price

    try:
        with transaction.atomic():
            demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
            if demo_acc.balance < amount:
                return Response({'success': False, 'error': 'Insufficient demo balance'}, status=status.HTTP_400_BAD_REQUEST)

            demo_acc.balance -= amount
            demo_acc.save(update_fields=['balance'])

            investment = DemoInvestment.objects.create(
                demo_account=demo_acc,
                investment_type='crypto',
                asset_name=coin,
                amount=amount,
                quantity=quantity,
                price_at_purchase=price,
            )
            # Set current_price safely (column may not exist if migration pending)
            _safe_save_current_price(investment, price)
            tx = DemoTransaction.objects.create(
                demo_account=demo_acc,
                transaction_type='crypto_buy',
                amount=amount,
                asset=coin,
                quantity=quantity,
                price=price,
                description=f'Bought {quantity:.6f} {coin} at ${price:.2f}',
            )
            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_acc.balance),
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(tx).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_sell_crypto(request):
    """Sell crypto (FIFO). Body: { coin, quantity }"""
    coin = request.data.get('coin', '').upper().strip()
    quantity = _to_decimal(request.data.get('quantity'))

    if not coin:
        return Response({'success': False, 'error': 'coin is required'}, status=status.HTTP_400_BAD_REQUEST)
    if quantity <= 0:
        return Response({'success': False, 'error': 'quantity must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

    price = _get_live_crypto_price(coin)
    if not price or price <= 0:
        return Response({'success': False, 'error': f'Unable to fetch live price for {coin}'}, status=status.HTTP_400_BAD_REQUEST)

    sell_amount = quantity * price

    try:
        with transaction.atomic():
            demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
            investments = list(demo_acc.investments.filter(
                investment_type='crypto', asset_name=coin, status='active',
            ).order_by('created_at'))

            total_available = sum(inv.quantity for inv in investments)
            if total_available < quantity:
                return Response({
                    'success': False,
                    'error': f'Insufficient {coin}. Available: {total_available:.6f}',
                }, status=status.HTTP_400_BAD_REQUEST)

            remaining = quantity
            for inv in investments:
                if remaining <= 0:
                    break
                if inv.quantity <= remaining:
                    remaining -= inv.quantity
                    inv.status = 'completed'
                    inv.save(update_fields=['status'])
                    _safe_save_current_price(inv, price)
                else:
                    inv.quantity -= remaining
                    inv.amount = inv.quantity * inv.price_at_purchase
                    inv.save(update_fields=['quantity', 'amount'])
                    _safe_save_current_price(inv, price)
                    remaining = Decimal('0')

            demo_acc.balance += sell_amount
            demo_acc.save(update_fields=['balance'])

            tx = DemoTransaction.objects.create(
                demo_account=demo_acc,
                transaction_type='crypto_sell',
                amount=sell_amount,
                asset=coin,
                quantity=quantity,
                price=price,
                description=f'Sold {quantity:.6f} {coin} at ${price:.2f}',
            )
            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_acc.balance),
                    'transaction': DemoTransactionSerializer(tx).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Capital Plans
# ---------------------------------------------------------------------------

PLAN_RATES = {
    'basic': {'rate': Decimal('20'), 'name': 'Basic Capital Plan'},
    'standard': {'rate': Decimal('30'), 'name': 'Standard Capital Plan'},
    'advance': {'rate': Decimal('40'), 'name': 'Advance Capital Plan'},
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_invest_capital_plan(request):
    """
    Invest in a demo capital plan.
    Body: { plan_type: basic|standard|advance, amount, months }
    """
    plan_type = request.data.get('plan_type', '').lower().strip()
    amount = _to_decimal(request.data.get('amount'))
    months_raw = request.data.get('months')

    if plan_type not in PLAN_RATES:
        return Response({'success': False, 'error': 'plan_type must be basic, standard, or advance'}, status=status.HTTP_400_BAD_REQUEST)
    if amount <= 0:
        return Response({'success': False, 'error': 'amount must be > 0'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        months = int(months_raw)
        if months <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return Response({'success': False, 'error': 'months must be a positive integer'}, status=status.HTTP_400_BAD_REQUEST)

    plan = PLAN_RATES[plan_type]

    try:
        with transaction.atomic():
            demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
            if demo_acc.balance < amount:
                return Response({'success': False, 'error': 'Insufficient demo balance'}, status=status.HTTP_400_BAD_REQUEST)

            demo_acc.balance -= amount
            demo_acc.save(update_fields=['balance'])

            investment = DemoInvestment.objects.create(
                demo_account=demo_acc,
                investment_type='capital_plan',
                asset_name=plan['name'],
                amount=amount,
                monthly_rate=plan['rate'],
                duration_months=months,
            )
            tx = DemoTransaction.objects.create(
                demo_account=demo_acc,
                transaction_type='investment',
                amount=amount,
                asset=plan['name'],
                description=f'Demo {plan["name"]} — {months} months at {plan["rate"]}%/month',
            )
            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_acc.balance),
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(tx).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Real Estate
# ---------------------------------------------------------------------------

PROPERTY_TYPES = {
    'starter': {'rate': Decimal('8'), 'name': 'Starter Property', 'months': 12},
    'premium': {'rate': Decimal('12'), 'name': 'Premium Property', 'months': 12},
    'luxury': {'rate': Decimal('18'), 'name': 'Luxury Estate', 'months': 12},
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_invest_real_estate(request):
    """
    Invest in a demo real estate property.
    Body: { property_type: starter|premium|luxury, amount }
    """
    property_type = request.data.get('property_type', '').lower().strip()
    amount = _to_decimal(request.data.get('amount'))

    if property_type not in PROPERTY_TYPES:
        return Response({'success': False, 'error': 'property_type must be starter, premium, or luxury'}, status=status.HTTP_400_BAD_REQUEST)
    if amount <= 0:
        return Response({'success': False, 'error': 'amount must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

    prop = PROPERTY_TYPES[property_type]

    try:
        with transaction.atomic():
            demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
            if demo_acc.balance < amount:
                return Response({'success': False, 'error': 'Insufficient demo balance'}, status=status.HTTP_400_BAD_REQUEST)

            demo_acc.balance -= amount
            demo_acc.save(update_fields=['balance'])

            investment = DemoInvestment.objects.create(
                demo_account=demo_acc,
                investment_type='real_estate',
                asset_name=prop['name'],
                amount=amount,
                monthly_rate=prop['rate'],
                duration_months=prop['months'],
            )
            tx = DemoTransaction.objects.create(
                demo_account=demo_acc,
                transaction_type='investment',
                amount=amount,
                asset=prop['name'],
                description=f'Demo {prop["name"]} — {prop["rate"]}%/month for {prop["months"]} months',
            )
            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_acc.balance),
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(tx).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Generic invest (backward compat)
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_invest(request):
    """
    Generic demo investment. Prefer the specific endpoints above.
    Body: { type, name, amount, rate (optional), months (optional) }
    """
    investment_type = request.data.get('type', 'capital_plan')
    asset_name = request.data.get('name', 'Investment')
    amount = _to_decimal(request.data.get('amount'))
    rate_raw = request.data.get('rate')
    months_raw = request.data.get('months')

    monthly_rate = _to_decimal(rate_raw) if rate_raw is not None else None
    try:
        duration_months = int(months_raw) if months_raw is not None else None
    except (TypeError, ValueError):
        duration_months = None

    if amount <= 0:
        return Response({'success': False, 'error': 'amount must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
            if demo_acc.balance < amount:
                return Response({'success': False, 'error': 'Insufficient demo balance'}, status=status.HTTP_400_BAD_REQUEST)

            demo_acc.balance -= amount
            demo_acc.save(update_fields=['balance'])

            investment = DemoInvestment.objects.create(
                demo_account=demo_acc,
                investment_type=investment_type,
                asset_name=asset_name,
                amount=amount,
                monthly_rate=monthly_rate,
                duration_months=duration_months,
            )
            tx = DemoTransaction.objects.create(
                demo_account=demo_acc,
                transaction_type='investment',
                amount=amount,
                asset=asset_name,
                description=f'Demo investment in {asset_name}',
            )
            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_acc.balance),
                    'investment': DemoInvestmentSerializer(investment).data,
                    'transaction': DemoTransactionSerializer(tx).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Portfolio & Transactions
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_investments(request):
    """
    Get all active demo investments.
    Crypto holdings get live price updated on each fetch.
    Query params: ?type=crypto|capital_plan|real_estate (optional filter)
    """
    demo_acc = _get_or_create_demo_account(request.user)
    inv_type = request.GET.get('type')

    qs = demo_acc.investments.filter(status='active')
    if inv_type:
        qs = qs.filter(investment_type=inv_type)

    investments = list(qs)

    # Update live prices for crypto
    coins = set(inv.asset_name for inv in investments if inv.investment_type == 'crypto')
    live_prices = {}
    for coin in coins:
        p = _get_live_crypto_price(coin)
        if p:
            live_prices[coin] = p

    for inv in investments:
        if inv.investment_type == 'crypto' and inv.asset_name in live_prices:
            _safe_save_current_price(inv, live_prices[inv.asset_name])

    serializer = DemoInvestmentSerializer(investments, many=True)
    return Response({'success': True, 'data': serializer.data, 'count': len(investments)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_portfolio(request):
    """
    Full portfolio summary: balance + all active investments with live values.
    """
    demo_acc = _get_or_create_demo_account(request.user)
    investments = list(demo_acc.investments.filter(status='active'))

    # Fetch live prices for all crypto
    coins = set(inv.asset_name for inv in investments if inv.investment_type == 'crypto')
    live_prices = {}
    for coin in coins:
        p = _get_live_crypto_price(coin)
        if p:
            live_prices[coin] = p

    crypto_value = Decimal('0')
    plan_value = Decimal('0')
    real_estate_value = Decimal('0')

    for inv in investments:
        if inv.investment_type == 'crypto':
            lp = live_prices.get(inv.asset_name)
            if lp and inv.quantity:
                current_val = inv.quantity * lp
                _safe_save_current_price(inv, lp)
                crypto_value += current_val
            else:
                crypto_value += inv.amount
        elif inv.investment_type == 'capital_plan':
            plan_value += inv.amount
        elif inv.investment_type == 'real_estate':
            real_estate_value += inv.amount

    total_invested = crypto_value + plan_value + real_estate_value
    total_portfolio = demo_acc.balance + total_invested

    return Response({
        'success': True,
        'data': {
            'balance': str(demo_acc.balance),
            'crypto_value': str(crypto_value),
            'capital_plan_value': str(plan_value),
            'real_estate_value': str(real_estate_value),
            'total_invested': str(total_invested),
            'total_portfolio_value': str(total_portfolio),
            'investments': DemoInvestmentSerializer(investments, many=True).data,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demo_transactions(request):
    """
    Get demo transaction history.
    Query params: ?limit=50&offset=0&type=crypto_buy (optional filters)
    """
    demo_acc = _get_or_create_demo_account(request.user)

    limit = min(int(request.GET.get('limit', 50)), 200)
    offset = int(request.GET.get('offset', 0))
    tx_type = request.GET.get('type')

    qs = demo_acc.transactions.all()
    if tx_type:
        qs = qs.filter(transaction_type=tx_type)

    total = qs.count()
    txs = qs[offset:offset + limit]
    serializer = DemoTransactionSerializer(txs, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'count': len(serializer.data),
        'total': total,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_deposit(request):
    """Add virtual funds to demo account. Body: { amount }"""
    amount = _to_decimal(request.data.get('amount'))
    if amount <= 0:
        return Response({'success': False, 'error': 'amount must be > 0'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            demo_acc = DemoAccount.objects.select_for_update().get(user=request.user)
            demo_acc.balance += amount
            demo_acc.save(update_fields=['balance'])
            tx = DemoTransaction.objects.create(
                demo_account=demo_acc,
                transaction_type='deposit',
                amount=amount,
                description=f'Demo deposit of ${amount}',
            )
            return Response({
                'success': True,
                'data': {
                    'new_balance': str(demo_acc.balance),
                    'transaction': DemoTransactionSerializer(tx).data,
                }
            })
    except DemoAccount.DoesNotExist:
        return Response({'success': False, 'error': 'Demo account not found'}, status=status.HTTP_404_NOT_FOUND)
