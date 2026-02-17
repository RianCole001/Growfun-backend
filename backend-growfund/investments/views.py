from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Trade, TradeHistory, CapitalInvestmentPlan
from .serializers import (
    TradeSerializer, CreateTradeSerializer, CloseTradeSerializer, TradeHistorySerializer,
    CapitalInvestmentPlanSerializer, CreateCapitalInvestmentPlanSerializer,
    CapitalInvestmentPlanDetailSerializer
)


class CapitalInvestmentPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing capital investment plans"""
    
    serializer_class = CapitalInvestmentPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return investment plans for current user"""
        return CapitalInvestmentPlan.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new investment plan"""
        serializer = CreateCapitalInvestmentPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Create investment plan
        plan = CapitalInvestmentPlan.objects.create(
            user=request.user,
            plan_type=data['plan_type'],
            initial_amount=data['initial_amount'],
            period_months=data['period_months'],
            growth_rate=data['growth_rate']
        )
        
        serializer = CapitalInvestmentPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Get detailed investment plan with monthly breakdown"""
        instance = self.get_object()
        serializer = CapitalInvestmentPlanDetailSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_plans(self, request):
        """Get all active investment plans"""
        plans = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed_plans(self, request):
        """Get all completed investment plans"""
        plans = self.get_queryset().filter(status='completed')
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark investment plan as completed"""
        plan = self.get_object()
        
        if plan.status == 'completed':
            return Response(
                {'error': 'Plan is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'completed'
        plan.completed_at = timezone.now()
        plan.save()
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel investment plan"""
        plan = self.get_object()
        
        if plan.status == 'cancelled':
            return Response(
                {'error': 'Plan is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'cancelled'
        plan.save()
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get investment plans summary"""
        plans = self.get_queryset()
        
        total_invested = sum(p.initial_amount for p in plans)
        total_returns = sum(p.total_return for p in plans)
        active_count = plans.filter(status='active').count()
        completed_count = plans.filter(status='completed').count()
        
        return Response({
            'total_invested': float(total_invested),
            'total_returns': float(total_returns),
            'active_plans': active_count,
            'completed_plans': completed_count,
            'total_plans': plans.count()
        })


class TradeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing trades"""
    
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return trades for current user"""
        return Trade.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new trade"""
        serializer = CreateTradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Calculate expiry time if timeframe is provided
        expires_at = None
        if data.get('timeframe'):
            timeframe_map = {
                '1m': timedelta(minutes=1),
                '5m': timedelta(minutes=5),
                '15m': timedelta(minutes=15),
                '30m': timedelta(minutes=30),
                '1h': timedelta(hours=1),
                '4h': timedelta(hours=4),
                '1d': timedelta(days=1),
            }
            expires_at = timezone.now() + timeframe_map[data['timeframe']]
        
        # Create trade
        trade = Trade.objects.create(
            user=request.user,
            asset=data['asset'],
            trade_type=data['trade_type'],
            entry_price=data['entry_price'],
            current_price=data['entry_price'],
            quantity=data['quantity'],
            stop_loss=data.get('stop_loss'),
            take_profit=data.get('take_profit'),
            timeframe=data.get('timeframe'),
            expires_at=expires_at
        )
        
        serializer = TradeSerializer(trade)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a trade"""
        trade = self.get_object()
        
        if trade.status != 'open':
            return Response(
                {'error': f'Trade is already {trade.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CloseTradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        exit_price = serializer.validated_data['exit_price']
        close_reason = serializer.validated_data['close_reason']
        
        # Calculate P&L
        pnl, pnl_percentage = trade.calculate_pnl(exit_price)
        
        # Update trade
        trade.exit_price = exit_price
        trade.current_price = exit_price
        trade.profit_loss = pnl
        trade.profit_loss_percentage = pnl_percentage
        trade.status = 'closed'
        trade.closed_at = timezone.now()
        trade.save()
        
        # Create history record
        TradeHistory.objects.create(
            user=request.user,
            asset=trade.asset,
            trade_type=trade.trade_type,
            entry_price=trade.entry_price,
            exit_price=exit_price,
            quantity=trade.quantity,
            profit_loss=pnl,
            profit_loss_percentage=pnl_percentage,
            close_reason=close_reason,
            opened_at=trade.created_at
        )
        
        serializer = TradeSerializer(trade)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """Update current price and check stop loss/take profit"""
        trade = self.get_object()
        
        if trade.status != 'open':
            return Response(
                {'error': 'Trade is not open'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_price = request.data.get('current_price')
        if not current_price:
            return Response(
                {'error': 'current_price is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_price = float(current_price)
        
        # Check expiry
        if trade.check_expiry():
            trade.exit_price = current_price
            trade.current_price = current_price
            pnl, pnl_percentage = trade.calculate_pnl(current_price)
            trade.profit_loss = pnl
            trade.profit_loss_percentage = pnl_percentage
            trade.status = 'expired'
            trade.closed_at = timezone.now()
            trade.save()
            
            TradeHistory.objects.create(
                user=request.user,
                asset=trade.asset,
                trade_type=trade.trade_type,
                entry_price=trade.entry_price,
                exit_price=current_price,
                quantity=trade.quantity,
                profit_loss=pnl,
                profit_loss_percentage=pnl_percentage,
                close_reason='expired',
                opened_at=trade.created_at
            )
            
            serializer = TradeSerializer(trade)
            return Response(serializer.data)
        
        # Check stop loss
        if trade.stop_loss:
            if trade.trade_type == 'buy' and current_price <= trade.stop_loss:
                trade.exit_price = trade.stop_loss
                trade.current_price = trade.stop_loss
                pnl, pnl_percentage = trade.calculate_pnl(trade.stop_loss)
                trade.profit_loss = pnl
                trade.profit_loss_percentage = pnl_percentage
                trade.status = 'stop_loss_hit'
                trade.closed_at = timezone.now()
                trade.save()
                
                TradeHistory.objects.create(
                    user=request.user,
                    asset=trade.asset,
                    trade_type=trade.trade_type,
                    entry_price=trade.entry_price,
                    exit_price=trade.stop_loss,
                    quantity=trade.quantity,
                    profit_loss=pnl,
                    profit_loss_percentage=pnl_percentage,
                    close_reason='stop_loss',
                    opened_at=trade.created_at
                )
                
                serializer = TradeSerializer(trade)
                return Response(serializer.data)
            
            elif trade.trade_type == 'sell' and current_price >= trade.stop_loss:
                trade.exit_price = trade.stop_loss
                trade.current_price = trade.stop_loss
                pnl, pnl_percentage = trade.calculate_pnl(trade.stop_loss)
                trade.profit_loss = pnl
                trade.profit_loss_percentage = pnl_percentage
                trade.status = 'stop_loss_hit'
                trade.closed_at = timezone.now()
                trade.save()
                
                TradeHistory.objects.create(
                    user=request.user,
                    asset=trade.asset,
                    trade_type=trade.trade_type,
                    entry_price=trade.entry_price,
                    exit_price=trade.stop_loss,
                    quantity=trade.quantity,
                    profit_loss=pnl,
                    profit_loss_percentage=pnl_percentage,
                    close_reason='stop_loss',
                    opened_at=trade.created_at
                )
                
                serializer = TradeSerializer(trade)
                return Response(serializer.data)
        
        # Check take profit
        if trade.take_profit:
            if trade.trade_type == 'buy' and current_price >= trade.take_profit:
                trade.exit_price = trade.take_profit
                trade.current_price = trade.take_profit
                pnl, pnl_percentage = trade.calculate_pnl(trade.take_profit)
                trade.profit_loss = pnl
                trade.profit_loss_percentage = pnl_percentage
                trade.status = 'take_profit_hit'
                trade.closed_at = timezone.now()
                trade.save()
                
                TradeHistory.objects.create(
                    user=request.user,
                    asset=trade.asset,
                    trade_type=trade.trade_type,
                    entry_price=trade.entry_price,
                    exit_price=trade.take_profit,
                    quantity=trade.quantity,
                    profit_loss=pnl,
                    profit_loss_percentage=pnl_percentage,
                    close_reason='take_profit',
                    opened_at=trade.created_at
                )
                
                serializer = TradeSerializer(trade)
                return Response(serializer.data)
            
            elif trade.trade_type == 'sell' and current_price <= trade.take_profit:
                trade.exit_price = trade.take_profit
                trade.current_price = trade.take_profit
                pnl, pnl_percentage = trade.calculate_pnl(trade.take_profit)
                trade.profit_loss = pnl
                trade.profit_loss_percentage = pnl_percentage
                trade.status = 'take_profit_hit'
                trade.closed_at = timezone.now()
                trade.save()
                
                TradeHistory.objects.create(
                    user=request.user,
                    asset=trade.asset,
                    trade_type=trade.trade_type,
                    entry_price=trade.entry_price,
                    exit_price=trade.take_profit,
                    quantity=trade.quantity,
                    profit_loss=pnl,
                    profit_loss_percentage=pnl_percentage,
                    close_reason='take_profit',
                    opened_at=trade.created_at
                )
                
                serializer = TradeSerializer(trade)
                return Response(serializer.data)
        
        # Just update current price
        trade.current_price = current_price
        pnl, pnl_percentage = trade.calculate_pnl(current_price)
        trade.profit_loss = pnl
        trade.profit_loss_percentage = pnl_percentage
        trade.save()
        
        serializer = TradeSerializer(trade)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def open_trades(self, request):
        """Get all open trades"""
        trades = self.get_queryset().filter(status='open')
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def closed_trades(self, request):
        """Get all closed trades"""
        trades = self.get_queryset().exclude(status='open')
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get trade history"""
        history = TradeHistory.objects.filter(user=request.user)
        serializer = TradeHistorySerializer(history, many=True)
        return Response(serializer.data)

# Crypto-specific endpoints for frontend compatibility
from rest_framework.decorators import api_view, permission_classes
from decimal import Decimal
from django.db import transaction as db_transaction
from accounts.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crypto_buy(request):
    """
    Buy cryptocurrency - creates a crypto investment record
    """
    coin = request.data.get('coin', '').upper()
    amount = Decimal(str(request.data.get('amount', 0)))
    price = Decimal(str(request.data.get('price', 0)))
    
    if not all([coin, amount, price]):
        return Response({
            'success': False,
            'message': 'Missing required fields: coin, amount, price'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check user balance
    if request.user.balance < amount:
        return Response({
            'success': False,
            'message': 'Insufficient balance'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    quantity = amount / price
    
    with db_transaction.atomic():
        # Create crypto investment (using Trade model for now)
        crypto_investment = Trade.objects.create(
            user=request.user,
            asset=coin,
            trade_type='buy',
            entry_price=price,
            current_price=price,
            quantity=quantity,
            amount=amount,
            status='open'
        )
        
        # Deduct from user balance
        request.user.balance -= amount
        request.user.save()
        
        # Create transaction record
        from transactions.models import Transaction
        Transaction.objects.create(
            user=request.user,
            transaction_type='investment',
            amount=amount,
            net_amount=amount,
            status='completed',
            reference=f"CRYPTO-BUY-{crypto_investment.id}",
            description=f"Crypto purchase: {quantity:.8f} {coin} at ${price}"
        )
        
        # Create notification
        from notifications.models import Notification
        Notification.create_notification(
            user=request.user,
            title="Crypto Purchase Completed",
            message=f"Successfully purchased {quantity:.8f} {coin} for ${amount}",
            notification_type='success'
        )
    
    return Response({
        'data': {
            'investment': {
                'id': crypto_investment.id,
                'type': 'crypto',
                'coin': coin,
                'amount': str(amount),
                'quantity': str(quantity),
                'price_at_purchase': str(price),
                'status': 'active',
                'date': crypto_investment.created_at.isoformat()
            },
            'transaction': {
                'id': crypto_investment.id,
                'type': 'Crypto Purchase',
                'amount': str(amount),
                'asset': coin,
                'quantity': str(quantity),
                'price': str(price),
                'status': 'completed',
                'date': crypto_investment.created_at.isoformat()
            },
            'new_balance': str(request.user.balance),
            'message': 'Crypto purchase successful'
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crypto_sell(request):
    """
    Sell cryptocurrency - closes crypto investment
    """
    investment_id = request.data.get('investment_id')
    coin = request.data.get('coin', '').upper()
    amount = Decimal(str(request.data.get('amount', 0)))
    price = Decimal(str(request.data.get('price', 0)))
    quantity = Decimal(str(request.data.get('quantity', 0)))
    
    if not all([investment_id, coin, amount, price, quantity]):
        return Response({
            'success': False,
            'message': 'Missing required fields: investment_id, coin, amount, price, quantity'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the crypto investment
        crypto_investment = Trade.objects.get(
            id=investment_id, 
            user=request.user, 
            asset=coin,
            status='open'
        )
    except Trade.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Crypto investment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if selling quantity is valid
    if quantity > crypto_investment.quantity:
        return Response({
            'success': False,
            'message': 'Cannot sell more than you own'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    with db_transaction.atomic():
        # Calculate profit/loss
        profit_loss = (price - crypto_investment.entry_price) * quantity
        
        # Close the trade or update quantity
        if quantity == crypto_investment.quantity:
            # Selling all - close the investment
            crypto_investment.exit_price = price
            crypto_investment.profit_loss = profit_loss
            crypto_investment.status = 'closed'
            crypto_investment.closed_at = timezone.now()
            crypto_investment.save()
            
            # Move to trade history
            TradeHistory.objects.create(
                user=request.user,
                asset=coin,
                trade_type='buy',
                entry_price=crypto_investment.entry_price,
                exit_price=price,
                quantity=quantity,
                amount=crypto_investment.amount,
                profit_loss=profit_loss,
                profit_loss_percentage=(profit_loss / crypto_investment.amount) * 100,
                close_reason='manual',
                opened_at=crypto_investment.created_at,
                closed_at=timezone.now()
            )
        else:
            # Partial sell - update the investment
            remaining_quantity = crypto_investment.quantity - quantity
            remaining_amount = remaining_quantity * crypto_investment.entry_price
            
            crypto_investment.quantity = remaining_quantity
            crypto_investment.amount = remaining_amount
            crypto_investment.save()
        
        # Credit user balance
        request.user.balance += amount
        request.user.save()
        
        # Create transaction record
        from transactions.models import Transaction
        Transaction.objects.create(
            user=request.user,
            transaction_type='profit' if profit_loss > 0 else 'withdrawal',
            amount=amount,
            net_amount=amount,
            status='completed',
            reference=f"CRYPTO-SELL-{crypto_investment.id}",
            description=f"Crypto sale: {quantity:.8f} {coin} at ${price}"
        )
        
        # Create notification
        from notifications.models import Notification
        notification_type = 'success' if profit_loss >= 0 else 'warning'
        Notification.create_notification(
            user=request.user,
            title="Crypto Sale Completed",
            message=f"Sold {quantity:.8f} {coin} for ${amount}. P&L: ${profit_loss:.2f}",
            notification_type=notification_type
        )
    
    return Response({
        'data': {
            'transaction': {
                'id': crypto_investment.id,
                'type': 'Crypto Sale',
                'amount': str(amount),
                'asset': coin,
                'quantity': str(quantity),
                'price': str(price),
                'status': 'completed',
                'date': timezone.now().isoformat()
            },
            'new_balance': str(request.user.balance),
            'updated_investment': {
                'id': crypto_investment.id,
                'quantity': str(crypto_investment.quantity),
                'amount': str(crypto_investment.amount)
            } if crypto_investment.status == 'open' else None,
            'profit_loss': str(profit_loss),
            'message': 'Crypto sale successful'
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crypto_prices(request):
    """
    Get crypto prices - mock data for now, replace with real API later
    """
    # Mock prices - replace with real API integration when ready
    prices = {
        'BTC': {
            'price': 65000.00,
            'change24h': 2.1,
            'change7d': -1.5,
            'change30d': 8.7
        },
        'ETH': {
            'price': 3200.00,
            'change24h': 1.8,
            'change7d': 3.2,
            'change30d': 15.4
        },
        'EXACOIN': {
            'price': 60.00,
            'change24h': 45.2,
            'change7d': 12.8,
            'change30d': 89.5
        },
        'USDT': {
            'price': 1.00,
            'change24h': 0.0,
            'change7d': 0.0,
            'change30d': 0.0
        }
    }
    
    return Response({
        'data': prices
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_crypto_portfolio(request):
    """
    Get user's crypto portfolio
    """
    crypto_investments = Trade.objects.filter(
        user=request.user,
        status='open'
    ).exclude(asset__in=['gold'])  # Exclude non-crypto assets
    
    portfolio = []
    total_value = Decimal('0')
    total_invested = Decimal('0')
    
    for investment in crypto_investments:
        current_value = investment.quantity * investment.current_price
        profit_loss = current_value - investment.amount
        profit_loss_percentage = (profit_loss / investment.amount) * 100 if investment.amount > 0 else 0
        
        portfolio.append({
            'id': investment.id,
            'type': 'crypto',
            'coin': investment.asset,
            'name': f"{investment.asset} Investment",
            'amount': str(investment.amount),
            'quantity': str(investment.quantity),
            'price_at_purchase': str(investment.entry_price),
            'current_price': str(investment.current_price),
            'current_value': str(current_value),
            'profit_loss': str(profit_loss),
            'profit_loss_percentage': float(profit_loss_percentage),
            'status': 'active',
            'date': investment.created_at.isoformat()
        })
        
        total_value += current_value
        total_invested += investment.amount
    
    total_profit_loss = total_value - total_invested
    total_profit_loss_percentage = (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0
    
    return Response({
        'data': {
            'investments': portfolio,
            'summary': {
                'total_invested': str(total_invested),
                'total_value': str(total_value),
                'total_profit_loss': str(total_profit_loss),
                'total_profit_loss_percentage': float(total_profit_loss_percentage),
                'investment_count': len(portfolio)
            }
        }
    }, status=status.HTTP_200_OK)