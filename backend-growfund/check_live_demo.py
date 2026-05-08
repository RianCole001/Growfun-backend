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
    print(f"✓ Found")
    print(f"  Balance: ${user.balance}")
    
    # Check if demo account exists
    try:
        demo = DemoAccount.objects.get(user=user)
        print(f"  Account Type: DEMO")
        print(f"  Demo Balance: ${demo.balance}")
    except DemoAccount.DoesNotExist:
        print(f"  Account Type: LIVE")
    
    # Check transactions
    txns = Transaction.objects.filter(user=user)
    print(f"  Transactions: {txns.count()}")
    for txn in txns:
        print(f"    - {txn.transaction_type}: ${txn.amount}")
        
except User.DoesNotExist:
    print(f"✗ User not found")

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

print(f"Total users: {all_users.count()}")
print(f"Live accounts: {len(live_users)}")
print(f"Demo accounts: {len(demo_users)}")

# Show demo accounts
print("\n[DEMO ACCOUNTS]")
for u in demo_users[:5]:
    print(f"  {u.email}")

# Show live accounts
print("\n[LIVE ACCOUNTS]")
for u in live_users[:5]:
    print(f"  {u.email}")

print("\n" + "=" * 80)
