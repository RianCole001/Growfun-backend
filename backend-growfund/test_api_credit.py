#!/usr/bin/env python
"""
Test the admin credit API endpoint
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Get or create admin user
admin_user = User.objects.filter(is_staff=True).first()
if not admin_user:
    admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    print("No admin user found! Creating one...")
    admin_user = User.objects.create_superuser(
        email='admin@test.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )

# Get a regular user to credit
test_user = User.objects.filter(is_staff=False).first()
if not test_user:
    print("No regular user found! Creating one...")
    test_user = User.objects.create_user(
        email='testuser@test.com',
        password='test123',
        first_name='Test',
        last_name='User'
    )

print(f"\n=== Testing Admin Credit API ===")
print(f"Admin: {admin_user.email}")
print(f"Target User: {test_user.email}")
print(f"Current Balance: ${test_user.balance}")

# Create API client
client = APIClient()

# Get admin token
refresh = RefreshToken.for_user(admin_user)
access_token = str(refresh.access_token)

# Set authorization header
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

# Test credit endpoint
print(f"\nCalling POST /api/accounts/admin/users/{test_user.id}/balance/")
response = client.post(
    f'/api/accounts/admin/users/{test_user.id}/balance/',
    {
        'action': 'credit',
        'amount': 25.00,
        'note': 'API Test Credit'
    },
    format='json'
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.data}")

# Refresh user from database
test_user.refresh_from_db()
print(f"\nNew Balance: ${test_user.balance}")

# Check transactions
from transactions.models import Transaction
recent_trans = Transaction.objects.filter(user=test_user).order_by('-created_at')[:3]
print(f"\nRecent Transactions:")
for t in recent_trans:
    print(f"  - {t.transaction_type}: ${t.amount} ({t.status}) - {t.description}")

if response.status_code == 200:
    print("\n✅ API endpoint working!")
else:
    print(f"\n❌ API endpoint failed: {response.data}")
