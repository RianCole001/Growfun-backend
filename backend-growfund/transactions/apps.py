from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def ready(self):
        # Start USDT deposit checker in background thread
        import os
        import sys
        
        # Don't start during migrations, management commands, or collectstatic
        if any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic', 'createsuperuser']):
            return
        
        # Only start in the main process (not during development reloads)
        if os.environ.get('RUN_MAIN') == 'true':
            return
            
        try:
            from .usdt_scheduler import start
            start()
        except Exception as e:
            # Silently fail if database isn't ready yet
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f'USDT scheduler not started: {e}')
