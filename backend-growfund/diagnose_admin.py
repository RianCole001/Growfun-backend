#!/usr/bin/env python
"""Diagnose admin login issues"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()

print("=" * 70)
print("ADMIN LOGIN DIAGNOSTICS")
print("=" * 70)

# Test emails to check
test_emails = [
    'Tabby@gmail.com',
    'tabby@gmail.com',
    'admin001@gmail.com',
    'admin@growfund.com'
]

print("\n1. CHECKING ALL USERS IN DATABASE")
print("-" * 70)
all_users = User.objects.all()
print(f"Total users: {all_users.count()}\n")

for user in all_users:
    admin_status = "ADMIN" if (user.is_staff or user.is_superuser) else "USER"
    verified_status = "✓" if user.is_verified else "✗"
    active_status = "ACTIVE" if user.is_active else "INACTIVE"
    
    print(f"[{admin_status}] {user.email}")
    print(f"  Status: {active_status} | Verified: {verified_status}")
    print(f"  Staff: {user.is_staff} | Superuser: {user.is_superuser}")
    print(f"  Balance: ${user.balance}")
    print()

print("\n2. CHECKING SPECIFIC ADMIN ACCOUNTS")
print("-" * 70)

for email in test_emails:
    try:
        user = User.objects.get(email=email)
        print(f"\n✓ FOUND: {email}")
        print(f"  ID: {user.id}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Active: {user.is_active}")
        print(f"  Verified: {user.is_verified}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Superuser: {user.is_superuser}")
        print(f"  Has password: {bool(user.password)}")
        print(f"  Password hash: {user.password[:50]}...")
    except User.DoesNotExist:
        print(f"\n✗ NOT FOUND: {email}")

print("\n\n3. TESTING AUTHENTICATION")
print("-" * 70)

# Test credentials
test_credentials = [
    ('Tabby@gmail.com', 'Tabby123!'),
    ('tabby@gmail.com', 'Tabby123!'),
    ('admin001@gmail.com', 'Buffers316!'),
    ('admin@growfund.com', 'Admin123!')
]

for email, password in test_credentials:
    print(f"\nTesting: {email} / {password}")
    
    # Check if user exists
    try:
        user = User.objects.get(email=email)
        print(f"  ✓ User exists")
        
        # Test password directly
        password_valid = check_password(password, user.password)
        print(f"  Password check: {'✓ VALID' if password_valid else '✗ INVALID'}")
        
        # Test Django authenticate
        auth_user = authenticate(username=email, password=password)
        if auth_user:
            print(f"  ✓ Authentication SUCCESS")
        else:
            print(f"  ✗ Authentication FAILED")
            
            # Try with email field
            auth_user = authenticate(email=email, password=password)
            if auth_user:
                print(f"  ✓ Authentication SUCCESS (using email field)")
            else:
                print(f"  ✗ Authentication FAILED (both username and email)")
                
    except User.DoesNotExist:
        print(f"  ✗ User does not exist")

print("\n\n4. CHECKING AUTHENTICATION BACKEND")
print("-" * 70)
from django.conf import settings
print(f"Authentication backends:")
for backend in settings.AUTHENTICATION_BACKENDS:
    print(f"  - {backend}")

print("\n\n5. CREATING/FIXING TABBY ADMIN")
print("-" * 70)

email = 'Tabby@gmail.com'
password = 'Tabby123!'

try:
    user = User.objects.get(email=email)
    print(f"✓ User exists: {email}")
    print(f"  Resetting password and permissions...")
    
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_verified = True
    user.is_active = True
    user.first_name = 'Tabby'
    user.last_name = 'Admin'
    user.save()
    
    print(f"  ✓ User updated!")
    
except User.DoesNotExist:
    print(f"✓ Creating new user: {email}")
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name='Tabby',
        last_name='Admin'
    )
    print(f"  ✓ User created!")

# Verify the fix
print(f"\nVerifying Tabby admin:")
user = User.objects.get(email=email)
print(f"  Email: {user.email}")
print(f"  Active: {user.is_active}")
print(f"  Verified: {user.is_verified}")
print(f"  Staff: {user.is_staff}")
print(f"  Superuser: {user.is_superuser}")

# Test authentication
auth_user = authenticate(username=email, password=password)
if auth_user:
    print(f"  ✓ Authentication test: SUCCESS")
else:
    print(f"  ✗ Authentication test: FAILED")

print("\n" + "=" * 70)
print("FINAL CREDENTIALS TO USE")
print("=" * 70)
print(f"\nEmail: {email}")
print(f"Password: {password}")
print("\nTry logging in now!")
print("=" * 70)
