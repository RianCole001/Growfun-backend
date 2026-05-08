"""
Test script to verify admin credit endpoint is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

# Get a test user
test_user = User.objects.filter(email='migwibrian316@gmail.com').first()

if test_user:
    print(f"\n=== Testing Admin Credit Endpoint ===")
    print(f"User: {test_user.email}")
    print(f"Current Balance: ${test_user.balance}")
    
    # Test credit
    old_balance = test_user.balance
    test_user.balance += Decimal('10.00')
    test_user.save()
    test_user.refresh_from_db()
    
    print(f"After +$10 credit: ${test_user.balance}")
    print(f"Balance changed: {test_user.balance != old_balance}")
    
    # Check transactions
    from transactions.models import Transaction
    recent_transactions = Transaction.objects.filter(user=test_user).order_by('-created_at')[:5]
    
    print(f"\nRecent Transactions:")
    for trans in recent_transactions:
        print(f"  - {trans.transaction_type}: ${trans.amount} - {trans.status} - {trans.created_at}")
    
    print(f"\n=== Test Complete ===")
else:
    print("Test user not found!")
