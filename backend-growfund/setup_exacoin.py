#!/usr/bin/env python
"""Setup ExaCoin with flexible pricing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from investments.admin_models import AdminCryptoPrice
from decimal import Decimal

print('=== EXACOIN SETUP ===')

# Create or update ExaCoin
exacoin, created = AdminCryptoPrice.objects.get_or_create(
    coin='EXACOIN',
    defaults={
        'name': 'ExaCoin',
        'buy_price': Decimal('62.00'),
        'sell_price': Decimal('59.50'),
        'change_24h': Decimal('3.33'),
        'is_active': True
    }
)

if created:
    print('✓ Created new EXACOIN price record')
else:
    print('✓ EXACOIN already exists')

# Test flexible pricing (sell > buy should work now)
print('\n=== TESTING FLEXIBLE PRICING ===')
exacoin.buy_price = Decimal('50.00')
exacoin.sell_price = Decimal('55.00')  # Higher than buy price
exacoin.save(skip_validation=True)
print(f'✓ Set EXACOIN: Buy ${exacoin.buy_price}, Sell ${exacoin.sell_price}')

# Reset to normal pricing
exacoin.buy_price = Decimal('62.00')
exacoin.sell_price = Decimal('59.50')
exacoin.save(skip_validation=True)
print(f'✓ Reset EXACOIN: Buy ${exacoin.buy_price}, Sell ${exacoin.sell_price}')

print('\n=== SETUP COMPLETE ===')