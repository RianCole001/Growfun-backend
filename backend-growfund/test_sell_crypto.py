#!/usr/bin/env python
"""Test script to check crypto sell functionality"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from investments.models import Trade
from investments.admin_models import AdminCryptoPrice

User = get_user_model()

# Get a test user (replace with actual username/email)
print("=== Checking Crypto Sell Setup ===\n")

# Check users
users = User.objects.all()[:5]
print(f"Found {User.objects.count()} users")
for user in users:
    print(f"  - {user.email} (ID: {user.id})")

# Check open trades
print("\n=== Open Crypto Trades ===")
open_trades = Trade.objects.filter(status='open').exclude(asset='gold')
print(f"Found {open_trades.count()} open crypto trades")

for trade in open_trades[:10]:
    print(f"\nTrade ID: {trade.id}")
    print(f"  User: {trade.user.email}")
    print(f"  Asset: {trade.asset}")
    print(f"  Quantity: {trade.quantity}")
    print(f"  Entry Price: ${trade.entry_price}")
    print(f"  Current Price: ${trade.current_price}")
    print(f"  Status: {trade.status}")

# Check AdminCryptoPrice
print("\n=== Admin Crypto Prices ===")
admin_prices = AdminCryptoPrice.objects.filter(is_active=True)
print(f"Found {admin_prices.count()} active crypto prices")

for price in admin_prices:
    print(f"\n{price.coin}:")
    print(f"  Buy Price: ${price.buy_price}")
    print(f"  Sell Price: ${price.sell_price}")
    print(f"  Active: {price.is_active}")

# Test sell data format
print("\n=== Test Sell Data Format ===")
if open_trades.exists():
    test_trade = open_trades.first()
    print(f"Example sell request data:")
    print(f"{{")
    print(f"  'investment_id': '{test_trade.id}',")
    print(f"  'coin': '{test_trade.asset}',")
    print(f"  'quantity': {float(test_trade.quantity)}")
    print(f"}}")
else:
    print("No open trades found to test with")
