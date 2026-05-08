"""
Management command to reset all data except users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from transactions.models import Transaction
from investments.models import Trade, CapitalInvestmentPlan
from notifications.models import Notification
from demo.models import DemoAccount, DemoInvestment, DemoTransaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete all data except users (keeps user accounts intact)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  WARNING: This will delete ALL data except user accounts!\n'
                    'This includes:\n'
                    '  - All transactions (deposits, withdrawals, investments)\n'
                    '  - All trades (crypto)\n'
                    '  - All capital investment plans\n'
                    '  - All notifications\n'
                    '  - All demo accounts and data\n'
                    '\nUser accounts will be preserved but balances will be reset to 0.\n'
                    '\nTo proceed, run: python manage.py reset_data --confirm\n'
                )
            )
            return

        self.stdout.write(self.style.WARNING('\n🗑️  Starting data deletion...\n'))

        # Count before deletion
        transaction_count = Transaction.objects.count()
        trade_count = Trade.objects.count()
        capital_plan_count = CapitalInvestmentPlan.objects.count()
        notification_count = Notification.objects.count()
        demo_account_count = DemoAccount.objects.count()
        demo_investment_count = DemoInvestment.objects.count()
        demo_transaction_count = DemoTransaction.objects.count()
        user_count = User.objects.count()

        self.stdout.write(f'📊 Current data counts:')
        self.stdout.write(f'  - Users: {user_count} (will be preserved)')
        self.stdout.write(f'  - Transactions: {transaction_count}')
        self.stdout.write(f'  - Trades: {trade_count}')
        self.stdout.write(f'  - Capital Plans: {capital_plan_count}')
        self.stdout.write(f'  - Notifications: {notification_count}')
        self.stdout.write(f'  - Demo Accounts: {demo_account_count}')
        self.stdout.write(f'  - Demo Investments: {demo_investment_count}')
        self.stdout.write(f'  - Demo Transactions: {demo_transaction_count}')

        # Delete data
        self.stdout.write(self.style.WARNING('\n🗑️  Deleting data...\n'))

        # Delete transactions
        Transaction.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {transaction_count} transactions'))

        # Delete trades
        Trade.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {trade_count} trades'))

        # Delete capital plans
        CapitalInvestmentPlan.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {capital_plan_count} capital plans'))

        # Delete notifications
        Notification.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {notification_count} notifications'))

        # Delete demo data
        DemoTransaction.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {demo_transaction_count} demo transactions'))
        
        DemoInvestment.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {demo_investment_count} demo investments'))
        
        DemoAccount.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Deleted {demo_account_count} demo accounts'))

        # Reset user balances to 0
        users_updated = User.objects.update(balance=0)
        self.stdout.write(self.style.SUCCESS(f'✅ Reset balances for {users_updated} users to $0.00'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ Data reset complete!\n'
                f'  - Kept {user_count} user accounts\n'
                f'  - All other data has been deleted\n'
                f'  - All user balances reset to $0.00\n'
            )
        )
