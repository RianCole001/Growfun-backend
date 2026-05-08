#!/usr/bin/env python
"""
Test script to check admin endpoints directly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.conf import settings
import json

# Add testserver to ALLOWED_HOSTS for testing
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

User = get_user_model()
client = Client()

# Get an admin user
admin_user = User.objects.get(email='test_admin@example.com')
print(f'Testing with admin user: {admin_user.email}')

# Try the known password
password = 'testpass123'
print(f'\nTrying password: {password}')
login_response = client.post('/api/auth/login/', {
    'email': admin_user.email,
    'password': password
}, content_type='application/json')
    
if login_response.status_code == 200:
    login_data = json.loads(login_response.content)
    token = login_data.get('tokens', {}).get('access')
    if token:
        print(f'Login successful! Token: {token[:20]}...')
        
        # Test admin endpoints
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        
        print('\n=== TESTING ADMIN ENDPOINTS ===')
        
        # Test investments endpoint
        inv_response = client.get('/api/admin/investments/', **headers)
        print(f'Investments endpoint: {inv_response.status_code}')
        if inv_response.status_code == 200:
            inv_data = json.loads(inv_response.content)
            print(f'Investments response: {inv_data}')
            print(f'Investments data count: {len(inv_data.get("data", []))}')
            if inv_data.get('data'):
                print(f'Sample investment: {inv_data["data"][0]}')
        else:
            print(f'Investments error: {inv_response.content}')
        
        # Test deposits endpoint
        dep_response = client.get('/api/admin/deposits/', **headers)
        print(f'Deposits endpoint: {dep_response.status_code}')
        if dep_response.status_code == 200:
            dep_data = json.loads(dep_response.content)
            print(f'Deposits response: {dep_data}')
            print(f'Deposits data count: {len(dep_data.get("data", []))}')
            if dep_data.get('data'):
                print(f'Sample deposit: {dep_data["data"][0]}')
        else:
            print(f'Deposits error: {dep_response.content}')
        
        # Test transactions endpoint
        txn_response = client.get('/api/admin/transactions/', **headers)
        print(f'Transactions endpoint: {txn_response.status_code}')
        if txn_response.status_code == 200:
            txn_data = json.loads(txn_response.content)
            print(f'Transactions response: {txn_data}')
            print(f'Transactions data count: {len(txn_data.get("data", []))}')
            if txn_data.get('data'):
                print(f'Sample transaction: {txn_data["data"][0]}')
        else:
            print(f'Transactions error: {txn_response.content}')
    else:
        print(f'Login response missing token: {login_data}')
else:
    print(f'Login failed: {login_response.status_code} - {login_response.content}')

print('\nTest completed.')