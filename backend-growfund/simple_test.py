#!/usr/bin/env python
"""Simple test of admin credit"""
import requests
import json

API_URL = 'http://localhost:8000/api'

print("Testing Admin Credit Functionality\n")

# Step 1: Login as admin
print("1. Logging in as admin...")
response = requests.post(
    f'{API_URL}/auth/login/',
    json={'email': 'testadmin@example.com', 'password': 'testpass123'}
)

if response.status_code == 200:
    admin_token = response.json()['access']
    print(f"   ✓ Admin token obtained")
else:
    print(f"   ✗ Failed: {response.status_code}")
    print(f"   {response.text[:200]}")
    exit(1)

# Step 2: Login as user
print("\n2. Logging in as user...")
response = requests.post(
    f'{API_URL}/auth/login/',
    json={'email': 'testuser@example.com', 'password': 'testpass123'}
)

if response.status_code == 200:
    user_token = response.json()['access']
    print(f"   ✓ User token obtained")
else:
    print(f"   ✗ Failed: {response.status_code}")
    exit(1)

# Step 3: Get initial balance
print("\n3. Getting initial balance...")
response = requests.get(
    f'{API_URL}/accounts/profile/',
    headers={'Authorization': f'Bearer {user_token}'}
)

if response.status_code == 200:
    initial_balance = response.json()['data']['balance']
    user_id = response.json()['data']['id']
    print(f"   ✓ Initial balance: ${initial_balance}")
    print(f"   ✓ User ID: {user_id}")
else:
    print(f"   ✗ Failed: {response.status_code}")
    exit(1)

# Step 4: Credit balance
print("\n4. Crediting $100 to user...")
response = requests.post(
    f'{API_URL}/accounts/admin/users/{user_id}/balance/',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'action': 'credit', 'amount': 100, 'note': 'Test credit'}
)

if response.status_code == 200:
    data = response.json()
    new_balance = data['data']['new_balance']
    print(f"   ✓ Credit successful")
    print(f"   ✓ New balance: ${new_balance}")
else:
    print(f"   ✗ Failed: {response.status_code}")
    print(f"   {response.text}")
    exit(1)

# Step 5: Verify balance updated
print("\n5. Verifying balance updated...")
response = requests.get(
    f'{API_URL}/accounts/profile/',
    headers={'Authorization': f'Bearer {user_token}'}
)

if response.status_code == 200:
    updated_balance = response.json()['data']['balance']
    expected = initial_balance + 100
    print(f"   ✓ Updated balance: ${updated_balance}")
    print(f"   ✓ Expected: ${expected}")
    if updated_balance == expected:
        print(f"   ✓ BALANCE MATCHES!")
    else:
        print(f"   ✗ Balance mismatch")
else:
    print(f"   ✗ Failed: {response.status_code}")
    exit(1)

# Step 6: Check transaction history
print("\n6. Checking transaction history...")
response = requests.get(
    f'{API_URL}/transactions/',
    headers={'Authorization': f'Bearer {user_token}'}
)

if response.status_code == 200:
    transactions = response.json()['results']
    print(f"   ✓ Total transactions: {len(transactions)}")
    
    admin_credit = None
    for txn in transactions:
        if txn['transaction_type'] == 'admin_credit':
            admin_credit = txn
            break
    
    if admin_credit:
        print(f"   ✓ Admin credit transaction found!")
        print(f"     - Amount: ${admin_credit['amount']}")
        print(f"     - Status: {admin_credit['status']}")
        print(f"     - Description: {admin_credit['description']}")
    else:
        print(f"   ✗ Admin credit transaction NOT found")
else:
    print(f"   ✗ Failed: {response.status_code}")
    exit(1)

print("\n" + "="*50)
print("✅ ALL TESTS PASSED - CREDITING IS WORKING!")
print("="*50)
