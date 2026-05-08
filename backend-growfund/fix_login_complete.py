#!/usr/bin/env python
"""Complete fix for admin login issues"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

User = get_user_model()

print("=" * 70)
print("COMPLETE LOGIN FIX")
print("=" * 70)

# Step 1: Verify authentication backend
print("\n1. CHECKING AUTHENTICATION BACKEND")
print("-" * 70)
print("Authentication backends configured:")
for backend in settings.AUTHENTICATION_BACKENDS:
    print(f"  ✓ {backend}")

if 'accounts.backends.EmailBackend' in settings.AUTHENTICATION_BACKENDS:
    print("\n✓ Custom EmailBackend is configured!")
else:
    print("\n⚠ WARNING: Custom EmailBackend not found in settings!")
    print("  Add this to settings.py:")
    print("  AUTHENTICATION_BACKENDS = [")
    print("      'accounts.backends.EmailBackend',")
    print("      'django.contrib.auth.backends.ModelBackend',")
    print("  ]")

# Step 2: Create/Fix all admin accounts
print("\n\n2. CREATING/FIXING ADMIN ACCOUNTS")
print("-" * 70)

admin_accounts = [
    {
        'email': 'Tabby@gmail.com',
        'password': 'Tabby123!',
        'first_name': 'Tabby',
        'last_name': 'Admin'
    },
    {
        'email': 'admin001@gmail.com',
        'password': 'Buffers316!',
        'first_name': 'Admin',
        'last_name': 'One'
    },
    {
        'email': 'admin@growfund.com',
        'password': 'Admin123!',
        'first_name': 'Admin',
        'last_name': 'User'
    }
]

for admin_data in admin_accounts:
    email = admin_data['email']
    password = admin_data['password']
    
    try:
        user = User.objects.get(email=email)
        print(f"\n✓ Found: {email}")
        
        # Update user
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.is_active = True
        user.first_name = admin_data['first_name']
        user.last_name = admin_data['last_name']
        user.save()
        
        print(f"  ✓ Updated permissions and password")
        
    except User.DoesNotExist:
        print(f"\n✓ Creating: {email}")
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name']
        )
        print(f"  ✓ Created successfully")
    
    # Verify user details
    print(f"  Details:")
    print(f"    - Active: {user.is_active}")
    print(f"    - Verified: {user.is_verified}")
    print(f"    - Staff: {user.is_staff}")
    print(f"    - Superuser: {user.is_superuser}")

# Step 3: Test authentication
print("\n\n3. TESTING AUTHENTICATION")
print("-" * 70)

for admin_data in admin_accounts:
    email = admin_data['email']
    password = admin_data['password']
    
    print(f"\nTesting: {email}")
    
    # Test with username parameter (for compatibility)
    user = authenticate(username=email, password=password)
    if user:
        print(f"  ✓ Authentication SUCCESS (username param)")
    else:
        print(f"  ✗ Authentication FAILED (username param)")
    
    # Test with email parameter
    user = authenticate(email=email, password=password)
    if user:
        print(f"  ✓ Authentication SUCCESS (email param)")
    else:
        print(f"  ✗ Authentication FAILED (email param)")

# Step 4: Show all users
print("\n\n4. ALL USERS IN DATABASE")
print("-" * 70)
all_users = User.objects.all().order_by('-is_staff', '-is_superuser', 'email')
print(f"Total users: {all_users.count()}\n")

for user in all_users:
    role = "ADMIN" if (user.is_staff or user.is_superuser) else "USER"
    status = "✓" if user.is_active else "✗"
    verified = "✓" if user.is_verified else "✗"
    
    print(f"[{role}] {user.email}")
    print(f"  Active: {status} | Verified: {verified} | Balance: ${user.balance}")

# Step 5: Final instructions
print("\n\n" + "=" * 70)
print("LOGIN CREDENTIALS")
print("=" * 70)

for admin_data in admin_accounts:
    print(f"\n{admin_data['first_name']} {admin_data['last_name']}:")
    print(f"  Email: {admin_data['email']}")
    print(f"  Password: {admin_data['password']}")

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("\n1. Restart your Django server:")
print("   python manage.py runserver")
print("\n2. Try logging in with any of the credentials above")
print("\n3. If login still fails, check:")
print("   - Frontend is sending correct email/password")
print("   - Frontend is using correct API endpoint")
print("   - Check browser console for errors")
print("\n" + "=" * 70)
