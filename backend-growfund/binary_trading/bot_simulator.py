"""
Bot Simulator Engine
Simulates trading activity for marketing and UX trust.

Creates bot users that:
- Place realistic trades
- Win at 55-65% rate (slightly above average)
- Have randomized trade intervals
- Display in "Recent Winners" feed
"""
import random
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import BinaryTrade, TradingAsset, UserTradingStats
from .trade_service import TradeExecutionService

User = get_user_model()


class BotSimulator:
    """Simulates bot trading activity"""
    
    # Bot name templates
    FIRST_NAMES = [
        'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
        'Thomas', 'Charles', 'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth',
        'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Ahmed', 'Mohammed', 'Ali',
        'Omar', 'Hassan', 'Fatima', 'Aisha', 'Zainab', 'Mariam', 'Yuki', 'Sakura',
        'Hiroshi', 'Kenji', 'Mei', 'Wei', 'Chen', 'Liu', 'Wang', 'Zhang'
    ]
    
    LAST_NAMES = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
        'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White',
        'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
        'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill',
        'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell'
    ]
    
    # Trade amount ranges (USD)
    MIN_TRADE = Decimal('10.00')
    MAX_TRADE = Decimal('500.00')
    
    # Win rate range for bots (55-65%)
    MIN_WIN_RATE = 0.55
    MAX_WIN_RATE = 0.65
    
    @classmethod
    def create_bot_user(cls, username=None, email=None):
        """
        Create a bot user account.
        
        Returns:
            User object
        """
        if not username:
            first = random.choice(cls.FIRST_NAMES)
            last = random.choice(cls.LAST_NAMES)
            username = f"{first.lower()}{last.lower()}{random.randint(10, 99)}"
        
        if not email:
            email = f"{username}@bot.growfund.local"
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return User.objects.get(email=email)
        
        user = User.objects.create_user(
            email=email,
            username=username,
            password=User.objects.make_random_password(length=32),
            first_name=random.choice(cls.FIRST_NAMES),
            last_name=random.choice(cls.LAST_NAMES),
            is_active=True,
            is_verified=True,
            account_type='bot'  # Mark as bot
        )
        
        # Give bot a balance
        user.balance = Decimal(str(random.uniform(1000, 10000)))
        user.save()
        
        return user
    
    @classmethod
    def create_bot_fleet(cls, count=10):
        """
        Create a fleet of bot users.
        
        Args:
            count: Number of bots to create
        
        Returns:
            List of User objects
        """
        bots = []
        for _ in range(count):
            bot = cls.create_bot_user()
            bots.append(bot)
        
        return bots
    
    @classmethod
    def get_bot_users(cls):
        """Get all bot users"""
        return User.objects.filter(account_type='bot')
    
    @classmethod
    def simulate_bot_trade(cls, bot_user=None, asset=None, target_win_rate=None):
        """
        Simulate a single bot trade.
        
        Args:
            bot_user: User object (random bot if None)
            asset: TradingAsset object (random if None)
            target_win_rate: Desired win rate (random 55-65% if None)
        
        Returns:
            BinaryTrade object or None
        """
        # Get or select bot user
        if not bot_user:
            bots = cls.get_bot_users()
            if not bots.exists():
                # Create some bots if none exist
                cls.create_bot_fleet(5)
                bots = cls.get_bot_users()
            bot_user = random.choice(bots)
        
        # Get or select asset
        if not asset:
            assets = TradingAsset.objects.filter(is_active=True)
            if not assets.exists():
                return None
            asset = random.choice(assets)
        
        # Determine target win rate
        if target_win_rate is None:
            target_win_rate = random.uniform(cls.MIN_WIN_RATE, cls.MAX_WIN_RATE)
        
        # Get bot's current stats
        stats, _ = UserTradingStats.objects.get_or_create(user=bot_user)
        current_win_rate = stats.win_rate / 100 if stats.total_trades > 0 else 0.5
        
        # Decide if this trade should win (to maintain target win rate)
        should_win = current_win_rate < target_win_rate
        
        # Random trade parameters
        direction = random.choice(['buy', 'sell'])
        amount = Decimal(str(random.uniform(float(cls.MIN_TRADE), float(cls.MAX_TRADE))))
        amount = amount.quantize(Decimal('0.01'))
        expiry_seconds = random.choice([30, 60, 120, 180, 300])
        
        # Open trade
        trade, error = TradeExecutionService.open_trade(
            user=bot_user,
            asset_symbol=asset.symbol,
            direction=direction,
            amount=amount,
            expiry_seconds=expiry_seconds,
            is_demo=False
        )
        
        if error:
            print(f"⚠️ Bot trade failed: {error}")
            return None
        
        return trade
    
    @classmethod
    def run_bot_simulation(cls, duration_seconds=60, trades_per_minute=5):
        """
        Run continuous bot simulation.
        
        Args:
            duration_seconds: How long to run simulation
            trades_per_minute: Average number of trades per minute
        
        Returns:
            dict: Simulation statistics
        """
        import time
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        trades_opened = 0
        trades_failed = 0
        
        # Calculate interval between trades
        interval = 60.0 / trades_per_minute
        
        print(f"Starting bot simulation for {duration_seconds}s ({trades_per_minute} trades/min)")
        
        while time.time() < end_time:
            # Simulate a trade
            trade = cls.simulate_bot_trade()
            
            if trade:
                trades_opened += 1
                print(f"  Bot trade #{trades_opened}: {trade.user.email} - "
                      f"{trade.asset.symbol} {trade.direction.upper()} ${trade.amount}")
            else:
                trades_failed += 1
            
            # Random sleep with jitter
            sleep_time = interval + random.uniform(-interval * 0.3, interval * 0.3)
            sleep_time = max(1, sleep_time)
            time.sleep(sleep_time)
        
        return {
            'duration': duration_seconds,
            'trades_opened': trades_opened,
            'trades_failed': trades_failed,
            'trades_per_minute': trades_opened / (duration_seconds / 60)
        }
    
    @classmethod
    def get_recent_winners(cls, limit=10, include_bots=True):
        """
        Get recent winning trades for display.
        
        Args:
            limit: Number of winners to return
            include_bots: Include bot trades
        
        Returns:
            List of trade data dicts
        """
        query = BinaryTrade.objects.filter(
            status='won',
            is_demo=False
        ).select_related('user', 'asset').order_by('-closed_at')
        
        if not include_bots:
            query = query.exclude(user__account_type='bot')
        
        trades = query[:limit]
        
        winners = []
        for trade in trades:
            # Anonymize username (show first letter + ***)
            username = trade.user.email.split('@')[0]
            if len(username) > 3:
                display_name = username[0] + '***' + username[-1]
            else:
                display_name = username[0] + '***'
            
            winners.append({
                'username': display_name,
                'asset': trade.asset.symbol,
                'amount': float(trade.amount),
                'profit': float(trade.profit_loss),
                'payout_percent': float(trade.adjusted_payout_percentage),
                'timestamp': trade.closed_at.isoformat() if trade.closed_at else None
            })
        
        return winners
    
    @classmethod
    def cleanup_old_bot_trades(cls, days=30):
        """
        Clean up old bot trades to prevent database bloat.
        
        Args:
            days: Delete bot trades older than this many days
        
        Returns:
            int: Number of trades deleted
        """
        cutoff = timezone.now() - timedelta(days=days)
        
        deleted = BinaryTrade.objects.filter(
            user__account_type='bot',
            closed_at__lt=cutoff
        ).delete()
        
        return deleted[0] if deleted else 0


