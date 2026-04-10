from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def ready(self):
        # Start USDT deposit checker in background thread
        import os
        # Only start in the main process (not during migrations or management commands)
        if os.environ.get('RUN_MAIN') != 'true':
            try:
                from .usdt_scheduler import start
                start()
            except Exception:
                pass
