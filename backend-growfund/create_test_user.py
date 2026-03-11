#!/usr/bin/env python
"""Create test user for API testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from accounts.models import User
from decimal import Decimal

email = "testuser@example.com"
password = "TestPass123!"

# Delete if exists
User.objects.filter(email=email).delete()

# Create new user
user = User.objects.create_user(
    email=email,
    password=password,
    first_name="Test",
    last_name="User",
    balance=Decimal('5000.00'),
    is_verified=True
)

print(f"✅ Created user: {user.email}")
print(f"   Password: {password}")
print(f"   Balance: ${user.balance}")
