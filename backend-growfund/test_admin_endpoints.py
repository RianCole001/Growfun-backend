#!/usr/bin/env python
"""
Test script for admin endpoints
Run this to test admin delete and suspend functionality
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

def get_admin_token():
    """Get JWT token for admin user"""
    try:
        admin = User.objects.get(email='admin@growfund.com')
        refresh = RefreshToken.for_user(admin)
        return str(refresh.access_token)
    except User.DoesNotExist:
        print("❌ Admin user not found. Creating admin user...")
        admin = User.objects.create_superuser(
            email='admin@growfund.com',
            password='Admin123!',
            first_name='Admin',
            last_name='User'
        )
        refresh = RefreshToken.for_user(admin)
        return str(refresh.access_token)

def create_test_user():
    """Create a test user for deletion/suspension"""
    try:
        test_user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
        return test_user
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        # Try to get existing user
        try:
            test_user = User.objects.get(email='testuser@example.com')
            print(f"✅ Using existing test user: {test_user.email} (ID: {test_user.id})")
            return test_user
        except User.DoesNotExist:
            return None

def test_admin_endpoints():
    """Test admin delete and suspend endpoints"""
    print("🧪 Testing Admin Endpoints...")
    
    # Get admin token
    token = get_admin_token()
    print(f"✅ Got admin token: {token[:20]}...")
    
    # Create test user
    test_user = create_test_user()
    if not test_user:
        print("❌ Could not create test user")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    base_url = 'http://localhost:8000'  # Change if running on different port
    
    # Test 1: Suspend user
    print(f"\n🔧 Testing suspend user {test_user.id}...")
    suspend_url = f"{base_url}/api/auth/admin/users/{test_user.id}/suspend/"
    suspend_data = {'action': 'suspend'}
    
    try:
        response = requests.post(suspend_url, json=suspend_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Suspend test PASSED")
        else:
            print("❌ Suspend test FAILED")
    except Exception as e:
        print(f"❌ Suspend test ERROR: {e}")
    
    # Test 2: Unsuspend user
    print(f"\n🔧 Testing unsuspend user {test_user.id}...")
    unsuspend_data = {'action': 'unsuspend'}
    
    try:
        response = requests.post(suspend_url, json=unsuspend_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Unsuspend test PASSED")
        else:
            print("❌ Unsuspend test FAILED")
    except Exception as e:
        print(f"❌ Unsuspend test ERROR: {e}")
    
    # Test 3: Delete user (soft delete)
    print(f"\n🔧 Testing delete user {test_user.id}...")
    delete_url = f"{base_url}/api/auth/admin/users/{test_user.id}/"
    
    try:
        response = requests.delete(delete_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Delete test PASSED")
        else:
            print("❌ Delete test FAILED")
    except Exception as e:
        print(f"❌ Delete test ERROR: {e}")
    
    # Test 4: List suspended users
    print(f"\n🔧 Testing list suspended users...")
    suspended_url = f"{base_url}/api/auth/admin/users/suspended/"
    
    try:
        response = requests.get(suspended_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ List suspended users test PASSED")
        else:
            print("❌ List suspended users test FAILED")
    except Exception as e:
        print(f"❌ List suspended users test ERROR: {e}")

if __name__ == '__main__':
    test_admin_endpoints()