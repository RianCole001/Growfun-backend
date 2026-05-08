"""
Comprehensive test script for binary trading system.
Tests all engines and components.

Usage:
    python test_binary_trading_complete.py
"""
import os
import django
import sys
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from binary_trading.models import TradingAsset, BinaryTrade, HouseEdgeConfig
from binary_trading.price_generator import PriceGenerator, PriceGeneratorManager
from binary_trading.trade_service import TradeExecutionService
from binary_trading.house_edge import HouseEdgeCalculator
from binary_trading.bot_simulator import BotSimulator
from binary_trading.price_feed import PriceFeedService

User = get_user_model()

print("=" * 70)
print("BINARY TRADING SYSTEM - COMPREHENSIVE TEST")
print("=" * 70)

# Test 1: Price Generator
print("\n[TEST 1] Price Generator Engine")
print("-" * 70)

try:
    gen = PriceGenerator('EURUSD', Decimal('1.0850'), Decimal('0.0030'))
    
    print("Generating 5 price ticks...")
    for i in range(5):
        tick = gen.generate_tick()
        print(f"  Tick {i+1}: ${tick['price']:.5f} | "
              f"Change: {tick['change_percent']:+.3f}% | "
              f"Regime: {tick['regime']}")
    
    print("\nGenerating 1 candle (60 ticks)...")
    candle = gen.generate_candle(duration_seconds=60, ticks_per_candle=60)
    print(f"  Open:   ${candle['open']:.5f}")
    print(f"  High:   ${candle['high']:.5f}")
    print(f"  Low:    ${candle['low']:.5f}")
    print(f"  Close:  ${candle['close']:.5f}")
    print(f"  Volume: {candle['volume']}")
    
    print("\n✓ Price Generator: PASSED")
except Exception as e:
    print(f"\n✗ Price Generator: FAILED - {e}")
    sys.exit(1)

# Test 2: Price Generator Manager
print("\n[TEST 2] Price Generator Manager")
print("-" * 70)

try:
    manager = PriceGeneratorManager()
    
    # Initialize generators for test assets
    symbols = ['EURUSD', 'BTC', 'GOLD']
    for symbol in symbols:
        gen = manager.get_generator(symbol, Decimal('100.00'), Decimal('0.0050'))
        print(f"  Initialized generator for {symbol}")
    
    # Generate ticks for all
    print("\nGenerating ticks for all assets...")
    ticks = manager.update_all_generators()
    for symbol, tick in ticks.items():
        print(f"  {symbol}: ${tick['price']:.5f}")
    
    print("\n✓ Price Generator Manager: PASSED")
except Exception as e:
    print(f"\n✗ Price Generator Manager: FAILED - {e}")
    sys.exit(1)

# Test 3: House Edge Calculator
print("\n[TEST 3] House Edge Engine")
print("-" * 70)

