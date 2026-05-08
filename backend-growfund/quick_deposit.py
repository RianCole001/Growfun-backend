import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from transactions.models import Transaction
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

# Find user
user = User.objects.get(email='migwibrian316@gmail.com')
print(f"User: {user.email}")
print(f"Initial balance: ${user.balance}")

# Deposit $30
user.balance += Decimal('30.00')
user.save()

# Create transaction
Transaction.objects.create(
    user=user,
    transaction_type='admin_credit',
    amount=Decimal('30.00'),
    net_amount=Decimal('30.00'),
    status='completed',
    reference=f'DEPOSIT-{user.id}-30',
    description='Admin deposit - $30',
    completed_at=timezone.now()
)

print(f"Final balance: ${user.balance}")
print("✅ Deposit successful!")
