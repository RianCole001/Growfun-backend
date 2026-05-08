#!/usr/bin/env python
"""Quick script to create Tabby admin user"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Tabby admin credentials
email = 'Tabby@gmail.com'
password = 'Tabby123!'  # Change this to your desired password
first_name = 'Tabby'
last_name = 'Admin'

print("=" * 60)
print("CREATING TABBY ADMIN USER")
print("=" * 60)

try:
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        admin = User.objects.get(email=email)
        print(f"\n✓ User already exists: {admin.email}")
        print(f"  Updating permissions...")
        
        # Update permissions
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_verified = True
        admin.first_name = first_name
        admin.last_name = last_name
        admin.set_password(password)
        admin.save()
        
        print(f"\n✓ Admin user updated successfully!")
    else:
        # Create new admin user
        print(f"\n✓ Creating new admin user: {email}")
        admin = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        print(f"\n✓ Admin user created successfully!")
    
    # Display details
    print("\n" + "=" * 60)
    print("ADMIN USER DETAILS")
    print("=" * 60)
    print(f"\nEmail: {admin.email}")
    print(f"Password: {password}")
    print(f"Name: {admin.first_name} {admin.last_name}")
    print(f"Staff: {admin.is_staff}")
    print(f"Superuser: {admin.is_superuser}")
    print(f"Verified: {admin.is_verified}")
    print(f"Balance: ${admin.balance}")
    
    print("\n" + "=" * 60)
    print("LOGIN CREDENTIALS")
    print("=" * 60)
    print(f"\nEmail: {email}")
    print(f"Password: {password}")
    print("\nYou can now login to the admin panel!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