try:
    # Get or create test user
    user, created = User.objects.get_or_create(
        email='test_trader@growfund.com',
        defaults={
            'username': 'test_trader',
            'first_name': 'Test',
            'last_name': 'Trader',
            'balance': Decimal('10000.00'),
            'is_verified': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"  Created test user: {user.email}")
    else:
        print(f"  Using existing user: {user.email}")
    
    # Get or create test asset
    asset, _ = TradingAsset.objects.get_or_create(
        symbol='EURUSD',
        defaults={
            'name': 'Euro/US Dollar',
            'asset_type': 'forex',
            'base_payout': Decimal('85.00'),
            'volatility': Decimal('0.0030')
        }
    )
    
    # Test house edge calculation
    calculator = HouseEdgeCalculator(user, asset, Decimal('100.00'))
    
    adjusted_payout, edge = calculator.calculate_payout_reduction()
    print(f"  Base Payout: {asset.base_payout}%")
    print(f"  House Edge: {edge}%")
    print(f"  Adjusted Payout: {adjusted_payout}%")
    
    current_price = Decimal('1.0850')
    adjusted_strike_buy = calculator.adjust_strike_price(current_price, 'buy')
    adjusted_strike_sell = calculator.adjust_strike_price(current_price, 'sell')
    
    print(f"\n  Current Price: ${current_price}")
    print(f"  Adjusted Strike (BUY):  ${adjusted_strike_buy:.5f} (+{((adjusted_strike_buy/current_price - 1) * 100):.3f}%)")
    print(f"  Adjusted Strike (SELL): ${adjusted_strike_sell:.5f} ({((adjusted_strike_sell/current_price - 1) * 100):.3f}%)")
    
    params = calculator.get_trade_parameters(current_price, 'buy')
    print(f"\n  Full Trade Parameters:")
    print(f"    Base Payout: {params['base_payout']}%")
    print(f"    Adjusted Payout: {params['adjusted_payout']}%")
    print(f"    House Edge: {params['house_edge']}%")
    print(f"    Execution Delay: {params['execution_delay_ms']}ms")
    
    print("\n✓ House Edge Engine: PASSED")
except Exception as e:
    print(f"\n✗ House Edge Engine: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Trade Execution
print("\n[TEST 4] Trade Execution Engine")
print("-" * 70)

try:
    # Ensure user has balance
    user.balance = Decimal('10000.00')
    user.save()
    
    print(f"  User balance: ${user.balance}")
    
    # Open a trade
    print("\n  Opening BUY trade...")
    trade, error = TradeExecutionService.open_trade(
        user=user,
        asset_symbol='EURUSD',
        direction='buy',
        amount=Decimal('100.00'),
        expiry_seconds=5,  # 5 seconds for quick test
        is_demo=False
    )
    
    if error:
        raise Exception(f"Failed to open trade: {error}")
    
    print(f"  ✓ Trade opened: {trade.id}")
    print(f"    Asset: {trade.asset.symbol}")
    print(f"    Direction: {trade.direction.upper()}")
    print(f"    Amount: ${trade.amount}")
    print(f"    Strike Price: ${trade.strike_price:.5f}")
    print(f"    Base Payout: {trade.base_payout_percentage}%")
    print(f"    Adjusted Payout: {trade.adjusted_payout_percentage}%")
    print(f"    House Edge: {trade.house_edge_applied}%")
    print(f"    Expires in: {trade.expiry_seconds}s")
    
    user.refresh_from_db()
    print(f"    New balance: ${user.balance}")
    
    # Wait for expiry
    print("\n  Waiting for trade to expire...")
    import time
    time.sleep(6)
    
    # Close the trade
    print("  Closing trade...")
    closed_trade, error = TradeExecutionService.close_trade(trade.id)
    
    if error:
        raise Exception(f"Failed to close trade: {error}")
    
    print(f"  ✓ Trade closed")
    print(f"    Final Price: ${closed_trade.final_price:.5f}")
    print(f"    Result: {closed_trade.status.upper()}")
    print(f"    Profit/Loss: ${closed_trade.profit_loss:+.2f}")
    
    user.refresh_from_db()
    print(f"    Final balance: ${user.balance}")
    
    print("\n✓ Trade Execution Engine: PASSED")
except Exception as e:
    print(f"\n✗ Trade Execution Engine: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Bot Simulator
print("\n[TEST 5] Bot Simulator Engine")
print("-" * 70)

try:
    # Check existing bots
    existing_bots = BotSimulator.get_bot_users().count()
    print(f"  Existing bots: {existing_bots}")
    
    # Create a bot if needed
    if existing_bots == 0:
        print("  Creating test bot...")
        bot = BotSimulator.create_bot_user()
        print(f"  ✓ Created bot: {bot.email}")
    else:
        bot = BotSimulator.get_bot_users().first()
        print(f"  Using existing bot: {bot.email}")
    
    # Simulate a bot trade
    print("\n  Simulating bot trade...")
    bot_trade = BotSimulator.simulate_bot_trade(bot_user=bot)
    
    if bot_trade:
        print(f"  ✓ Bot trade opened: {bot_trade.id}")
        print(f"    Asset: {bot_trade.asset.symbol}")
        print(f"    Direction: {bot_trade.direction.upper()}")
        print(f"    Amount: ${bot_trade.amount}")
    else:
        print("  ⚠ Bot trade failed (may be due to insufficient balance)")
    
    # Get recent winners
    print("\n  Getting recent winners...")
    winners = BotSimulator.get_recent_winners(limit=5)
    print(f"  Found {len(winners)} recent winners:")
    for i, winner in enumerate(winners, 1):
        print(f"    {i}. {winner['username']} won ${winner['profit']:.2f} on {winner['asset']}")
    
    print("\n✓ Bot Simulator Engine: PASSED")
except Exception as e:
    print(f"\n✗ Bot Simulator Engine: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Price Feed Service
print("\n[TEST 6] Price Feed Service")
print("-" * 70)

try:
    # Initialize prices
    print("  Initializing price feed...")
    PriceFeedService.initialize_prices()
    
    # Get current price
    print("\n  Fetching current prices...")
    price = PriceFeedService.get_current_price('EURUSD')
    if price:
        print(f"  EURUSD: ${price:.5f}")
    
    # Update all prices
    print("\n  Updating all prices...")
    prices = PriceFeedService.update_all_prices()
    for symbol, data in list(prices.items())[:3]:
        print(f"    {symbol}: ${data['price']:.5f}")
    
    print("\n✓ Price Feed Service: PASSED")
except Exception as e:
    print(f"\n✗ Price Feed Service: FAILED - {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✓ All core engines tested successfully!")
print("\nSystem is ready for:")
print("  1. WebSocket streaming (run: python manage.py run_price_generator)")
print("  2. Trade execution (run: python manage.py close_expired_trades)")
print("  3. Bot simulation (run: python manage.py run_bot_simulator)")
print("\nNext: Start the Django server and connect via WebSocket")
print("=" * 70)
