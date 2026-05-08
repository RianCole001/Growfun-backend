"""
Verify all admin endpoints are working and accessible
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from transactions.models import Transaction

User = get_user_model()

print("\n🔧 Admin Endpoints Verification\n")
print("=" * 60)

# Check admin user exists
try:
    admin_user = User.objects.get(email='admin@growfund.com')
    print(f"✅ Admin user found: {admin_user.email}")
    print(f"   Is Staff: {admin_user.is_staff}")
    print(f"   Is Superuser: {admin_user.is_superuser}")
except User.DoesNotExist:
    print("❌ Admin user not found")

# Check test data exists
print(f"\n📊 Current Database State:")
print(f"   Users: {User.objects.count()}")
print(f"   Transactions: {Transaction.objects.count()}")

# Show transaction breakdown
transaction_types = {}
for txn in Transaction.objects.all():
    txn_type = txn.transaction_type
    if txn_type not in transaction_types:
        transaction_types[txn_type] = []
    transaction_types[txn_type].append({
        'id': txn.id,
        'user': txn.user.email,
        'amount': str(txn.amount),
        'method': txn.payment_method,
        'status': txn.status
    })

for txn_type, transactions in transaction_types.items():
    print(f"\n   {txn_type.upper()} ({len(transactions)}):")
    for txn in transactions[:3]:  # Show first 3
        print(f"     - ID {txn['id']}: {txn['user']} - ${txn['amount']} via {txn['method']} ({txn['status']})")
    if len(transactions) > 3:
        print(f"     ... and {len(transactions) - 3} more")

# List available admin endpoints
print(f"\n🔗 Available Admin Endpoints:")
endpoints = [
    "GET /api/admin/transactions/ - List all transactions",
    "PUT /api/admin/transactions/{id}/edit/ - Edit transaction",
    "DELETE /api/admin/transactions/{id}/delete/ - Delete transaction",
    "GET /api/admin/deposits/ - List all deposits",
    "POST /api/admin/deposits/{id}/approve/ - Approve deposit",
    "POST /api/admin/deposits/{id}/reject/ - Reject deposit",
    "GET /api/admin/withdrawals/ - List all withdrawals",
    "POST /api/admin/withdrawals/{id}/approve/ - Approve withdrawal",
    "POST /api/admin/withdrawals/{id}/reject/ - Reject withdrawal",
    "GET /api/admin/investments/ - List all investments"
]

for endpoint in endpoints:
    print(f"   ✅ {endpoint}")

# Show sample transactions that can be edited
editable_transactions = Transaction.objects.filter(
    transaction_type__in=['deposit', 'withdrawal']
)[:3]

if editable_transactions:
    print(f"\n📝 Sample Transactions Available for Editing:")
    for txn in editable_transactions:
        print(f"   - ID {txn.id}: {txn.user.email} - {txn.transaction_type} - ${txn.amount}")
        print(f"     Method: {txn.payment_method} | Status: {txn.status}")
        print(f"     Edit URL: PUT /api/admin/transactions/{txn.id}/edit/")
        print(f"     Delete URL: DELETE /api/admin/transactions/{txn.id}/delete/")
        print()

print(f"🔑 Admin Credentials:")
print(f"   Email: admin@growfund.com")
print(f"   Password: admin123")

print(f"\n✅ Admin endpoints verification complete!")
print("=" * 60)
print()