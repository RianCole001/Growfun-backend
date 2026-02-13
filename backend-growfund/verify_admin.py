#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("ADMIN VERIFICATION AND SETUP")
print("=" * 70)

# Admin credentials to create/verify
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

print("\n1. CHECKING/CREATING ADMIN USERS")
print("-" * 70)

for admin_data in admins:
    email = admin_data['email']
    try:
        admin = User.objects.get(email=email)
        print(f"\n✓ Admin exists: {email}")
        print(f"  is_staff: {admin.is_staff}")
        print(f"  is_superuser: {admin.is_superuser}")
        print(f"  is_verified: {admin.is_verified}")
        
        # Fix permissions if needed
        if not admin.is_staff or not admin.is_superuser or not admin.is_verified:
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_verified = True
            admin.save()
            print(f"  ✓ Updated permissions!")
        
    except User.DoesNotExist:
        print(f"\n✓ Creating admin: {email}")
        admin = User.objects.create_superuser(
            email=email,
            password=admin_data['password'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name']
        )
        print(f"  ✓ Created successfully!")
        print(f"  is_staff: {admin.is_staff}")
        print(f"  is_superuser: {admin.is_superuser}")
        print(f"  is_verified: {admin.is_verified}")

print("\n2. ALL USERS IN DATABASE")
print("-" * 70)
all_users = User.objects.all().order_by('-date_joined')
print(f"\nTotal users: {all_users.count()}\n")

for i, user in enumerate(all_users, 1):
    admin_badge = " [ADMIN]" if (user.is_staff or user.is_superuser) else ""
    verified_badge = " [VERIFIED]" if user.is_verified else " [PENDING]"
    print(f"{i}. {user.email}{admin_badge}{verified_badge}")
    print(f"   Name: {user.first_name} {user.last_name}")
    print(f"   Staff: {user.is_staff}, Superuser: {user.is_superuser}")
    print(f"   Created: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

print("=" * 70)
print("ADMIN LOGIN CREDENTIALS")
print("=" * 70)
print("\nAdmin 1:")
print("  Email: admin001@gmail.com")
print("  Password: Buffers316!")
print("\nAdmin 2:")
print("  Email: admin@growfund.com")
print("  Password: Admin123!")
print("\n" + "=" * 70)
