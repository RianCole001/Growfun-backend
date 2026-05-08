#!/usr/bin/env python
"""Test API endpoints"""
import requests
import json

# Test admin login
login_data = {
    "email": "admin@growfund.com",
    "password": "Admin123!"
}

print('=== TESTING API ENDPOINTS ===')

try:
    # Login as admin
    response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
    if response.status_code == 200:
        token = response.json()['data']['access']
        print('✓ Admin login successful')
        
        # Test admin deposits endpoint
        headers = {'Authorization': f'Bearer {token}'}
        deposits_response = requests.get('http://localhost:8000/api/admin/deposits/', headers=headers)
        
        if deposits_response.status_code == 200:
            deposits_data = deposits_response.json()
            print(f'✓ Admin deposits endpoint working')
            print(f'  Found {len(deposits_data["data"])} deposits/credits')
            
            for deposit in deposits_data['data'][:3]:  # Show first 3
                print(f'  - {deposit["user"]}: ${deposit["amount"]} ({deposit["status"]})')
        else:
            print(f'✗ Deposits endpoint failed: {deposits_response.status_code}')
            print(f'  Response: {deposits_response.text}')
            
        # Test crypto prices endpoint
        prices_response = requests.get('http://localhost:8000/api/investments/admin/crypto-prices/', headers=headers)
        if prices_response.status_code == 200:
            prices_data = prices_response.json()
            print(f'✓ Crypto prices endpoint working')
            print(f'  Found {len(prices_data["data"])} coins')
            
            for coin_data in prices_data['data']:
                if coin_data['coin'] == 'EXACOIN':
                    print(f'  - EXACOIN: Buy ${coin_data["buy_price"]}, Sell ${coin_data["sell_price"]}')
                    break
        else:
            print(f'✗ Crypto prices endpoint failed: {prices_response.status_code}')
            
    else:
        print(f'✗ Admin login failed: {response.status_code}')
        print(f'  Response: {response.text}')
        
except Exception as e:
    print(f'✗ Error: {e}')

print('\n=== TEST COMPLETE ===')