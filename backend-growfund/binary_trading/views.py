from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from decimal import Decimal
from .models import TradingAsset, BinaryTrade, UserTradingStats, AssetPrice
from .serializers import (
    TradingAssetSerializer, OpenTradeSerializer, BinaryTradeSerializer,
    UserTradingStatsSerializer, DemoTradingStatsSerializer, AssetPriceSerializer
)
from .trade_service import TradeExecutionService
from .price_feed import PriceFeedService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assets(request):
    """Get all available trading assets"""
    assets = TradingAsset.objects.filter(is_active=True)
    serializer = TradingAssetSerializer(assets, many=True)
    return Response({
        'success': True,
        'assets': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_asset_price(request, symbol):
    """Get current price for a specific asset"""
    price = PriceFeedService.get_current_price(symbol.upper())
    
    if price is None:
        return Response({
            'success': False,
            'error': 'Asset not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': True,
        'symbol': symbol.upper(),
        'price': float(price),
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_prices(request):
    """Get current prices for all active assets"""
    prices = PriceFeedService.update_all_prices()
    return Response({
        'success': True,
        'prices': prices
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def open_trade(request):
    """Open a new binary trade (real or demo)"""
    serializer = OpenTradeSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    is_demo = data.get('is_demo', False)
    
    # Execute trade
    trade, error = TradeExecutionService.open_trade(
        user=request.user,
        asset_symbol=data['asset_symbol'],
        direction=data['direction'],
        amount=data['amount'],
        expiry_seconds=data['expiry_seconds'],
        is_demo=is_demo
    )
    
    if error:
        return Response({
            'success': False,
            'error': error
        }, status=status.HTTP_400_BAD_REQUEST)
    
    trade_serializer = BinaryTradeSerializer(trade)
    
    # Get appropriate balance
    if is_demo:
        try:
            from demo.models import DemoAccount
            demo_account, _ = DemoAccount.objects.get_or_create(
                user=request.user, defaults={'balance': Decimal('10000.00')}
            )
            new_balance = float(demo_account.balance)
        except Exception:
            new_balance = 0
    else:
        new_balance = float(request.user.balance)
    
    return Response({
        'success': True,
        'message': f'{"Demo" if is_demo else "Real"} trade opened successfully',
        'trade': trade_serializer.data,
        'new_balance': new_balance,
        'is_demo': is_demo
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_trades(request):
    """Get all active trades for the user (real and demo separated)"""
    is_demo = request.GET.get('is_demo', 'false').lower() == 'true'
    
    trades = BinaryTrade.objects.filter(
        user=request.user,
        status='active',
        is_demo=is_demo
    ).select_related('asset')
    
    serializer = BinaryTradeSerializer(trades, many=True)
    
    return Response({
        'success': True,
        'trades': serializer.data,
        'count': trades.count(),
        'is_demo': is_demo
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trade_history(request):
    """
    Get trade history for the user — real and demo are strictly separated.
    Includes won, lost, and cancelled trades.
    """
    limit = min(int(request.GET.get('limit', 50)), 200)
    offset = int(request.GET.get('offset', 0))
    is_demo = request.GET.get('is_demo', 'false').lower() == 'true'

    base_qs = BinaryTrade.objects.filter(
        user=request.user,
        status__in=['won', 'lost', 'cancelled'],
        is_demo=is_demo
    ).select_related('asset').order_by('-closed_at', '-opened_at')

    trades = base_qs[offset:offset + limit]
    serializer = BinaryTradeSerializer(trades, many=True)

    total_count = base_qs.count()

    # Summary for this account type
    from django.db.models import Sum
    won_qs  = base_qs.filter(status='won')
    lost_qs = base_qs.filter(status='lost')
    total_wagered = base_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_won     = won_qs.aggregate(t=Sum('profit_loss'))['t'] or Decimal('0')
    total_lost    = lost_qs.aggregate(t=Sum('profit_loss'))['t'] or Decimal('0')

    return Response({
        'success': True,
        'is_demo': is_demo,
        'trades': serializer.data,
        'count': len(serializer.data),
        'total': total_count,
        'summary': {
            'total_wagered': float(total_wagered),
            'total_won': float(total_won),
            'net_pnl': float(total_won + total_lost),
            'win_count': won_qs.count(),
            'loss_count': lost_qs.count(),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """
    Get trading statistics for the user.
    Returns real and demo stats separately — they never mix.
    """
    is_demo = request.GET.get('is_demo', 'false').lower() == 'true'

    try:
        if is_demo:
            from .models import DemoTradingStats
            stats, _ = DemoTradingStats.objects.get_or_create(user=request.user)
            serializer = DemoTradingStatsSerializer(stats)
        else:
            stats, _ = UserTradingStats.objects.get_or_create(user=request.user)
            serializer = UserTradingStatsSerializer(stats)
        return Response({
            'success': True,
            'is_demo': is_demo,
            'stats': serializer.data
        })
    except Exception as e:
        # Table may not exist yet if migration is pending
        return Response({
            'success': True,
            'is_demo': is_demo,
            'stats': {
                'total_trades': 0, 'total_wins': 0, 'total_losses': 0,
                'current_win_streak': 0, 'max_win_streak': 0, 'win_rate': 0,
                'total_profit': '0.00', 'total_loss': '0.00',
                'net_profit': '0.00', 'total_volume': '0.00',
            }
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def close_expired_trades(request):
    """Manually trigger closing of expired trades (admin only)"""
    results = TradeExecutionService.close_expired_trades()
    return Response({
        'success': True,
        'message': f"Closed {results['closed']} trades, {results['errors']} errors",
        'results': results
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_trade(request, trade_id):
    """
    Close a specific trade by ID.
    Called by the frontend when the countdown timer reaches zero.
    Users can only close their own trades.
    """
    try:
        trade = BinaryTrade.objects.get(id=trade_id, user=request.user)
    except BinaryTrade.DoesNotExist:
        return Response({'success': False, 'error': 'Trade not found'}, status=status.HTTP_404_NOT_FOUND)

    if trade.status != 'active':
        # Already settled — just return current state
        from .serializers import BinaryTradeSerializer
        return Response({'success': True, 'trade': BinaryTradeSerializer(trade).data})

    # Only allow closing if expired or within 2s of expiry (grace window)
    seconds_remaining = (trade.expires_at - timezone.now()).total_seconds()
    if seconds_remaining > 2:
        return Response({
            'success': False,
            'error': f'Trade expires in {int(seconds_remaining)}s'
        }, status=status.HTTP_400_BAD_REQUEST)

    closed_trade, error = TradeExecutionService.close_trade(trade_id)
    if error:
        return Response({'success': False, 'error': error}, status=status.HTTP_400_BAD_REQUEST)

    from .serializers import BinaryTradeSerializer
    if trade.is_demo:
        from demo.models import DemoAccount
        demo_account = DemoAccount.objects.get(user=request.user)
        new_balance = float(demo_account.balance)
    else:
        request.user.refresh_from_db()
        new_balance = float(request.user.balance)

    return Response({
        'success': True,
        'trade': BinaryTradeSerializer(closed_trade).data,
        'new_balance': new_balance,
        'is_demo': closed_trade.is_demo
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_data(request, symbol):
    """
    Return OHLC candlestick data for a trading asset.

    Query params:
      interval  - 1m | 5m | 15m | 30m | 1h | 4h | 1d  (default: 1m)
      limit     - number of candles to return           (default: 100, max: 500)

    Sources (in priority order):
      Crypto  → CoinGecko OHLC API (real market data)
      Gold    → Yahoo Finance GC=F  (real market data)
      Oil     → Yahoo Finance CL=F  (real market data)
      Forex   → Yahoo Finance EURUSD=X etc. (real market data)
      Fallback→ Aggregated stored price ticks (when all APIs unavailable)
    """
    from .chart_service import ChartService

    interval = request.GET.get('interval', '1m')
    valid_intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    if interval not in valid_intervals:
        return Response({
            'success': False,
            'error': f'Invalid interval. Choose from: {", ".join(valid_intervals)}'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = min(int(request.GET.get('limit', 100)), 500)
    except ValueError:
        limit = 100

    candles = ChartService.get_ohlc(symbol.upper(), interval, limit)

    if not candles:
        return Response({
            'success': False,
            'error': f'No chart data available for {symbol.upper()}'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'symbol': symbol.upper(),
        'interval': interval,
        'candles': candles,
        'count': len(candles),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balances(request):
    """Get both real and demo balances"""
    from demo.models import DemoAccount
    
    # Get or create demo account
    demo_account, created = DemoAccount.objects.get_or_create(
        user=request.user,
        defaults={'balance': Decimal('10000.00')}
    )
    
    return Response({
        'success': True,
        'real_balance': float(request.user.balance),
        'demo_balance': float(demo_account.balance)
    })
