#!/usr/bin/env python
"""
Script to verify all existing users in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("VERIFYING ALL USERS")
print("=" * 60)

# Get all unverified users
unverified_users = User.objects.filter(is_verified=False)
count = unverified_users.count()

if count == 0:
    print("\n✓ All users are already verified!")
else:
    print(f"\nFound {count} unverified user(s). Verifying now...")
    
    # Verify all users
    updated = unverified_users.update(is_verified=True)
    
    print(f"\n✓ Successfully verified {updated} user(s)!")
    
    # Show verified users
    print("\nVerified users:")
    for user in User.objects.filter(id__in=unverified_users.values_list('id', flat=True)):
        print(f"  - {user.email} ({user.get_full_name()})")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
