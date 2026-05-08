"""
Quick setup script for binary trading system.
Run this after migrations to initialize the system.

Usage:
    python manage.py shell < binary_trading/setup_binary_trading.py
    
Or:
    python manage.py shell
    >>> exec(open('binary_trading/setup_binary_trading.py').read())
"""
from decimal import Decimal
from binary_trading.models import TradingAsset, HouseEdgeConfig
from binary_trading.bot_simulator import BotSimulator

print("=" * 60)
print("Binary Trading System Setup")
print("=" * 60)

# 1. Create Trading Assets
print("\n1. Creating trading assets...")

assets_data = [
    # Forex
    {
        'symbol': 'EURUSD',
        'name': 'Euro/US Dollar',
        'asset_type': 'forex',
        'base_payout': Decimal('85.00'),
        'volatility': Decimal('0.0030'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('5000.00')
    },
    {
        'symbol': 'GBPUSD',
        'name': 'British Pound/US Dollar',
        'asset_type': 'forex',
        'base_payout': Decimal('85.00'),
        'volatility': Decimal('0.0035'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('5000.00')
    },
    {
        'symbol': 'USDJPY',
        'name': 'US Dollar/Japanese Yen',
        'asset_type': 'forex',
        'base_payout': Decimal('84.00'),
        'volatility': Decimal('0.0032'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('5000.00')
    },
    
    # Crypto
    {
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'asset_type': 'crypto',
        'base_payout': Decimal('80.00'),
        'volatility': Decimal('0.0100'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('10000.00')
    },
    {
        'symbol': 'ETH',
        'name': 'Ethereum',
        'asset_type': 'crypto',
        'base_payout': Decimal('82.00'),
        'volatility': Decimal('0.0120'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('10000.00')
    },
    {
        'symbol': 'BNB',
        'name': 'Binance Coin',
        'asset_type': 'crypto',
        'base_payout': Decimal('81.00'),
        'volatility': Decimal('0.0110'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('5000.00')
    },
    
    # Commodities
    {
        'symbol': 'GOLD',
        'name': 'Gold',
        'asset_type': 'commodity',
        'base_payout': Decimal('85.00'),
        'volatility': Decimal('0.0040'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('5000.00')
    },
    {
        'symbol': 'OIL',
        'name': 'Crude Oil',
        'asset_type': 'commodity',
        'base_payout': Decimal('83.00'),
        'volatility': Decimal('0.0080'),
        'min_trade_amount': Decimal('10.00'),
        'max_trade_amount': Decimal('5000.00')
    },
]

created_count = 0
for asset_data in assets_data:
    asset, created = TradingAsset.objects.get_or_create(
        symbol=asset_data['symbol'],
        defaults=asset_data
    )
    if created:
        print(f"  ✓ Created {asset.symbol} - {asset.name}")
        created_count += 1
    else:
        print(f"  - {asset.symbol} already exists")

print(f"\nCreated {created_count} new assets")

# 2. Create House Edge Configuration
print("\n2. Creating house edge configuration...")

config, created = HouseEdgeConfig.objects.get_or_create(
    name='Default',
    defaults={
        'win_streak_3_reduction': Decimal('5.00'),
        'win_streak_5_reduction': Decimal('10.00'),
        'high_amount_threshold': Decimal('1000.00'),
        'high_amount_reduction': Decimal('3.00'),
        'very_high_amount_threshold': Decimal('5000.00'),
        'very_high_amount_reduction': Decimal('5.00'),
        'high_profit_threshold': Decimal('1000.00'),
        'high_profit_reduction': Decimal('10.00'),
        'strike_price_adjustment': Decimal('0.0010'),
        'atm_is_loss': True,
        'min_delay_ms': 100,
        'max_delay_ms': 500,
        'max_open_trades_per_user': 10,
        'max_exposure_per_asset': Decimal('5000.00'),
        'max_total_exposure': Decimal('10000.00'),
        'is_active': True
    }
)

if created:
    print("  ✓ Created house edge configuration")
else:
    print("  - House edge configuration already exists")

# 3. Initialize Price Feed
print("\n3. Initializing price feed...")

from binary_trading.price_feed import PriceFeedService

PriceFeedService.initialize_prices()
print("  ✓ Price feed initialized")

# 4. Create Bot Users (Optional)
print("\n4. Creating bot users...")

existing_bots = BotSimulator.get_bot_users().count()
if existing_bots < 5:
    bots_to_create = 10 - existing_bots
    bots = BotSimulator.create_bot_fleet(bots_to_create)
    print(f"  ✓ Created {len(bots)} bot users")
else:
    print(f"  - {existing_bots} bot users already exist")

# 5. Summary
print("\n" + "=" * 60)
print("Setup Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Start Redis server:")
print("   redis-server")
print("\n2. Run Django server:")
print("   python manage.py runserver")
print("\n3. Run price generator (in separate terminal):")
print("   python manage.py run_price_generator")
print("\n4. Run trade closer (in separate terminal):")
print("   python manage.py close_expired_trades")
print("\n5. (Optional) Run bot simulator (in separate terminal):")
print("   python manage.py run_bot_simulator --trades-per-minute 3")
print("\n6. Test WebSocket connection:")
print("   ws://localhost:8000/ws/binary-trading/prices/")
print("\n" + "=" * 60)
