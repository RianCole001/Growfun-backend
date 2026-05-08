"""
Test admin edit and delete transaction endpoints
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from transactions.admin_views import admin_edit_transaction, admin_delete_transaction, admin_get_transactions
from transactions.models import Transaction
from decimal import Decimal
import json

User = get_user_model()

print("\n🧪 Testing Admin Edit and Delete Transaction Endpoints\n")
print("=" * 70)

# Get admin user
try:
    admin_user = User.objects.get(email='admin@growfund.com')
    print(f"✅ Using admin user: {admin_user.email}")
except User.DoesNotExist:
    print("❌ Admin user not found. Please create one first.")
    exit(1)

# Get a test user
try:
    test_user = User.objects.filter(email__contains='user').first()
    if not test_user:
        print("❌ No test users found. Please run create_test_data first.")
        exit(1)
    print(f"✅ Using test user: {test_user.email}")
    print(f"   Initial balance: ${test_user.balance}")
except Exception as e:
    print(f"❌ Error getting test user: {e}")
    exit(1)

# Create a request factory
factory = RequestFactory()

# Get initial transactions count
initial_count = Transaction.objects.count()
print(f"\n📊 Initial transactions count: {initial_count}")

# Test 1: Create a test transaction to edit
print("\n" + "=" * 70)
print("📝 Test 1: Creating a test transaction")
print("=" * 70)

test_transaction = Transaction.objects.create(
    user=test_user,
    transaction_type='deposit',
    amount=Decimal('100.00'),
    payment_method='mpesa',
    status='completed',
    reference='TEST-MPESA-001'
)

# Update user balance
test_user.balance += Decimal('100.00')
test_user.save()

print(f"✅ Created test transaction:")
print(f"   ID: {test_transaction.id}")
print(f"   Amount: ${test_transaction.amount}")
print(f"   Method: {test_transaction.payment_method}")
print(f"   Status: {test_transaction.status}")
print(f"   User balance after: ${test_user.balance}")

# Test 2: Edit the transaction amount
print("\n" + "=" * 70)
print("📝 Test 2: Editing transaction amount")
print("=" * 70)

request = factory.put(
    f'/api/admin/transactions/{test_transaction.id}/edit/',
    data=json.dumps({
        'amount': '150.00'
    }),
    content_type='application/json'
)
request.user = admin_user
response = admin_edit_transaction(request, test_transaction.id)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Transaction edited successfully")
    print(f"   New amount: ${data['data']['transaction']['amount']}")
    
    # Refresh user balance
    test_user.refresh_from_db()
    print(f"   User balance after edit: ${test_user.balance}")
else:
    print(f"❌ Edit failed with status: {response.status_code}")
    print(f"   Response: {response.content}")

# Test 3: Edit the payment method
print("\n" + "=" * 70)
print("📝 Test 3: Editing payment method")
print("=" * 70)

request = factory.put(
    f'/api/admin/transactions/{test_transaction.id}/edit/',
    data=json.dumps({
        'payment_method': 'mtn_momo',
        'reference': 'TEST-MTN-002'
    }),
    content_type='application/json'
)
request.user = admin_user
response = admin_edit_transaction(request, test_transaction.id)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Payment method edited successfully")
    print(f"   New method: {data['data']['transaction']['payment_method']}")
    print(f"   New reference: {data['data']['transaction']['reference']}")
else:
    print(f"❌ Edit failed with status: {response.status_code}")

# Test 4: Edit transaction status
print("\n" + "=" * 70)
print("📝 Test 4: Editing transaction status")
print("=" * 70)

# Create a pending transaction
pending_transaction = Transaction.objects.create(
    user=test_user,
    transaction_type='deposit',
    amount=Decimal('200.00'),
    payment_method='airtel_money',
    status='pending',
    reference='TEST-AIRTEL-003'
)

print(f"✅ Created pending transaction:")
print(f"   ID: {pending_transaction.id}")
print(f"   Amount: ${pending_transaction.amount}")
print(f"   Status: {pending_transaction.status}")
print(f"   User balance before: ${test_user.balance}")

# Change status to completed
request = factory.put(
    f'/api/admin/transactions/{pending_transaction.id}/edit/',
    data=json.dumps({
        'status': 'completed'
    }),
    content_type='application/json'
)
request.user = admin_user
response = admin_edit_transaction(request, pending_transaction.id)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Status changed to completed")
    
    # Refresh user balance
    test_user.refresh_from_db()
    print(f"   User balance after status change: ${test_user.balance}")
else:
    print(f"❌ Edit failed with status: {response.status_code}")

# Test 5: Delete a transaction
print("\n" + "=" * 70)
print("📝 Test 5: Deleting a transaction")
print("=" * 70)

balance_before_delete = test_user.balance
print(f"   User balance before delete: ${balance_before_delete}")

request = factory.delete(f'/api/admin/transactions/{test_transaction.id}/delete/')
request.user = admin_user
response = admin_delete_transaction(request, test_transaction.id)

if response.status_code == 200:
    data = json.loads(response.content)
    print(f"✅ Transaction deleted successfully")
    print(f"   Deleted transaction ID: {data['data']['deleted_transaction']['id']}")
    
    # Refresh user balance
    test_user.refresh_from_db()
    print(f"   User balance after delete: ${test_user.balance}")
    
    # Verify transaction is deleted
    try:
        Transaction.objects.get(id=test_transaction.id)
        print(f"❌ Transaction still exists!")
    except Transaction.DoesNotExist:
        print(f"✅ Transaction successfully removed from database")
else:
    print(f"❌ Delete failed with status: {response.status_code}")
    print(f"   Response: {response.content}")

# Test 6: Verify final state
print("\n" + "=" * 70)
print("📊 Final State")
print("=" * 70)

final_count = Transaction.objects.count()
print(f"   Initial transactions: {initial_count}")
print(f"   Final transactions: {final_count}")
print(f"   Net change: {final_count - initial_count}")

test_user.refresh_from_db()
print(f"   Final user balance: ${test_user.balance}")

print("\n" + "=" * 70)
print("✅ Admin edit and delete testing complete!")
print("=" * 70)
print()
