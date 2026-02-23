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
    from decimal import Decimal
    import requests
    
    # Get all admin-controlled prices from database
    admin_prices = AdminCryptoPrice.objects.all()
    prices_dict = {}
    
    # Add existing admin prices to dict
    for price in admin_prices:
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
            'updated_by': price.updated_by.email if price.updated_by else None,
            'is_admin_controlled': True
        }
    
    # Fetch other coins from CoinGecko API and create/update them
    try:
        coingecko_url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,cardano,solana,polkadot',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_7d_change': 'true',
            'include_30d_change': 'true'
        }
        
        response = requests.get(coingecko_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Map CoinGecko IDs to our symbols
            coin_mapping = {
                'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin'},
                'ethereum': {'symbol': 'ETH', 'name': 'Ethereum'},
                'binancecoin': {'symbol': 'BNB', 'name': 'Binance Coin'},
                'cardano': {'symbol': 'ADA', 'name': 'Cardano'},
                'solana': {'symbol': 'SOL', 'name': 'Solana'},
                'polkadot': {'symbol': 'DOT', 'name': 'Polkadot'}
            }
            
            for gecko_id, coin_info in coin_mapping.items():
                if gecko_id in data:
                    coin_data = data[gecko_id]
                    symbol = coin_info['symbol']
                    name = coin_info['name']
                    
                    # Get current market price as buy price
                    buy_price = Decimal(str(coin_data.get('usd', 0)))
                    
                    # Calculate sell price (3% lower than buy price for spread)
                    sell_price = buy_price * Decimal('0.97')
                    
                    # Get or create the coin price record
                    admin_price, created = AdminCryptoPrice.objects.get_or_create(
                        coin=symbol,
                        defaults={
                            'name': name,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'change_24h': Decimal(str(coin_data.get('usd_24h_change', 0))),
                            'change_7d': Decimal(str(coin_data.get('usd_7d_change', 0))),
                            'change_30d': Decimal(str(coin_data.get('usd_30d_change', 0))),
                            'is_active': True,
                            'updated_by': request.user
                        }
                    )
                    
                    # If not created, update buy price from API but keep admin-set sell price
                    if not created:
                        admin_price.buy_price = buy_price
                        admin_price.change_24h = Decimal(str(coin_data.get('usd_24h_change', 0)))
                        admin_price.change_7d = Decimal(str(coin_data.get('usd_7d_change', 0)))
                        admin_price.change_30d = Decimal(str(coin_data.get('usd_30d_change', 0)))
                        admin_price.updated_by = request.user
                        admin_price.save()
                    
                    # Add to response dict
                    prices_dict[symbol] = {
                        'id': admin_price.id,
                        'coin': admin_price.coin,
                        'name': admin_price.name,
                        'buy_price': str(admin_price.buy_price),
                        'sell_price': str(admin_price.sell_price),
                        'spread': str(admin_price.spread),
                        'spread_percentage': float(admin_price.spread_percentage),
                        'change_24h': float(admin_price.change_24h),
                        'change_7d': float(admin_price.change_7d),
                        'change_30d': float(admin_price.change_30d),
                        'is_active': admin_price.is_active,
                        'last_updated': admin_price.last_updated.isoformat(),
                        'updated_by': admin_price.updated_by.email if admin_price.updated_by else None,
                        'is_admin_controlled': symbol == 'EXACOIN'  # Only EXACOIN is fully admin controlled
                    }
    
    except Exception as e:
        print(f"⚠️ CoinGecko API error: {e}")
        # Continue with existing data if API fails
    
    return Response({
        'success': True,
        'data': prices_dict
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_update_crypto_price(request):
    """
    Update crypto price (admin only)
    
    For EXACOIN: Admin can set both buy and sell prices
    For other coins: Admin can only set sell price, buy price comes from API
    
    Request body:
    {
        "coin": "BTC",
        "buy_price": 65000.00,  // Optional for non-EXACOIN coins
        "sell_price": 63000.00,  // Required
        "change24h": 2.5  // Optional
    }
    """
    # Extract data from request
    coin = request.data.get('coin', '').upper()
    buy_price = request.data.get('buy_price')
    sell_price = request.data.get('sell_price')
    change24h = request.data.get('change24h', 0)
    change7d = request.data.get('change7d', 0)
    change30d = request.data.get('change30d', 0)
    
    # Validate required fields
    if not coin:
        return Response({
            'success': False,
            'error': 'Coin is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not sell_price:
        return Response({
            'success': False,
            'error': 'Sell price is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # For EXACOIN, buy_price is required. For others, it's optional (comes from API)
    if coin == 'EXACOIN' and not buy_price:
        return Response({
            'success': False,
            'error': 'Buy price is required for EXACOIN'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate price values
    try:
        if buy_price:
            buy_price = float(buy_price)
        sell_price = float(sell_price)
        change24h = float(change24h)
        change7d = float(change7d) if change7d else 0
        change30d = float(change30d) if change30d else 0
    except (ValueError, TypeError):
        return Response({
            'success': False,
            'error': 'Invalid price or change values'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    with db_transaction.atomic():
        try:
            # Get existing price record
            crypto_price = AdminCryptoPrice.objects.get(coin=coin)
            
            # Update sell price (always allowed)
            crypto_price.sell_price = Decimal(str(sell_price))
            
            # Update buy price only for EXACOIN or if provided
            if coin == 'EXACOIN' and buy_price:
                crypto_price.buy_price = Decimal(str(buy_price))
                crypto_price.change_24h = Decimal(str(change24h))
                crypto_price.change_7d = Decimal(str(change7d))
                crypto_price.change_30d = Decimal(str(change30d))
            elif buy_price:  # For other coins, update buy price if provided
                crypto_price.buy_price = Decimal(str(buy_price))
            
            crypto_price.is_active = True
            crypto_price.updated_by = request.user
            crypto_price.save()
            
        except AdminCryptoPrice.DoesNotExist:
            # Create new price record if it doesn't exist
            if not buy_price:
                return Response({
                    'success': False,
                    'error': f'Buy price is required to create new {coin} price record'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            crypto_price = AdminCryptoPrice.objects.create(
                coin=coin,
                name=coin,
                buy_price=Decimal(str(buy_price)),
                sell_price=Decimal(str(sell_price)),
                change_24h=Decimal(str(change24h)),
                change_7d=Decimal(str(change7d)),
                change_30d=Decimal(str(change30d)),
                is_active=True,
                updated_by=request.user
            )
        
        # Log price change to history
        CryptoPriceHistory.objects.create(
            coin=coin,
            buy_price=crypto_price.buy_price,
            sell_price=crypto_price.sell_price,
            change_24h=crypto_price.change_24h,
            updated_by=request.user
        )
    
    # Return in exact frontend format
    return Response({
        'data': {
            'coin': crypto_price.coin,
            'buy_price': float(f"{crypto_price.buy_price:.2f}"),
            'sell_price': float(f"{crypto_price.sell_price:.2f}"),
            'change24h': float(f"{crypto_price.change_24h:.2f}"),
            'change7d': float(f"{crypto_price.change_7d:.2f}"),
            'change30d': float(f"{crypto_price.change_30d:.2f}"),
            'updated_at': crypto_price.last_updated.isoformat()
        },
        'success': True
    }, status=status.HTTP_200_OK)


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