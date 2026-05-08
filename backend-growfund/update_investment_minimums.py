#!/usr/bin/env python
"""Update minimum investment amounts to $30 for starter plans"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from settings_app.models import PlatformSettings
from decimal import Decimal

print('=== UPDATING INVESTMENT MINIMUMS ===')

# Get or create settings
settings = PlatformSettings.get_settings()

print('\n=== CURRENT SETTINGS ===')
print(f'Capital Basic Min: ${settings.capital_basic_min}')
print(f'Capital Standard Min: ${settings.capital_standard_min}')
print(f'Capital Advance Min: ${settings.capital_advance_min}')
print(f'Real Estate Starter Min: ${settings.real_estate_starter_min}')
print(f'Real Estate Premium Min: ${settings.real_estate_premium_min}')
print(f'Real Estate Luxury Min: ${settings.real_estate_luxury_min}')
print(f'Min Crypto Investment: ${settings.min_crypto_investment}')

print('\n=== UPDATING TO $30 FOR STARTER PLANS ===')

# Update starter plan minimums to $30
settings.capital_basic_min = Decimal('30.00')
settings.real_estate_starter_min = Decimal('30.00')

# Also update crypto minimum to $30 for consistency
settings.min_crypto_investment = Decimal('30.00')

settings.save()

print('\n=== NEW SETTINGS ===')
print(f'Capital Basic Min: ${settings.capital_basic_min} ✓')
print(f'Capital Standard Min: ${settings.capital_standard_min}')
print(f'Capital Advance Min: ${settings.capital_advance_min}')
print(f'Real Estate Starter Min: ${settings.real_estate_starter_min} ✓')
print(f'Real Estate Premium Min: ${settings.real_estate_premium_min}')
print(f'Real Estate Luxury Min: ${settings.real_estate_luxury_min}')
print(f'Min Crypto Investment: ${settings.min_crypto_investment} ✓')

print('\n=== UPDATE COMPLETE ===')
print('Minimum investment for starter plans is now $30')