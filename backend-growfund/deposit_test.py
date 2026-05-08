#!/usr/bin/env python
"""Test depositing $30 to migwibrian316@gmail.com"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from transactions.models import Transaction
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

print("=" * 80)
print("DEPOSIT TEST - $30 to migwibrian316@gmail.com")
print("=" * 80)

# Step 1: Find user
print("\n[STEP 1] Finding user...")
try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    print(f"✓ User found: {user.email}")
    print(f"  ID: {user.id}")
    print(f"  Name: {user.first_name} {user.last_name}")
    print(f"  Current balance: ${user.balance}")
except User.DoesNotExist:
    print(f"✗ User not found: migwibrian316@gmail.com")
    print("\nAvailable users:")
    for u in User.objects.all()[:10]:
        print(f"  - {u.email} (Balance: ${u.balance})")
    exit(1)

# Step 2: Get initial balance
print("\n[STEP 2] Recording initial balance...")
initial_balance = user.balance
print(f"✓ Initial balance: ${initial_balance}")

# Step 3: Credit $30
print("\n[STEP 3] Crediting $30...")
deposit_amount = Decimal('30.00')
user.balance += deposit_amount
user.save()
print(f"✓ Balance updated: ${user.balance}")

# Step 4: Create transaction
print("\n[STEP 4] Creating transaction record...")
transaction = Transaction.objects.create(
    user=user,
    transaction_type='admin_credit',
    amount=deposit_amount,
    net_amount=deposit_amount,
    status='completed',
    reference=f'DEPOSIT-{user.id}-30USD',
    description='Admin deposit - $30 USD',
    completed_at=timezone.now()
)
print(f"✓ Transaction created")
print(f"  ID: {transaction.id}")
print(f"  Type: {transaction.transaction_type}")
print(f"  Amount: ${transaction.amount}")
print(f"  Status: {transaction.status}")
print(f"  Reference: {transaction.reference}")

# Step 5: Verify
print("\n[STEP 5] Verifying...")
user.refresh_from_db()
print(f"✓ User balance verified: ${user.balance}")
print(f"  Initial: ${initial_balance}")
print(f"  Deposit: ${deposit_amount}")
print(f"  Final: ${user.balance}")
print(f"  Expected: ${initial_balance + deposit_amount}")

if user.balance == initial_balance + deposit_amount:
    print(f"✓ BALANCE CORRECT!")
else:
    print(f"✗ Balance mismatch!")

# Step 6: Check transaction in history
print("\n[STEP 6] Checking transaction history...")
transactions = Transaction.objects.filter(user=user, transaction_type='admin_credit')
print(f"✓ Admin credit transactions: {transactions.count()}")
for txn in transactions:
    print(f"  - ${txn.amount} ({txn.status}) - {txn.created_at}")

# Step 7: Summary
print("\n" + "=" * 80)
print("DEPOSIT SUMMARY")
print("=" * 80)
print(f"Email: {user.email}")
print(f"User ID: {user.id}")
print(f"Initial Balance: ${initial_balance}")
print(f"Deposit Amount: ${deposit_amount}")
print(f"Final Balance: ${user.balance}")
print(f"Transaction ID: {transaction.id}")
print(f"Transaction Status: {transaction.status}")
print(f"Transaction Type: {transaction.transaction_type}")
print(f"\n✅ DEPOSIT SUCCESSFUL!")
print("=" * 80)
