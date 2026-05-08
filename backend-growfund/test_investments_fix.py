#!/usr/bin/env python
"""Test the investments fix"""
import requests
import json

print('=== TESTING INVESTMENTS FIX ===')

# Login as the specific user
login_data = {
    "email": "migwibrian316@gmail.com",
    "password": "password123"  # You may need to update this
}

try:
    # Try to login as the user
    response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
    if response.status_code == 200:
        token = response.json()['data']['access']
        print('✓ User login successful')
        
        # Test new unified investments endpoint
        headers = {'Authorization': f'Bearer {token}'}
        investments_response = requests.get('http://localhost:8000/api/investments/all/', headers=headers)
        
        if investments_response.status_code == 200:
            investments_data = investments_response.json()
            print(f'✓ Unified investments endpoint working')
            print(f'  Total investments: {investments_data["data"]["summary"]["investment_count"]}')
            print(f'  Crypto investments: {investments_data["data"]["summary"]["crypto_count"]}')
            print(f'  Capital plans: {investments_data["data"]["summary"]["capital_plan_count"]}')
            
            for inv in investments_data['data']['investments']:
                print(f'  - {inv["type"]}: {inv["name"]} = ${inv["amount"]} (Status: {inv["status"]})')
        else:
            print(f'✗ Investments endpoint failed: {investments_response.status_code}')
            print(f'  Response: {investments_response.text}')
            
        # Test crypto portfolio endpoint
        crypto_response = requests.get('http://localhost:8000/api/investments/crypto/portfolio/', headers=headers)
        if crypto_response.status_code == 200:
            crypto_data = crypto_response.json()
            print(f'✓ Crypto portfolio endpoint working')
            print(f'  Crypto investments: {len(crypto_data["data"]["investments"])}')
            
            for inv in crypto_data['data']['investments']:
                print(f'  - {inv["coin"]}: {inv["quantity"]} = ${inv["amount"]}')
        else:
            print(f'✗ Crypto portfolio failed: {crypto_response.status_code}')
            
    else:
        print(f'✗ User login failed: {response.status_code}')
        print(f'  Response: {response.text}')
        
        # Try with admin login to test admin deposits
        admin_login = {
            "email": "admin@growfund.com",
            "password": "Admin123!"
        }
        
        admin_response = requests.post('http://localhost:8000/api/auth/login/', json=admin_login)
        if admin_response.status_code == 200:
            admin_token = admin_response.json()['data']['access']
            print('✓ Admin login successful')
            
            # Test admin deposits endpoint
            admin_headers = {'Authorization': f'Bearer {admin_token}'}
            deposits_response = requests.get('http://localhost:8000/api/admin/deposits/', headers=admin_headers)
            
            if deposits_response.status_code == 200:
                deposits_data = deposits_response.json()
                print(f'✓ Admin deposits endpoint working')
                print(f'  Total deposits/credits: {len(deposits_data["data"])}')
                
                for deposit in deposits_data['data'][:5]:  # Show first 5
                    print(f'  - {deposit["user"]}: ${deposit["amount"]} ({deposit.get("method", "N/A")})')
            else:
                print(f'✗ Admin deposits failed: {deposits_response.status_code}')
        
except Exception as e:
    print(f'✗ Error: {e}')

print('\n=== TEST COMPLETE ===')