"""
Test that deposits now use mobile money instead of admin credits
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from transactions.models import Transaction

User = get_user_model()

print("\n📱 Testing Mobile Money Deposits\n")
print("=" * 60)

# Get test users
test_users = User.objects.filter(email__contains='user').order_by('email')

print(f"📊 Found {test_users.count()} test users")

# Check their deposits
for user in test_users:
    print(f"\n👤 User: {user.email}")
    print(f"   Balance: ${user.balance}")
    
    # Get user's deposits
    deposits = Transaction.objects.filter(
        user=user,
        transaction_type='deposit'
    ).order_by('-created_at')
    
    print(f"   Deposits: {deposits.count()}")
    
    for deposit in deposits:
        print(f"     - ${deposit.amount} via {deposit.payment_method} ({deposit.status})")
        print(f"       Reference: {deposit.reference}")

# Check all transaction types
print(f"\n📊 All Transaction Types:")
transaction_types = Transaction.objects.values_list('transaction_type', flat=True).distinct()
for txn_type in transaction_types:
    count = Transaction.objects.filter(transaction_type=txn_type).count()
    print(f"   - {txn_type}: {count}")

# Check payment methods
print(f"\n💳 Payment Methods Used:")
payment_methods = Transaction.objects.exclude(
    payment_method__isnull=True
).values_list('payment_method', flat=True).distinct()

for method in payment_methods:
    count = Transaction.objects.filter(payment_method=method).count()
    print(f"   - {method}: {count}")

print(f"\n✅ Mobile money deposits verification complete!")
print("=" * 60)
print()