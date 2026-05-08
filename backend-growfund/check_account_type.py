# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from demo.models import DemoAccount
from transactions.models import Transaction

User = get_user_model()

print("=" * 80)
print("LIVE vs DEMO ACCOUNT CHECK")
print("=" * 80)

# Check target user
print("\n[TARGET USER] migwibrian316@gmail.com")
try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    print("Found: YES")
    print("Balance: $" + str(user.balance))
    
    # Check if demo account exists
    try:
        demo = DemoAccount.objects.get(user=user)
        print("Account Type: DEMO")
        print("Demo Balance: $" + str(demo.balance))
    except DemoAccount.DoesNotExist:
        print("Account Type: LIVE")
    
    # Check transactions
    txns = Transaction.objects.filter(user=user)
    print("Transactions: " + str(txns.count()))
    for txn in txns:
        print("  - " + txn.transaction_type + ": $" + str(txn.amount))
        
except User.DoesNotExist:
    print("User not found")

# Count live vs demo
print("\n[ACCOUNT TYPES]")
all_users = User.objects.all()
demo_users = []
live_users = []

for u in all_users:
    try:
        DemoAccount.objects.get(user=u)
        demo_users.append(u)
    except:
        live_users.append(u)

print("Total users: " + str(all_users.count()))
print("Live accounts: " + str(len(live_users)))
print("Demo accounts: " + str(len(demo_users)))

# Show demo accounts
print("\n[DEMO ACCOUNTS]")
for u in demo_users[:5]:
    print("  " + u.email)

# Show live accounts
print("\n[LIVE ACCOUNTS]")
for u in live_users[:5]:
    print("  " + u.email)

print("\n" + "=" * 80)
