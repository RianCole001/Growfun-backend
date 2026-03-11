"""
Price Feed Service for Binary Trading
Provides real-time price updates for assets
"""
from decimal import Decimal
import random
from .models import TradingAsset, AssetPrice
from django.utils import timezone


class PriceFeedService:
    """Generate and manage asset prices"""
    
    # Base prices for different assets
    BASE_PRICES = {
        'OIL': Decimal('75.50'),
        'GOLD': Decimal('2050.00'),
        'EURUSD': Decimal('1.0850'),
        'GBPUSD': Decimal('1.2650'),
        'BTC': Decimal('65000.00'),
        'ETH': Decimal('3200.00'),
    }
    
    @classmethod
    def get_current_price(cls, asset_symbol):
        """Get current price for an asset"""
        # Try to get latest price from database
        latest_price = AssetPrice.objects.filter(
            asset__symbol=asset_symbol
        ).order_by('-timestamp').first()
        
        if latest_price:
            # Check if price is recent (within last 5 seconds)
            age = (timezone.now() - latest_price.timestamp).total_seconds()
            if age < 5:
                return latest_price.price
        
        # Generate new price if no recent price exists
        return cls.generate_price(asset_symbol)
    
    @classmethod
    def generate_price(cls, asset_symbol):
        """Generate a new price based on random walk"""
        try:
            asset = TradingAsset.objects.get(symbol=asset_symbol)
        except TradingAsset.DoesNotExist:
            return None
        
        # Get last price or use base price
        last_price_obj = AssetPrice.objects.filter(
            asset=asset
        ).order_by('-timestamp').first()
        
        if last_price_obj:
            last_price = last_price_obj.price
        else:
            last_price = cls.BASE_PRICES.get(asset_symbol, Decimal('100.00'))
        
        # Apply random walk with asset's volatility
        volatility = float(asset.volatility)
        change = random.uniform(-volatility, volatility)
        new_price = last_price * (Decimal('1') + Decimal(str(change)))
        
        # Save new price
        AssetPrice.objects.create(asset=asset, price=new_price)
        
        return new_price
    
    @classmethod
    def update_all_prices(cls):
        """Update prices for all active assets"""
        assets = TradingAsset.objects.filter(is_active=True)
        prices = {}
        
        for asset in assets:
            price = cls.generate_price(asset.symbol)
            prices[asset.symbol] = {
                'symbol': asset.symbol,
                'name': asset.name,
                'price': float(price),
                'timestamp': timezone.now().isoformat()
            }
        
        return prices
    
    @classmethod
    def initialize_prices(cls):
        """Initialize base prices for all assets"""
        for symbol, base_price in cls.BASE_PRICES.items():
            try:
                asset = TradingAsset.objects.get(symbol=symbol)
                # Create initial price if none exists
                if not AssetPrice.objects.filter(asset=asset).exists():
                    AssetPrice.objects.create(asset=asset, price=base_price)
            except TradingAsset.DoesNotExist:
                pass
