"""
Management command to run the continuous price generator.
This should be run as a background process alongside the Django server.

Usage:
    python manage.py run_price_generator
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from binary_trading.price_generator import PriceGeneratorManager
from binary_trading.models import TradingAsset, AssetPrice
import time
import random


class Command(BaseCommand):
    help = 'Run continuous price generation for all active trading assets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=float,
            default=0.5,
            help='Tick generation interval in seconds (default: 0.5)'
        )
        parser.add_argument(
            '--adjust-interval',
            type=int,
            default=30,
            help='How often to adjust for trade imbalance in seconds (default: 30)'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        adjust_interval = options['adjust_interval']
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting price generator (tick interval: {interval}s, adjust interval: {adjust_interval}s)'
        ))
        
        manager = PriceGeneratorManager()
        
        # Initialize generators for all active assets
        assets = TradingAsset.objects.filter(is_active=True)
        for asset in assets:
            # Get latest price or use default
            latest = AssetPrice.objects.filter(asset=asset).order_by('-timestamp').first()
            base_price = latest.price if latest else asset.min_trade_amount * 10
            
            generator = manager.get_generator(asset.symbol, base_price, asset.volatility)
            self.stdout.write(f'  Initialized {asset.symbol} at ${base_price}')
        
        self.stdout.write(self.style.SUCCESS('All generators initialized. Starting price stream...'))
        
        last_adjust = time.time()
        tick_count = 0
        
        try:
            while True:
                start_time = time.time()
                
                # Generate ticks for all assets
                ticks = manager.update_all_generators()
                
                # Store ticks in database
                for symbol, tick in ticks.items():
                    try:
                        asset = TradingAsset.objects.get(symbol=symbol)
                        AssetPrice.objects.create(asset=asset, price=tick['price'])
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'Failed to store price for {symbol}: {e}'
                        ))
                
                tick_count += 1
                
                # Periodically adjust generators based on trade imbalance
                if time.time() - last_adjust >= adjust_interval:
                    self.stdout.write(f'Adjusting generators for trade imbalance (tick #{tick_count})...')
                    for symbol in ticks.keys():
                        manager.adjust_generator_for_trades(symbol)
                    last_adjust = time.time()
                
                # Log progress every 100 ticks
                if tick_count % 100 == 0:
                    self.stdout.write(f'Generated {tick_count} ticks...')
                
                # Sleep for remaining interval time
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                # Add small random jitter for realism
                sleep_time += random.uniform(-0.05, 0.05)
                sleep_time = max(0.1, sleep_time)
                
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping price generator...'))
            self.stdout.write(self.style.SUCCESS(f'Generated {tick_count} total ticks'))
