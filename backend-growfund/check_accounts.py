import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from demo.models import DemoAccount
from transactions.models import Transaction
from decimal import Decimal

User = get_user_model()

print("=" * 80)
print("ACCOUNT TYPE ANALYSIS")
print("=" * 80)

# Check target user
print("\n[1] TARGET USER: migwibrian316@gmail.com")
try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    print(f"✓ Found: {user.email}")
    print(f"  ID: {user.id}")
    print(f"  Balance: ${user.balance}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")
    
    # Check if has demo account
    try:
        demo = DemoAccount.objects.get(user=user)
        print(f"  Demo Account: YES")
        print(f"    Demo Balance: ${demo.balance}")
    except DemoAccount.DoesNotExist:
        print(f"  Demo Account: NO")
    
    # Check transactions
    txns = Transaction.objects.filter(user=user)
    print(f"  Transactions: {txns.count()}")
    for txn in txns:
        print(f"    - {txn.transaction_type}: ${txn.amount} ({txn.status})")
        
except User.DoesNotExist:
    print(f"✗ User not found")

# Check all users with balances
print("\n[2] ALL USERS WITH BALANCES")
users = User.objects.filter(balance__gt=0).order_by('-balance')[:10]
print(f"Users with balance > $0: {users.count()}")
for u in users:
    try:
        demo = DemoAccount.objects.get(user=u)
        demo_status = "DEMO"
    except:
        demo_status = "LIVE"
    print(f"  {u.email}: ${u.balance} ({demo_status})")

# Check demo accounts
print("\n[3] DEMO ACCOUNTS")
try:
    demo_accounts = DemoAccount.objects.all()[:10]
    print(f"Total demo accounts: {demo_accounts.count()}")
    for demo in demo_accounts:
        print(f"  {demo.user.email}: ${demo.balance}")
except Exception as e:
    print(f"Error checking demo accounts: {e}")

# Check live accounts (no demo)
print("\n[4] LIVE ACCOUNTS (No Demo)")
live_users = []
for user in User.objects.all():
    try:
        DemoAccount.objects.get(user=user)
    except DemoAccount.DoesNotExist:
        live_users.append(user)

print(f"Total live accounts: {len(live_users)}")
for u in live_users[:10]:
    print(f"  {u.email}: ${u.balance}")

# Check transactions by type
print("\n[5] TRANSACTION SUMMARY")
admin_credits = Transaction.objects.filter(transaction_type='admin_credit')
print(f"Admin credit transactions: {admin_credits.count()}")
total_admin_credit = sum(t.amount for t in admin_credits)
print(f"Total admin credited: ${total_admin_credit}")

# Check if migwibrian316@gmail.com has admin credits
print("\n[6] MIGWIBRIAN316@GMAIL.COM TRANSACTIONS")
try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    user_txns = Transaction.objects.filter(user=user)
    print(f"Total transactions: {user_txns.count()}")
    for txn in user_txns:
        print(f"  {txn.transaction_type}: ${txn.amount} - {txn.description}")
except:
    print("User not found")

print("\n" + "=" * 80)
