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
