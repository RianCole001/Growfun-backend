from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import TradingAsset, BinaryTrade, UserTradingStats, AssetPrice
from .serializers import (
    TradingAssetSerializer, OpenTradeSerializer, BinaryTradeSerializer,
    UserTradingStatsSerializer, AssetPriceSerializer
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
        from demo.models import DemoAccount
        demo_account = DemoAccount.objects.get(user=request.user)
        new_balance = float(demo_account.balance)
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
    """Get trade history for the user (real and demo separated)"""
    # Get query parameters
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    is_demo = request.GET.get('is_demo', 'false').lower() == 'true'
    
    trades = BinaryTrade.objects.filter(
        user=request.user,
        status__in=['won', 'lost'],
        is_demo=is_demo
    ).select_related('asset').order_by('-closed_at')[offset:offset+limit]
    
    serializer = BinaryTradeSerializer(trades, many=True)
    
    total_count = BinaryTrade.objects.filter(
        user=request.user,
        status__in=['won', 'lost'],
        is_demo=is_demo
    ).count()
    
    return Response({
        'success': True,
        'trades': serializer.data,
        'count': len(serializer.data),
        'total': total_count,
        'is_demo': is_demo
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """Get trading statistics for the user"""
    stats, created = UserTradingStats.objects.get_or_create(user=request.user)
    serializer = UserTradingStatsSerializer(stats)
    
    return Response({
        'success': True,
        'stats': serializer.data
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
