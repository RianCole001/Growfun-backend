#!/usr/bin/env python
"""
Quick script to reset admin password or show admin credentials
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from accounts.models import User

def reset_admin_password():
    print("=" * 60)
    print("ADMIN PASSWORD RESET")
    print("=" * 60)
    
    # Find admin user
    admin = User.objects.filter(email='admin@growfund.com').first()
    
    if not admin:
        print("\n❌ Admin user 'admin@growfund.com' not found!")
        print("\nCreating new admin user...")
        
        # Create new admin
        admin = User.objects.create_user(
            email='admin@growfund.com',
            password='Admin123!',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        print("✅ Admin user created!")
    else:
        print(f"\n✅ Found admin user: {admin.email}")
        print("\nResetting password...")
        admin.set_password('Admin123!')
        admin.save()
        print("✅ Password reset successfully!")
    
    print("\n" + "=" * 60)
    print("ADMIN LOGIN CREDENTIALS")
    print("=" * 60)
    print(f"Email:    admin@growfund.com")
    print(f"Password: Admin123!")
    print("=" * 60)
    print("\n📍 Admin Panel URLs:")
    print("   Localhost:  http://localhost:3000/admin")
    print("   ngrok:      https://fdc9-129-222-147-116.ngrok-free.app/admin")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    reset_admin_password()
