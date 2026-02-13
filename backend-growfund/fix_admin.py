#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Admin credentials
admins = [
    {
        'email': 'admin@growfund.com',
        'password': 'Admin123!',
        'first_name': 'Admin',
        'last_name': 'User'
    },
    {
        'email': 'admin001@gmail.com',
        'password': 'Buffers316!',
        'first_name': 'Admin',
        'last_name': 'One'
    }
]

print("=" * 60)
print("ADMIN USER SETUP")
print("=" * 60)

# Create or update admin users
for admin_data in admins:
    email = admin_data['email']
    try:
        admin = User.objects.get(email=email)
        print(f"\n✓ Admin user found: {admin.email}")
        print(f"  is_staff: {admin.is_staff}")
        print(f"  is_superuser: {admin.is_superuser}")
        print(f"  is_verified: {admin.is_verified}")
        
        # Fix permissions
        if not admin.is_staff or not admin.is_superuser or not admin.is_verified:
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_verified = True
            admin.save()
            print("\n  ✓ Permissions updated!")
            print(f"    is_staff: {admin.is_staff}")
            print(f"    is_superuser: {admin.is_superuser}")
            print(f"    is_verified: {admin.is_verified}")
        else:
            print("\n  ✓ Already has all permissions!")
            
    except User.DoesNotExist:
        print(f"\n✓ Creating admin user: {email}")
        admin = User.objects.create_superuser(
            email=email,
            password=admin_data['password'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name']
        )
        print(f"  ✓ Created successfully!")
        print(f"    is_staff: {admin.is_staff}")
        print(f"    is_superuser: {admin.is_superuser}")
        print(f"    is_verified: {admin.is_verified}")

# List all users
print("\n" + "=" * 60)
print("ALL USERS IN DATABASE")
print("=" * 60)
all_users = User.objects.all()
print(f"\nTotal users: {all_users.count()}\n")
for user in all_users:
    admin_badge = " [ADMIN]" if (user.is_staff or user.is_superuser) else ""
    verified_badge = " [VERIFIED]" if user.is_verified else " [PENDING]"
    print(f"  {user.email}{admin_badge}{verified_badge}")
    print(f"    staff: {user.is_staff}, superuser: {user.is_superuser}")

print("\n" + "=" * 60)
print("ADMIN LOGIN CREDENTIALS")
print("=" * 60)
for admin_data in admins:
    print(f"\nAdmin 1:")
    print(f"  Email: {admin_data['email']}")
    print(f"  Password: {admin_data['password']}")
print("\n" + "=" * 60)
