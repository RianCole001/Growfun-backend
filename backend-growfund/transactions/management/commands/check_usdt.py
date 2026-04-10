from django.core.management.base import BaseCommand
from transactions.tron_monitor import process_usdt_deposits


class Command(BaseCommand):
    help = 'Check for confirmed USDT TRC20 deposits'

    def handle(self, *args, **kwargs):
        process_usdt_deposits()
        self.stdout.write(self.style.SUCCESS('USDT deposit check complete'))