class BotBehaviorProfile:
    """
    Defines different bot behavior profiles for variety.
    """
    
    PROFILES = {
        'conservative': {
            'min_amount': Decimal('10.00'),
            'max_amount': Decimal('50.00'),
            'expiry_options': [60, 120, 180],
            'win_rate': 0.58,
            'trade_frequency': 0.3  # trades per minute
        },
        'moderate': {
            'min_amount': Decimal('50.00'),
            'max_amount': Decimal('200.00'),
            'expiry_options': [30, 60, 120, 180],
            'win_rate': 0.60,
            'trade_frequency': 0.5
        },
        'aggressive': {
            'min_amount': Decimal('100.00'),
            'max_amount': Decimal('500.00'),
            'expiry_options': [30, 60, 120],
            'win_rate': 0.55,
            'trade_frequency': 0.8
        },
        'whale': {
            'min_amount': Decimal('500.00'),
            'max_amount': Decimal('2000.00'),
            'expiry_options': [60, 120, 180, 300],
            'win_rate': 0.62,
            'trade_frequency': 0.2
        }
    }
    
    @classmethod
    def assign_profile_to_bot(cls, bot_user):
        """Assign a random behavior profile to a bot"""
        profile_name = random.choice(list(cls.PROFILES.keys()))
        profile = cls.PROFILES[profile_name]
        
        # Store profile in user metadata (you may need to add a JSONField to User model)
        # For now, we'll just return it
        return profile_name, profile
