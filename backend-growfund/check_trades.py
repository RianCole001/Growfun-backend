#!/usr/bin/env python
"""Check trade and balance status"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from accounts.models import User
from binary_trading.models import BinaryTrade, TradingAsset
from demo.models import DemoAccount

# Get first user
user = User.objects.first()
if not user:
    print("No users found!")
    exit()

print(f"User: {user.email}")
print(f"Real Balance: ${user.balance}")

# Check demo account
demo = DemoAccount.objects.filter(user=user).first()
if demo:
    print(f"Demo Balance: ${demo.balance}")
else:
    print("Demo Balance: No demo account")

# Check recent trades
trades = BinaryTrade.objects.filter(user=user).order_by('-opened_at')[:10]
print(f"\nRecent Trades: {trades.count()}")
for t in trades:
    print(f"  - {t.asset.symbol} {t.direction.upper()} ${t.amount} [{t.status}] Demo:{t.is_demo} Opened:{t.opened_at}")

# Check assets
assets = TradingAsset.objects.filter(is_active=True)
print(f"\nActive Assets: {assets.count()}")
for a in assets:
    print(f"  - {a.symbol}: {a.name}")
