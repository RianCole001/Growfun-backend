"""
Management command to continuously close expired trades.
This should be run as a background process.

Usage:
    python manage.py close_expired_trades
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from binary_trading.trade_service import TradeExecutionService
import time


class Command(BaseCommand):
    help = 'Continuously close expired binary trades'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=1,
            help='Check interval in seconds (default: 1)'
        )
    
    def handle(self, *args, **options):
        interval = options['interval']
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting expired trade closer (check interval: {interval}s)'
        ))
        
        total_closed = 0
        total_errors = 0
        
        try:
            while True:
                start_time = time.time()
                
                # Close expired trades
                results = TradeExecutionService.close_expired_trades()
                
                closed = results['closed']
                errors = results['errors']
                
                if closed > 0 or errors > 0:
                    total_closed += closed
                    total_errors += errors
                    
                    self.stdout.write(
                        f'[{timezone.now().strftime("%H:%M:%S")}] '
                        f'Closed: {closed}, Errors: {errors} '
                        f'(Total: {total_closed} closed, {total_errors} errors)'
                    )
                    
                    # Log error details if any
                    if errors > 0 and results.get('error_details'):
                        for error_detail in results['error_details']:
                            self.stdout.write(self.style.ERROR(
                                f'  Trade {error_detail["trade_id"]}: {error_detail["error"]}'
                            ))
                
                # Sleep for remaining interval time
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping trade closer...'))
            self.stdout.write(self.style.SUCCESS(
                f'Total closed: {total_closed}, Total errors: {total_errors}'
            ))
