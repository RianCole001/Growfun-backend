#!/usr/bin/env python
"""
Simple script to create admin users
Run with: py manage.py shell < setup_admins.py
"""

from django.contrib.auth import get_user_model

User = get_user_model()

# Admin credentials
admins = [
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

print("=" * 60)
print("CREATING ADMIN USERS")
print("=" * 60)

for admin_data in admins:
    email = admin_data['email']
    try:
        admin = User.objects.get(email=email)
        print(f"\n✓ Admin exists: {email}")
        
        # Fix permissions
        if not admin.is_staff or not admin.is_superuser or not admin.is_verified:
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_verified = True
            admin.save()
            print(f"  ✓ Updated permissions")
        else:
            print(f"  ✓ Already has all permissions")
            
    except User.DoesNotExist:
        print(f"\n✓ Creating: {email}")
        admin = User.objects.create_superuser(
            email=email,
            password=admin_data['password'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name']
        )
        print(f"  ✓ Created successfully")

print("\n" + "=" * 60)
print("ADMIN CREDENTIALS")
print("=" * 60)
print("\nAdmin 1:")
print("  Email: admin001@gmail.com")
print("  Password: Buffers316!")
print("\nAdmin 2:")
print("  Email: admin@growfund.com")
print("  Password: Admin123!")
print("\n" + "=" * 60)
