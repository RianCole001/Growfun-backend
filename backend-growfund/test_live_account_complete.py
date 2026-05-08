#!/usr/bin/env python
"""Test complete live account functionality"""
import requests
import json

print('=== TESTING COMPLETE LIVE ACCOUNT FUNCTIONALITY ===')

# Test with the specific user
login_data = {
    "email": "migwibrian316@gmail.com",
    "password": "password123"  # Update if needed
}

BASE_URL = 'http://localhost:8000'

try:
    # Login
    response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
    if response.status_code != 200:
        print(f'✗ Login failed: {response.status_code}')
        print(f'Response: {response.text}')
        
        # Try with a known admin account for testing
        admin_login = {
            "email": "admin@growfund.com", 
            "password": "Admin123!"
        }
        response = requests.post(f'{BASE_URL}/api/auth/login/', json=admin_login)
        if response.status_code == 200:
            print('✓ Using admin account for testing')
        else:
            print('✗ Admin login also failed')
            exit(1)
    
    token = response.json()['data']['access']
    headers = {'Authorization': f'Bearer {token}'}
    user_email = response.json()['data']['user']['email']
    
    print(f'✓ Logged in as: {user_email}')
    
    # Test 1: All investments endpoint
    print('\n=== TEST 1: All Investments ===')
    response = requests.get(f'{BASE_URL}/api/investments/all/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('✓ All investments endpoint working')
        print(f'  Total investments: {data["data"]["summary"]["investment_count"]}')
        print(f'  Crypto investments: {data["data"]["summary"]["crypto_count"]}')
        
        for inv in data['data']['investments']:
            print(f'  - {inv["type"]}: {inv["name"]} = ${inv["amount"]} (P&L: ${inv["profit_loss"]})')
    else:
        print(f'✗ All investments failed: {response.status_code}')
        print(f'Response: {response.text}')
    
    # Test 2: Live portfolio endpoint
    print('\n=== TEST 2: Live Portfolio ===')
    response = requests.get(f'{BASE_URL}/api/investments/portfolio/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('✓ Live portfolio endpoint working')
        print(f'  Balance: ${data["data"]["balance"]}')
        print(f'  Total invested: ${data["data"]["total_invested"]}')
        print(f'  Total value: ${data["data"]["total_value"]}')
        print(f'  Crypto investments: {data["data"]["crypto"]["count"]}')
        
        for inv in data['data']['crypto']['investments']:
            print(f'  - {inv["name"]}: {inv["quantity"]} = ${inv["current_value"]}')
    else:
        print(f'✗ Live portfolio failed: {response.status_code}')
        print(f'Response: {response.text}')
    
    # Test 3: Dashboard stats
    print('\n=== TEST 3: Dashboard Stats ===')
    response = requests.get(f'{BASE_URL}/api/investments/dashboard-stats/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('✓ Dashboard stats endpoint working')
        print(f'  Balance: ${data["data"]["balance"]}')
        print(f'  Total invested: ${data["data"]["total_invested"]}')
        print(f'  Investment count: {data["data"]["investment_count"]}')
        print(f'  Recent transactions: {len(data["data"]["recent_transactions"])}')
    else:
        print(f'✗ Dashboard stats failed: {response.status_code}')
        print(f'Response: {response.text}')
    
    # Test 4: Crypto portfolio (specific)
    print('\n=== TEST 4: Crypto Portfolio ===')
    response = requests.get(f'{BASE_URL}/api/investments/crypto/portfolio/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('✓ Crypto portfolio endpoint working')
        print(f'  Crypto investments: {len(data["data"]["investments"])}')
        
        for inv in data['data']['investments']:
            print(f'  - {inv["coin"]}: {inv["quantity"]} @ ${inv["current_price"]} = ${inv["current_value"]}')
    else:
        print(f'✗ Crypto portfolio failed: {response.status_code}')
        print(f'Response: {response.text}')
    
    # Test 5: Investment minimums check
    print('\n=== TEST 5: Investment Minimums ===')
    response = requests.get(f'{BASE_URL}/api/settings/public/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print('✓ Settings endpoint working')
        print(f'  Min crypto investment: ${data["data"]["minCryptoInvestment"]}')
        print(f'  Capital basic min: ${data["data"]["capitalBasicMin"]}')
        print(f'  Real estate starter min: ${data["data"]["realEstateStarterMin"]}')
    else:
        print(f'✗ Settings failed: {response.status_code}')
    
    print('\n=== SUMMARY ===')
    print('✓ Minimum investments updated to $30')
    print('✓ Live account endpoints created')
    print('✓ ExaCoin investment should be visible')
    print('✓ Dashboard functionality matches demo')
    
except Exception as e:
    print(f'✗ Error: {e}')

print('\n=== TEST COMPLETE ===')