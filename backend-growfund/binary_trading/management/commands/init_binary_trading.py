from django.core.management.base import BaseCommand
from binary_trading.models import TradingAsset, HouseEdgeConfig
from binary_trading.price_feed import PriceFeedService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialize binary trading system with default assets and configuration'
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing Binary Trading System...\n')
        
        # Create default house edge config
        config, created = HouseEdgeConfig.objects.get_or_create(
            name='Default',
            defaults={
                'is_active': True,
                'win_streak_3_reduction': Decimal('5.00'),
                'win_streak_5_reduction': Decimal('10.00'),
                'high_amount_threshold': Decimal('1000.00'),
                'high_amount_reduction': Decimal('3.00'),
                'very_high_amount_threshold': Decimal('5000.00'),
                'very_high_amount_reduction': Decimal('5.00'),
                'high_profit_threshold': Decimal('1000.00'),
                'high_profit_reduction': Decimal('10.00'),
                'strike_price_adjustment': Decimal('0.0010'),
                'min_delay_ms': 100,
                'max_delay_ms': 500,
                'max_open_trades_per_user': 10,
                'max_exposure_per_asset': Decimal('5000.00'),
                'max_total_exposure': Decimal('10000.00'),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created default house edge configuration'))
        else:
            self.stdout.write('✓ House edge configuration already exists')
        
        # Create trading assets
        assets_data = [
            {'symbol': 'OIL', 'name': 'Crude Oil', 'asset_type': 'commodity', 'volatility': Decimal('0.0050')},
            {'symbol': 'GOLD', 'name': 'Gold', 'asset_type': 'commodity', 'volatility': Decimal('0.0030')},
            {'symbol': 'EURUSD', 'name': 'EUR/USD', 'asset_type': 'forex', 'volatility': Decimal('0.0020')},
            {'symbol': 'GBPUSD', 'name': 'GBP/USD', 'asset_type': 'forex', 'volatility': Decimal('0.0025')},
            {'symbol': 'BTC', 'name': 'Bitcoin', 'asset_type': 'crypto', 'volatility': Decimal('0.0100')},
            {'symbol': 'ETH', 'name': 'Ethereum', 'asset_type': 'crypto', 'volatility': Decimal('0.0120')},
        ]
        
        for asset_data in assets_data:
            asset, created = TradingAsset.objects.get_or_create(
                symbol=asset_data['symbol'],
                defaults=asset_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created asset: {asset.symbol} - {asset.name}'))
            else:
                self.stdout.write(f'✓ Asset already exists: {asset.symbol}')
        
        # Initialize prices
        self.stdout.write('\nInitializing asset prices...')
        PriceFeedService.initialize_prices()
        self.stdout.write(self.style.SUCCESS('✓ Asset prices initialized'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Binary Trading System initialized successfully!'))
