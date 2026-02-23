from django.core.management.base import BaseCommand
from settings_app.models import PlatformSettings
from decimal import Decimal


class Command(BaseCommand):
    help = 'Setup initial platform settings'

    def handle(self, *args, **options):
        # Get or create settings
        settings, created = PlatformSettings.objects.get_or_create(
            id=1,
            defaults={
                'platform_name': 'GrowFund',
                'platform_email': 'support@growfund.com',
                'maintenance_mode': False,
                'min_deposit': Decimal('100.00'),
                'max_deposit': Decimal('100000.00'),
                'min_withdrawal': Decimal('50.00'),
                'max_withdrawal': Decimal('50000.00'),
                'deposit_fee': Decimal('0.00'),
                'withdrawal_fee': Decimal('2.00'),
                'auto_approve_deposits': False,
                'auto_approve_withdrawals': False,
                'auto_approve_deposit_limit': Decimal('1000.00'),
                'auto_approve_withdrawal_limit': Decimal('500.00'),
                'email_notifications': True,
                'sms_notifications': False,
                'referral_bonus': Decimal('50.00'),
                'min_capital_plan_investment': Decimal('500.00'),
                'min_real_estate_investment': Decimal('1000.00'),
                'min_crypto_investment': Decimal('50.00'),
                # Capital Plan Individual Minimums
                'capital_basic_min': Decimal('100.00'),
                'capital_standard_min': Decimal('500.00'),
                'capital_advance_min': Decimal('2000.00'),
                # Real Estate Individual Minimums
                'real_estate_starter_min': Decimal('1000.00'),
                'real_estate_premium_min': Decimal('5000.00'),
                'real_estate_luxury_min': Decimal('20000.00'),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Platform settings created successfully!'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Platform settings already exist'))
        
        self.stdout.write(self.style.SUCCESS(f'\nCurrent Settings:'))
        self.stdout.write(f'  Platform Name: {settings.platform_name}')
        self.stdout.write(f'  Support Email: {settings.platform_email}')
        self.stdout.write(f'  Maintenance Mode: {settings.maintenance_mode}')
        self.stdout.write(f'  Min Deposit: ${settings.min_deposit}')
        self.stdout.write(f'  Max Deposit: ${settings.max_deposit}')
        self.stdout.write(f'  Min Withdrawal: ${settings.min_withdrawal}')
        self.stdout.write(f'  Max Withdrawal: ${settings.max_withdrawal}')
        self.stdout.write(f'  Deposit Fee: {settings.deposit_fee}%')
        self.stdout.write(f'  Withdrawal Fee: {settings.withdrawal_fee}%')
        self.stdout.write(f'  Referral Bonus: ${settings.referral_bonus}')
        self.stdout.write(f'  Auto-approve Deposits: {settings.auto_approve_deposits}')
        self.stdout.write(f'  Auto-approve Withdrawals: {settings.auto_approve_withdrawals}')
        self.stdout.write(f'  Min Capital Plan Investment: ${settings.min_capital_plan_investment}')
        self.stdout.write(f'  Min Real Estate Investment: ${settings.min_real_estate_investment}')
        self.stdout.write(f'  Min Crypto Investment: ${settings.min_crypto_investment}')
