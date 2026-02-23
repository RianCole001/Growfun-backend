#!/usr/bin/env python
"""
Simple script to check current platform settings in the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from settings_app.models import PlatformSettings

def check_settings():
    print("🔧 Checking Platform Settings in Database...")
    
    try:
        settings = PlatformSettings.get_settings()
        print(f"✅ Settings found with ID: {settings.id}")
        print(f"📊 Platform Name: {settings.platform_name}")
        print(f"📊 Platform Email: {settings.platform_email}")
        
        print("\n💰 Individual Plan Minimums:")
        print(f"  - Capital Basic Min: ${settings.capital_basic_min}")
        print(f"  - Capital Standard Min: ${settings.capital_standard_min}")
        print(f"  - Capital Advance Min: ${settings.capital_advance_min}")
        print(f"  - Real Estate Starter Min: ${settings.real_estate_starter_min}")
        print(f"  - Real Estate Premium Min: ${settings.real_estate_premium_min}")
        print(f"  - Real Estate Luxury Min: ${settings.real_estate_luxury_min}")
        
        print(f"\n📅 Last Updated: {settings.updated_at}")
        print(f"👤 Updated By: {settings.updated_by}")
        
        # Test updating a value
        print("\n🧪 Testing update...")
        old_basic_min = settings.capital_basic_min
        settings.capital_basic_min = 150
        settings.save()
        print(f"✅ Updated capital_basic_min from {old_basic_min} to {settings.capital_basic_min}")
        
        # Revert the change
        settings.capital_basic_min = old_basic_min
        settings.save()
        print(f"🔄 Reverted capital_basic_min back to {settings.capital_basic_min}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_settings()