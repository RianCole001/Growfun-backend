"""
Quick script to verify test data was created correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from transactions.models import Transaction
from investments.models import Trade, CapitalInvestmentPlan
from notifications.models import Notification

User = get_user_model()

print("\n📊 Test Data Verification\n")
print("=" * 60)

# Count users
users = User.objects.all()
print(f"\n👥 Users: {users.count()}")
for user in users:
    print(f"  - {user.email} (Balance: ${user.balance})")

# Count transactions
transactions = Transaction.objects.all()
print(f"\n💰 Transactions: {transactions.count()}")
transaction_types = {}
for txn in transactions:
    txn_type = txn.transaction_type
    if txn_type not in transaction_types:
        transaction_types[txn_type] = 0
    transaction_types[txn_type] += 1

for txn_type, count in transaction_types.items():
    print(f"  - {txn_type}: {count}")

# Count capital plans
plans = CapitalInvestmentPlan.objects.all()
print(f"\n📈 Capital Investment Plans: {plans.count()}")
for plan in plans:
    print(f"  - {plan.user.email}: {plan.plan_type} - ${plan.initial_amount} (Final: ${plan.final_amount})")

# Count trades
trades = Trade.objects.all()
print(f"\n💎 Crypto Trades: {trades.count()}")
for trade in trades:
    print(f"  - {trade.user.email}: {trade.asset} - {trade.quantity} @ ${trade.entry_price}")

# Count notifications
notifications = Notification.objects.all()
print(f"\n🔔 Notifications: {notifications.count()}")

print("\n" + "=" * 60)
print("✅ Test data verification complete!\n")
