"""
Live account investment views that mirror demo functionality
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal

from .models import Trade, CapitalInvestmentPlan
from .admin_models import AdminCryptoPrice
from transactions.models import Transaction
from settings_app.models import PlatformSettings


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_portfolio(request):
    """
    Live account portfolio - matches demo portfolio functionality
    Returns: balance + all investments with current values
    """
    user = request.user
    
    # Get all active investments
    crypto_trades = Trade.objects.filter(user=user, status='open').exclude(asset__in=['gold'])
    capital_plans = CapitalInvestmentPlan.objects.filter(user=user, status='active')
    
    # Calculate crypto values with live prices
    crypto_value = Decimal('0')
    crypto_investments = []
    
    if crypto_trades.exists():
        # Get live prices
        held_coins = set(trade.asset for trade in crypto_trades)
        from .views import _fetch_live_prices
        live_prices, coin_names = _fetch_live_prices(held_coins)
        
        for trade in crypto_trades:
            coin = trade.asset
            invested_amount = trade.entry_price * trade.quantity
            current_price = live_prices.get(coin) or trade.current_price or trade.entry_price
            current_value = trade.quantity * current_price
            profit_loss = current_value - invested_amount
            
            crypto_investments.append({
                'id': str(trade.id),
                'asset': coin,
                'name': coin_names.get(coin, coin),
                'quantity': f"{trade.quantity:.8f}",
                'invested_amount': f"{invested_amount:.2f}",
                'current_price': f"{current_price:.2f}",
                'current_value': f"{current_value:.2f}",
                'profit_loss': f"{profit_loss:.2f}",
                'profit_loss_percentage': float(f"{(profit_loss / invested_amount * 100):.2f}") if invested_amount > 0 else 0.0,
                'date': trade.created_at.isoformat()
            })
            
            crypto_value += current_value
    
    # Calculate capital plan values
    plan_value = Decimal('0')
    plan_investments = []
    
    for plan in capital_plans:
        plan_investments.append({
            'id': str(plan.id),
            'type': plan.plan_type,
            'name': f'{plan.plan_type.title()} Plan',
            'invested_amount': f"{plan.initial_amount:.2f}",
            'current_value': f"{plan.total_return:.2f}",
            'profit_loss': f"{plan.total_return - plan.initial_amount:.2f}",
            'growth_rate': f"{plan.growth_rate:.2f}%",
            'period_months': plan.period_months,
            'date': plan.created_at.isoformat()
        })
        plan_value += plan.total_return
    
    total_invested = sum(Decimal(inv['invested_amount']) for inv in crypto_investments + plan_investments)
    total_value = crypto_value + plan_value
    total_profit_loss = total_value - total_invested
    
    return Response({
        'success': True,
        'data': {
            'balance': f"{user.balance:.2f}",
            'total_invested': f"{total_invested:.2f}",
            'total_value': f"{total_value:.2f}",
            'total_profit_loss': f"{total_profit_loss:.2f}",
            'total_profit_loss_percentage': float(f"{(total_profit_loss / total_invested * 100):.2f}") if total_invested > 0 else 0.0,
            'crypto': {
                'value': f"{crypto_value:.2f}",
                'count': len(crypto_investments),
                'investments': crypto_investments
            },
            'capital_plans': {
                'value': f"{plan_value:.2f}",
                'count': len(plan_investments),
                'investments': plan_investments
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def live_invest_capital_plan(request):
    """
    Invest in capital plan - matches demo functionality
    Body: { plan_type: "basic"|"standard"|"advance", amount: 100, period_months: 6 }
    """
    plan_type = request.data.get('plan_type', '').lower()
    amount = Decimal(str(request.data.get('amount', 0)))
    period_months = int(request.data.get('period_months', 6))
    
    if plan_type not in ['basic', 'standard', 'advance']:
        return Response({
            'success': False,
            'error': 'Invalid plan type. Must be basic, standard, or advance'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if amount <= 0:
        return Response({
            'success': False,
            'error': 'Amount must be greater than 0'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check minimum investment
    settings = PlatformSettings.get_settings()
    min_amounts = {
        'basic': settings.capital_basic_min,
        'standard': settings.capital_standard_min,
        'advance': settings.capital_advance_min
    }
    
    if amount < min_amounts[plan_type]:
        return Response({
            'success': False,
            'error': f'Minimum investment for {plan_type} plan is ${min_amounts[plan_type]}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check user balance
    if request.user.balance < amount:
        return Response({
            'success': False,
            'error': f'Insufficient balance. Available: ${request.user.balance:.2f}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Growth rates
    growth_rates = {
        'basic': Decimal('20.00'),      # 20% per month
        'standard': Decimal('30.00'),   # 30% per month
        'advance': Decimal('40.00'),    # 40% per month
    }
    
    with db_transaction.atomic():
        # Deduct from balance
        user = request.user
        user.balance -= amount
        user.save(update_fields=['balance'])
        
        # Create investment plan
        plan = CapitalInvestmentPlan.objects.create(
            user=user,
            plan_type=plan_type,
            initial_amount=amount,
            period_months=period_months,
            growth_rate=growth_rates[plan_type]
        )
        
        # Create transaction record
        Transaction.objects.create(
            user=user,
            transaction_type='investment',
            amount=amount,
            net_amount=amount,
            status='completed',
            reference=f"CAPITAL-PLAN-{plan.id}",
            description=f"Capital plan investment: {plan_type.title()} plan - {period_months} months",
            completed_at=timezone.now()
        )
        
        # Create notification
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=user,
                title="Investment Created",
                message=f"Successfully invested ${amount} in {plan_type.title()} capital plan",
                notification_type='success'
            )
        except Exception:
            pass
    
    return Response({
        'success': True,
        'data': {
            'investment': {
                'id': str(plan.id),
                'type': 'capital_plan',
                'plan_type': plan_type,
                'amount': f"{amount:.2f}",
                'period_months': period_months,
                'growth_rate': f"{growth_rates[plan_type]:.2f}%",
                'status': 'active',
                'date': plan.created_at.isoformat()
            },
            'new_balance': f"{user.balance:.2f}",
            'message': f'Successfully invested in {plan_type.title()} capital plan'
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_dashboard_stats(request):
    """
    Dashboard statistics for live account
    """
    user = request.user
    
    # Get investment counts and values
    crypto_trades = Trade.objects.filter(user=user, status='open').exclude(asset__in=['gold'])
    capital_plans = CapitalInvestmentPlan.objects.filter(user=user, status='active')
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Calculate totals
    total_crypto_invested = sum(trade.entry_price * trade.quantity for trade in crypto_trades)
    total_plan_invested = sum(plan.initial_amount for plan in capital_plans)
    total_invested = total_crypto_invested + total_plan_invested
    
    return Response({
        'success': True,
        'data': {
            'balance': f"{user.balance:.2f}",
            'total_invested': f"{total_invested:.2f}",
            'investment_count': crypto_trades.count() + capital_plans.count(),
            'crypto_investments': crypto_trades.count(),
            'capital_plans': capital_plans.count(),
            'recent_transactions': [
                {
                    'type': txn.transaction_type,
                    'amount': f"{txn.amount:.2f}",
                    'description': txn.description,
                    'status': txn.status,
                    'date': txn.created_at.isoformat()
                }
                for txn in recent_transactions
            ]
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_balance(request):
    """
    Get live account balance and basic info
    """
    user = request.user
    
    # Count investments
    crypto_count = Trade.objects.filter(user=user, status='open').exclude(asset__in=['gold']).count()
    plan_count = CapitalInvestmentPlan.objects.filter(user=user, status='active').count()
    
    return Response({
        'success': True,
        'data': {
            'balance': f"{user.balance:.2f}",
            'email': user.email,
            'name': user.get_full_name(),
            'crypto_investments': crypto_count,
            'capital_plans': plan_count,
            'total_investments': crypto_count + plan_count
        }
    }, status=status.HTTP_200_OK)