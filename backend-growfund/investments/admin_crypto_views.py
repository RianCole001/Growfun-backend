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
    """Update or create crypto price (admin only) - Enhanced for EXACOIN"""
    serializer = UpdateCryptoPriceSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    coin = data['coin'].upper()
    
    with db_transaction.atomic():
        # Get or create price record
        price, created = AdminCryptoPrice.objects.get_or_create(
            coin=coin,
            defaults={
                'name': coin,
                'buy_price': data['buy_price'],
                'sell_price': data['sell_price'],
                'change_24h': data.get('change_24h', 0),
                'change_7d': data.get('change_7d', 0),
                'change_30d': data.get('change_30d', 0),
                'updated_by': request.user
            }
        )
        
        if not created:
            # Update existing price
            price.buy_price = data['buy_price']
            price.sell_price = data['sell_price']
            price.change_24h = data.get('change_24h', price.change_24h)
            price.change_7d = data.get('change_7d', price.change_7d)
            price.change_30d = data.get('change_30d', price.change_30d)
            price.updated_by = request.user
            price.save()
        
        # Log price change to history
        CryptoPriceHistory.objects.create(
            coin=coin,
            buy_price=price.buy_price,
            sell_price=price.sell_price,
            change_24h=price.change_24h,
            updated_by=request.user
        )
        
        # Create notification for admin
        try:
            from notifications.models import Notification
            action = "created" if created else "updated"
            Notification.create_notification(
                user=request.user,
                title=f"Crypto Price {action.title()}",
                message=f"{coin} price {action}: Buy ${price.buy_price}, Sell ${price.sell_price} (Spread: {price.spread_percentage:.2f}%)",
                notification_type='info'
            )
        except Exception as e:
            print(f"Warning: Could not create notification: {e}")
    
    # Return in frontend format
    return Response({
        'data': {
            'coin': price.coin,
            'price': float(f"{price.buy_price:.2f}"),  # Format with 2 decimals
            'change24h': float(f"{price.change_24h:.2f}"),  # Format with decimals
            'updated_at': price.last_updated.isoformat()
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