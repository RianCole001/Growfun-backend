"""
Management command to run the bot trading simulator.
Creates realistic trading activity for marketing and UX.

Usage:
    python manage.py run_bot_simulator --trades-per-minute 5
"""
from django.core.management.base import BaseCommand
from binary_trading.bot_simulator import BotSimulator
import time


class Command(BaseCommand):
    help = 'Run continuous bot trading simulation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--trades-per-minute',
            type=float,
            default=3.0,
            help='Average number of bot trades per minute (default: 3.0)'
        )
        parser.add_argument(
            '--create-bots',
            type=int,
            default=0,
            help='Create this many bot users before starting (default: 0)'
        )
    
    def handle(self, *args, **options):
        trades_per_minute = options['trades_per_minute']
        create_bots = options['create_bots']
        
        # Create bots if requested
        if create_bots > 0:
            self.stdout.write(f'Creating {create_bots} bot users...')
            bots = BotSimulator.create_bot_fleet(create_bots)
            self.stdout.write(self.style.SUCCESS(f'Created {len(bots)} bots'))
        
        # Check if we have any bots
        bot_count = BotSimulator.get_bot_users().count()
        if bot_count == 0:
            self.stdout.write(self.style.WARNING('No bot users found. Creating 5 bots...'))
            BotSimulator.create_bot_fleet(5)
            bot_count = 5
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting bot simulator with {bot_count} bots '
            f'({trades_per_minute} trades/min)'
        ))
        
        # Calculate interval between trades
        interval = 60.0 / trades_per_minute
        
        total_trades = 0
        total_failed = 0
        
        try:
            while True:
                start_time = time.time()
                
                # Simulate a trade
                trade = BotSimulator.simulate_bot_trade()
                
                if trade:
                    total_trades += 1
                    self.stdout.write(
                        f'[{total_trades}] {trade.user.email} - '
                        f'{trade.asset.symbol} {trade.direction.upper()} '
                        f'${trade.amount} ({trade.expiry_seconds}s)'
                    )
                else:
                    total_failed += 1
                    if total_failed % 10 == 0:
                        self.stdout.write(self.style.WARNING(
                            f'Failed trades: {total_failed}'
                        ))
                
                # Sleep for remaining interval time
                elapsed = time.time() - start_time
                sleep_time = max(0.5, interval - elapsed)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping bot simulator...'))
            self.stdout.write(self.style.SUCCESS(
                f'Total trades: {total_trades}, Failed: {total_failed}'
            ))
