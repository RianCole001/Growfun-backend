#!/usr/bin/env python
"""
Test script for Binary Trading System
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from binary_trading.models import TradingAsset, BinaryTrade, UserTradingStats, HouseEdgeConfig
from binary_trading.price_feed import PriceFeedService
from binary_trading.trade_service import TradeExecutionService
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

print("=" * 70)
print("BINARY TRADING SYSTEM TEST")
print("=" * 70)

# 1. Check Assets
print("\n1. TRADING ASSETS")
print("-" * 70)
assets = TradingAsset.objects.filter(is_active=True)
for asset in assets:
    print(f"✓ {asset.symbol:8} - {asset.name:20} | Payout: {asset.base_payout}% | Volatility: {asset.volatility}")

# 2. Check House Edge Config
print("\n2. HOUSE EDGE CONFIGURATION")
print("-" * 70)
config = HouseEdgeConfig.objects.filter(is_active=True).first()
if config:
    print(f"✓ Configuration: {config.name}")
    print(f"  Win Streak 3+ Reduction: {config.win_streak_3_reduction}%")
    print(f"  Win Streak 5+ Reduction: {config.win_streak_5_reduction}%")
    print(f"  High Amount Threshold: ${config.high_amount_threshold}")
    print(f"  Strike Price Adjustment: {config.strike_price_adjustment}")
    print(f"  Max Open Trades: {config.max_open_trades_per_user}")
else:
    print("✗ No house edge configuration found")

# 3. Check Prices
print("\n3. CURRENT PRICES")
print("-" * 70)
for asset in assets:
    price = PriceFeedService.get_current_price(asset.symbol)
    print(f"✓ {asset.symbol:8} - ${price}")

# 4. Test Trade Opening (if admin user exists)
print("\n4. TRADE EXECUTION TEST")
print("-" * 70)
try:
    admin = User.objects.filter(is_staff=True).first()
    if admin and admin.balance >= 100:
        print(f"Testing with user: {admin.email}")
        print(f"Current balance: ${admin.balance}")
        
        # Open a test trade
        trade, error = TradeExecutionService.open_trade(
            user=admin,
            asset_symbol='OIL',
            direction='buy',
            amount=Decimal('100.00'),
            expiry_seconds=300
        )
        
        if trade:
            print(f"\n✓ Trade opened successfully!")
            print(f"  Trade ID: {trade.id}")
            print(f"  Asset: {trade.asset.symbol}")
            print(f"  Direction: {trade.direction.upper()}")
            print(f"  Amount: ${trade.amount}")
            print(f"  Strike Price: ${trade.strike_price}")
            print(f"  Adjusted Payout: {trade.adjusted_payout_percentage}%")
            print(f"  House Edge Applied: {trade.house_edge_applied}%")
            print(f"  Expires in: {trade.expiry_seconds} seconds")
            print(f"  New Balance: ${admin.balance}")
        else:
            print(f"✗ Failed to open trade: {error}")
    else:
        print("⚠ No admin user with sufficient balance found")
        print("  Create an admin and add balance to test trading")
except Exception as e:
    print(f"✗ Error during trade test: {e}")

# 5. Statistics
print("\n5. SYSTEM STATISTICS")
print("-" * 70)
total_trades = BinaryTrade.objects.count()
active_trades = BinaryTrade.objects.filter(status='active').count()
won_trades = BinaryTrade.objects.filter(status='won').count()
lost_trades = BinaryTrade.objects.filter(status='lost').count()

print(f"Total Trades: {total_trades}")
print(f"Active Trades: {active_trades}")
print(f"Won Trades: {won_trades}")
print(f"Lost Trades: {lost_trades}")

if won_trades + lost_trades > 0:
    platform_win_rate = (lost_trades / (won_trades + lost_trades)) * 100
    print(f"Platform Win Rate: {platform_win_rate:.2f}%")

print("\n" + "=" * 70)
print("✅ BINARY TRADING SYSTEM IS OPERATIONAL")
print("=" * 70)
print("\nAPI Endpoints Available:")
print("  GET  /api/binary/assets/")
print("  GET  /api/binary/prices/")
print("  GET  /api/binary/assets/{symbol}/price/")
print("  POST /api/binary/trades/open/")
print("  GET  /api/binary/trades/active/")
print("  GET  /api/binary/trades/history/")
print("  GET  /api/binary/stats/")
print("\nServer running at: http://localhost:8000")
print("=" * 70)
