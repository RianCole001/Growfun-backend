#!/usr/bin/env python
"""Test API call to reproduce 500 error"""
import requests
import json

# Test data
url = "http://localhost:8000/api/binary/trades/open/"
headers = {
    "Content-Type": "application/json",
}

# Get token first
login_url = "http://localhost:8000/api/auth/login/"
login_data = {
    "email": "testuser@example.com",
    "password": "TestPass123!"
}

print("Logging in...")
login_response = requests.post(login_url, json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    response_data = login_response.json()
    token = response_data.get('tokens', {}).get('access')
    
    if not token:
        print("No token in response!")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        exit(1)
    
    print(f"Token: {token[:20]}...")
    
    headers["Authorization"] = f"Bearer {token}"
    
    # Test trade
    trade_data = {
        "asset_symbol": "OIL",
        "direction": "buy",
        "amount": 10,
        "expiry_seconds": 60,
        "is_demo": True
    }
    
    print(f"\nOpening trade...")
    print(f"Data: {json.dumps(trade_data, indent=2)}")
    
    response = requests.post(url, json=trade_data, headers=headers)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Login failed: {login_response.text}")
