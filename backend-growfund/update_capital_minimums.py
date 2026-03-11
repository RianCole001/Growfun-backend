#!/usr/bin/env python
"""
Script to update capital plan minimum investment amounts
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from settings_app.models import PlatformSettings

print("=" * 60)
print("UPDATING CAPITAL PLAN MINIMUM INVESTMENTS")
print("=" * 60)

# Get or create platform settings
settings, created = PlatformSettings.objects.get_or_create(
    id=1,
    defaults={
        'capital_basic_min': Decimal('30.00'),
        'capital_standard_min': Decimal('60.00'),
        'capital_advance_min': Decimal('100.00'),
    }
)

if created:
    print("\n✓ Created new platform settings with updated minimums!")
else:
    print("\n📝 Updating existing platform settings...")
    
    # Update the minimums
    settings.capital_basic_min = Decimal('30.00')
    settings.capital_standard_min = Decimal('60.00')
    settings.capital_advance_min = Decimal('100.00')
    settings.save()
    
    print("✓ Successfully updated!")

print("\n" + "=" * 60)
print("CURRENT CAPITAL PLAN MINIMUMS")
print("=" * 60)
print(f"Basic Plan:    ${settings.capital_basic_min}")
print(f"Standard Plan: ${settings.capital_standard_min}")
print(f"Advance Plan:  ${settings.capital_advance_min}")
print("=" * 60)
