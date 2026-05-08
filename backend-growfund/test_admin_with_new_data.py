"""
Test admin endpoints with the new test data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from transactions.admin_views import admin_get_investments, admin_get_deposits, admin_get_transactions
import json

User = get_user_model()

print("\n🧪 Testing Admin Endpoints with New Test Data\n")
print("=" * 70)

# Get or create an admin user
admin_user, created = User.objects.get_or_create(
    email='admin@growfund.com',
    defaults={
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True,
        'is_verified': True
    }
)

if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✅ Created admin user: {admin_user.email}")
else:
    print(f"ℹ️  Using existing admin user: {admin_user.email}")

# Create a request factory
factory = RequestFactory()

# Test investments endpoint
print("\n" + "=" * 70)
print("📊 Testing /api/admin/investments/")
print("=" * 70)

request = factory.get('/api/admin/investments/')
request.user = admin_user
response = admin_get_investments(request)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Status: {response.status_code}")
    print(f"📈 Total Investments: {data.get('total_investments', 0)}")
    
    if 'summary' in data:
        summary = data['summary']
        print(f"\n📊 Summary:")
        print(f"  - Crypto Trades: {summary.get('crypto_count', 0)}")
        print(f"  - Capital Plans: {summary.get('capital_plans_count', 0)}")
        print(f"  - Total Invested: ${summary.get('total_invested', 0)}")
        print(f"  - Current Value: ${summary.get('total_current_value', 0)}")
        print(f"  - P&L: ${summary.get('total_profit_loss', 0)}")
    
    if 'data' in data and len(data['data']) > 0:
        print(f"\n📋 Sample Investment:")
        investment = data['data'][0]
        print(f"  - User: {investment.get('user')}")
        print(f"  - Type: {investment.get('type')}")
        print(f"  - Asset: {investment.get('asset', 'N/A')}")
        print(f"  - Amount: ${investment.get('amount', 0)}")
        print(f"  - Status: {investment.get('status')}")
else:
    print(f"❌ Status: {response.status_code}")

# Test deposits endpoint
print("\n" + "=" * 70)
print("💰 Testing /api/admin/deposits/")
print("=" * 70)

request = factory.get('/api/admin/deposits/')
request.user = admin_user
response = admin_get_deposits(request)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Status: {response.status_code}")
    print(f"💵 Total Deposits: {len(data.get('data', []))}")
    
    if 'data' in data and len(data['data']) > 0:
        print(f"\n📋 Sample Deposit:")
        deposit = data['data'][0]
        print(f"  - User: {deposit.get('user')}")
        print(f"  - Amount: ${deposit.get('amount')}")
        print(f"  - Method: {deposit.get('method')}")
        print(f"  - Status: {deposit.get('status')}")
        print(f"  - Reference: {deposit.get('reference')}")
else:
    print(f"❌ Status: {response.status_code}")

# Test transactions endpoint
print("\n" + "=" * 70)
print("💳 Testing /api/admin/transactions/")
print("=" * 70)

request = factory.get('/api/admin/transactions/')
request.user = admin_user
response = admin_get_transactions(request)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Status: {response.status_code}")
    print(f"📝 Total Transactions: {len(data.get('data', []))}")
    
    # Count transaction types
    if 'data' in data:
        types = {}
        for txn in data['data']:
            txn_type = txn.get('type', 'Unknown')
            types[txn_type] = types.get(txn_type, 0) + 1
        
        print(f"\n📊 Transaction Types:")
        for txn_type, count in types.items():
            print(f"  - {txn_type}: {count}")
    
    if 'data' in data and len(data['data']) > 0:
        print(f"\n📋 Sample Transaction:")
        txn = data['data'][0]
        print(f"  - User: {txn.get('user')}")
        print(f"  - Type: {txn.get('type')}")
        print(f"  - Amount: ${txn.get('amount')}")
        print(f"  - Status: {txn.get('status')}")
else:
    print(f"❌ Status: {response.status_code}")

print("\n" + "=" * 70)
print("✅ Admin endpoint testing complete!")
print("=" * 70)

print(f"\n🔑 Admin Credentials:")
print(f"  Email: {admin_user.email}")
print(f"  Password: admin123")
print(f"  Is Staff: {admin_user.is_staff}")
print(f"  Is Superuser: {admin_user.is_superuser}")
print()
