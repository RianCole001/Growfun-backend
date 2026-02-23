#!/usr/bin/env python
"""
Simple script to test user notification endpoint
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_user_notifications():
    print("🔍 Testing User Notification Endpoint")
    print("=" * 50)
    
    # Get a regular user (not admin)
    regular_user = User.objects.filter(is_active=True, is_staff=False).first()
    
    if not regular_user:
        print("❌ No regular user found")
        return
    
    print(f"👤 Testing with user: {regular_user.email}")
    
    # Generate JWT token for the user
    refresh = RefreshToken.for_user(regular_user)
    access_token = str(refresh.access_token)
    
    print(f"🔑 Generated token: {access_token[:20]}...")
    
    # Test the notification endpoint
    url = "http://localhost:8000/api/notifications/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"🌐 Testing endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response format:")
            print(f"   - Success: {data.get('success', 'N/A')}")
            print(f"   - Data count: {len(data.get('data', []))}")
            print(f"   - Unread count: {data.get('unread_count', 'N/A')}")
            
            # Show first few notifications
            notifications = data.get('data', [])
            if notifications:
                print(f"\n📋 First 3 notifications:")
                for i, notif in enumerate(notifications[:3]):
                    print(f"   {i+1}. {notif.get('title', 'No title')} - {notif.get('type', 'No type')} - Read: {notif.get('read', 'N/A')}")
            else:
                print("📭 No notifications found for this user")
                
        else:
            print(f"❌ Error response: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the Django server running on localhost:8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_user_notifications()