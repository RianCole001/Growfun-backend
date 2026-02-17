from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction as db_transaction
from decimal import Decimal

from .admin_models import AdminCryptoPrice, CryptoPriceHistory
from .serializers import (
    AdminCryptoPriceSerializer, UpdateCryptoPriceSerializer,
    PublicCryptoPriceSerializer, CryptoPriceHistorySerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_get_crypto_prices(request):
    """Get all crypto prices for admin management"""
    prices = AdminCryptoPrice.objects.all()
    
    # Format as dictionary with coin as key
    prices_dict = {}
    for price in prices:
        prices_dict[price.coin] = {
            'id': price.id,
            'coin': price.coin,
            'name': price.name,
            'buy_price': str(price.buy_price),
            'sell_price': str(price.sell_price),
            'spread': str(price.spread),
            'spread_percentage': float(price.spread_percentage),
            'change_24h': float(price.change_24h),
            'change_7d': float(price.change_7d),
            'change_30d': float(price.change_30d),
            'is_active': price.is_active,
            'last_updated': price.last_updated.isoformat(),
            'updated_by': price.updated_by.email if price.updated_by else None
        }
    
    return Response({
        'success': True,
        'data': prices_dict
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_update_crypto_price(request):
    """
    Update EXACOIN price (admin only)
    
    This endpoint is ONLY for EXACOIN - the admin-controlled coin.
    All other coins (BTC, ETH, BNB, ADA, SOL, DOT) are fetched from CoinGecko API.
    
    Request body:
    {
        "coin": "EXACOIN",
        "price": 130.00,
        "change24h": 48.5
    }
    
    Response format matches frontend requirements:
    {
        "data": {
            "coin": "EXACOIN",
            "price": 130.00,
            "change24h": 48.50,
            "updated_at": "2026-02-17T10:30:00Z"
        },
        "success": true
    }
    """
    # Extract data from request
    coin = request.data.get('coin', 'EXACOIN').upper()
    price = request.data.get('price')
    change24h = request.data.get('change24h', 0)
    change7d = request.data.get('change7d', 0)
    change30d = request.data.get('change30d', 0)
    
    # Validate required fields
    if not price:
        return Response({
            'success': False,
            'error': 'Price is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate price is a number
    try:
        price = float(price)
        change24h = float(change24h)
        change7d = float(change7d) if change7d else 0
        change30d = float(change30d) if change30d else 0
    except (ValueError, TypeError):
        return Response({
            'success': False,
            'error': 'Invalid price or change values'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    with db_transaction.atomic():
        # Get or create EXACOIN price record
        exacoin, created = AdminCryptoPrice.objects.get_or_create(
            coin=coin,
            defaults={
                'name': coin,
                'buy_price': Decimal(str(price)),
                'sell_price': Decimal(str(price)),  # Same as buy for EXACOIN
                'change_24h': Decimal(str(change24h)),
                'change_7d': Decimal(str(change7d)),
                'change_30d': Decimal(str(change30d)),
                'is_active': True,
                'updated_by': request.user
            }
        )
        
        if not created:
            # Update existing EXACOIN price
            exacoin.buy_price = Decimal(str(price))
            exacoin.sell_price = Decimal(str(price))
            exacoin.change_24h = Decimal(str(change24h))
            exacoin.change_7d = Decimal(str(change7d))
            exacoin.change_30d = Decimal(str(change30d))
            exacoin.is_active = True
            exacoin.updated_by = request.user
            exacoin.save()
        
        # Log price change to history
        CryptoPriceHistory.objects.create(
            coin=coin,
            buy_price=exacoin.buy_price,
            sell_price=exacoin.sell_price,
            change_24h=exacoin.change_24h,
            updated_by=request.user
        )
    
    # Return in exact frontend format
    return Response({
        'data': {
            'coin': exacoin.coin,
            'price': float(f"{exacoin.buy_price:.2f}"),
            'change24h': float(f"{exacoin.change_24h:.2f}"),
            'change7d': float(f"{exacoin.change_7d:.2f}"),
            'change30d': float(f"{exacoin.change_30d:.2f}"),
            'updated_at': exacoin.last_updated.isoformat()
        },
        'success': True
    }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_toggle_crypto_active(request, coin):
    """Enable/disable trading for a specific coin"""
    try:
        price = AdminCryptoPrice.objects.get(coin=coin.upper())
        price.is_active = not price.is_active
        price.updated_by = request.user
        price.save()
        
        return Response({
            'success': True,
            'message': f'{coin} trading {"enabled" if price.is_active else "disabled"}',
            'data': {
                'coin': price.coin,
                'is_active': price.is_active
            }
        }, status=status.HTTP_200_OK)
    
    except AdminCryptoPrice.DoesNotExist:
        return Response({
            'success': False,
            'error': f'Price for {coin} not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_get_price_history(request, coin):
    """Get price change history for a specific coin"""
    history = CryptoPriceHistory.objects.filter(coin=coin.upper())[:50]  # Last 50 changes
    serializer = CryptoPriceHistorySerializer(history, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_bulk_update_prices(request):
    """Bulk update multiple crypto prices"""
    prices_data = request.data.get('prices', [])
    
    if not prices_data:
        return Response({
            'success': False,
            'error': 'No prices provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    updated = []
    errors = []
    
    with db_transaction.atomic():
        for price_data in prices_data:
            serializer = UpdateCryptoPriceSerializer(data=price_data)
            
            if serializer.is_valid():
                data = serializer.validated_data
                coin = data['coin'].upper()
                
                price, created = AdminCryptoPrice.objects.update_or_create(
                    coin=coin,
                    defaults={
                        'buy_price': data['buy_price'],
                        'sell_price': data['sell_price'],
                        'change_24h': data.get('change_24h', 0),
                        'change_7d': data.get('change_7d', 0),
                        'change_30d': data.get('change_30d', 0),
                        'updated_by': request.user
                    }
                )
                
                updated.append(coin)
                
                # Log to history
                CryptoPriceHistory.objects.create(
                    coin=coin,
                    buy_price=price.buy_price,
                    sell_price=price.sell_price,
                    change_24h=price.change_24h,
                    updated_by=request.user
                )
            else:
                errors.append({
                    'coin': price_data.get('coin'),
                    'errors': serializer.errors
                })
    
    return Response({
        'success': len(errors) == 0,
        'message': f'Updated {len(updated)} prices',
        'updated': updated,
        'errors': errors if errors else None
    }, status=status.HTTP_200_OK if len(errors) == 0 else status.HTTP_207_MULTI_STATUS)