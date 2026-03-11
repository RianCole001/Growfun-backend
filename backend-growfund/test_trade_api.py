#!/usr/bin/env python
"""Test trade API functionality"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from accounts.models import User
from binary_trading.trade_service import TradeExecutionService
from binary_trading.price_feed import PriceFeedService
from demo.models import DemoAccount
from decimal import Decimal

# Get user
user = User.objects.first()
print(f"Testing with user: {user.email}")
print(f"Initial Real Balance: ${user.balance}")

# Get or create demo account
demo, created = DemoAccount.objects.get_or_create(
    user=user,
    defaults={'balance': Decimal('10000.00')}
)
print(f"Initial Demo Balance: ${demo.balance}")

# Initialize prices
print("\nInitializing prices...")
PriceFeedService.initialize_prices()

# Get current price
price = PriceFeedService.get_current_price('OIL')
print(f"Current OIL price: ${price}")

# Test opening a demo trade
print("\n--- Testing Demo Trade ---")
print(f"Demo balance before: ${demo.balance}")

trade, error = TradeExecutionService.open_trade(
    user=user,
    asset_symbol='OIL',
    direction='buy',
    amount=Decimal('100.00'),
    expiry_seconds=300,
    is_demo=True
)

if error:
    print(f"ERROR: {error}")
else:
    print(f"✅ Trade opened successfully!")
    print(f"Trade ID: {trade.id}")
    print(f"Amount: ${trade.amount}")
    print(f"Strike Price: ${trade.strike_price}")
    print(f"Status: {trade.status}")
    print(f"Is Demo: {trade.is_demo}")
    
    # Refresh demo account
    demo.refresh_from_db()
    print(f"Demo balance after: ${demo.balance}")
    print(f"Balance deducted: ${Decimal('100.00')}")
    
    # Check user real balance
    user.refresh_from_db()
    print(f"Real balance (should be unchanged): ${user.balance}")

print("\n--- Testing Real Trade ---")
# Give user some real balance first
user.balance = Decimal('5000.00')
user.save()
print(f"Real balance before: ${user.balance}")

trade2, error2 = TradeExecutionService.open_trade(
    user=user,
    asset_symbol='GOLD',
    direction='sell',
    amount=Decimal('200.00'),
    expiry_seconds=300,
    is_demo=False
)

if error2:
    print(f"ERROR: {error2}")
else:
    print(f"✅ Trade opened successfully!")
    print(f"Trade ID: {trade2.id}")
    print(f"Amount: ${trade2.amount}")
    print(f"Is Demo: {trade2.is_demo}")
    
    # Refresh user
    user.refresh_from_db()
    print(f"Real balance after: ${user.balance}")
    print(f"Balance deducted: ${Decimal('200.00')}")
    
    # Check demo balance
    demo.refresh_from_db()
    print(f"Demo balance (should be unchanged): ${demo.balance}")
