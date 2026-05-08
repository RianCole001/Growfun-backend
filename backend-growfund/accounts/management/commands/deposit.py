from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from transactions.models import Transaction
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Deposit money to a user account'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('amount', type=float)

    def handle(self, *args, **options):
        email = options['email']
        amount = Decimal(str(options['amount']))

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {email}'))
            return

        initial_balance = user.balance
        user.balance += amount
        user.save()

        Transaction.objects.create(
            user=user,
            transaction_type='admin_credit',
            amount=amount,
            net_amount=amount,
            status='completed',
            reference=f'DEPOSIT-{user.id}-{int(amount)}',
            description=f'Admin deposit - ${amount}',
            completed_at=timezone.now()
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Deposit successful!'))
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Initial balance: ${initial_balance}')
        self.stdout.write(f'Deposit amount: ${amount}')
        self.stdout.write(f'Final balance: ${user.balance}')
