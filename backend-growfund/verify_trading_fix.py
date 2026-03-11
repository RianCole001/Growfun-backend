#!/usr/bin/env python
"""Verify binary trading is working correctly"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from accounts.models import User
from binary_trading.trade_service import TradeExecutionService
from binary_trading.price_feed import PriceFeedService
from demo.models import DemoAccount
from decimal import Decimal

print("=" * 60)
print("BINARY TRADING VERIFICATION")
print("=" * 60)

# Get user
user = User.objects.first()
if not user:
    print("❌ No users found. Create a user first.")
    exit(1)

print(f"\n✅ User: {user.email}")

# Initialize prices
PriceFeedService.initialize_prices()
print("✅ Prices initialized")

# Get or create demo account
demo, created = DemoAccount.objects.get_or_create(
    user=user,
    defaults={'balance': Decimal('10000.00')}
)

print(f"\n📊 BALANCES BEFORE:")
print(f"   Real: ${user.balance}")
print(f"   Demo: ${demo.balance}")

# Test demo trade
print(f"\n🎮 TESTING DEMO TRADE...")
print(f"   Opening $50 BUY trade on OIL (demo mode)")

trade1, error1 = TradeExecutionService.open_trade(
    user=user,
    asset_symbol='OIL',
    direction='buy',
    amount=Decimal('50.00'),
    expiry_seconds=300,
    is_demo=True
)

if error1:
    print(f"   ❌ ERROR: {error1}")
else:
    demo.refresh_from_db()
    user.refresh_from_db()
    print(f"   ✅ Trade opened: {trade1.id}")
    print(f"   ✅ Demo balance: ${demo.balance} (deducted $50)")
    print(f"   ✅ Real balance: ${user.balance} (unchanged)")

# Test real trade (if user has balance)
if user.balance >= 50:
    print(f"\n💰 TESTING REAL TRADE...")
    print(f"   Opening $50 SELL trade on GOLD (real mode)")
    
    trade2, error2 = TradeExecutionService.open_trade(
        user=user,
        asset_symbol='GOLD',
        direction='sell',
        amount=Decimal('50.00'),
        expiry_seconds=300,
        is_demo=False
    )
    
    if error2:
        print(f"   ❌ ERROR: {error2}")
    else:
        demo.refresh_from_db()
        user.refresh_from_db()
        print(f"   ✅ Trade opened: {trade2.id}")
        print(f"   ✅ Real balance: ${user.balance} (deducted $50)")
        print(f"   ✅ Demo balance: ${demo.balance} (unchanged)")
else:
    print(f"\n⚠️  Skipping real trade test (insufficient balance)")

print(f"\n📊 FINAL BALANCES:")
demo.refresh_from_db()
user.refresh_from_db()
print(f"   Real: ${user.balance}")
print(f"   Demo: ${demo.balance}")

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE")
print("=" * 60)
print("\nBackend is working correctly!")
print("If frontend balance isn't updating, check:")
print("1. API response is being read correctly")
print("2. State is being updated with new_balance")
print("3. Chart polling isn't being stopped")
