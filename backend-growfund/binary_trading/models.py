from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class TradingAsset(models.Model):
    """Available assets for binary trading"""
    ASSET_TYPES = [
        ('forex', 'Forex'),
        ('crypto', 'Cryptocurrency'),
        ('commodity', 'Commodity'),
        ('stock', 'Stock'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    base_payout = models.DecimalField(max_digits=5, decimal_places=2, default=85.00)
    volatility = models.DecimalField(max_digits=5, decimal_places=4, default=0.0050)
    is_active = models.BooleanField(default=True)
    min_trade_amount = models.DecimalField(max_digits=12, decimal_places=2, default=10.00)
    max_trade_amount = models.DecimalField(max_digits=12, decimal_places=2, default=5000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class HouseEdgeConfig(models.Model):
    """Configuration for house edge algorithm"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    
    # Payout reduction factors
    win_streak_3_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    win_streak_5_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    high_amount_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    high_amount_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)
    very_high_amount_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=5000.00)
    very_high_amount_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    high_profit_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    high_profit_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    
    # Strike price manipulation
    strike_price_adjustment = models.DecimalField(max_digits=5, decimal_places=4, default=0.0010)
    
    # ATM (at-the-money) rule: True = treat as loss (house keeps stake), False = refund stake
    atm_is_loss = models.BooleanField(default=True, help_text='If final price == strike price, treat as loss (True) or refund stake (False)')
    
    # Execution delay
    min_delay_ms = models.IntegerField(default=100)
    max_delay_ms = models.IntegerField(default=500)
    
    # Risk limits
    max_open_trades_per_user = models.IntegerField(default=10)
    max_exposure_per_asset = models.DecimalField(max_digits=12, decimal_places=2, default=5000.00)
    max_total_exposure = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name



class BinaryTrade(models.Model):
    """Binary options trade"""
    DIRECTION_CHOICES = [
        ('buy', 'Buy/Call'),
        ('sell', 'Sell/Put'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='binary_trades')
    asset = models.ForeignKey(TradingAsset, on_delete=models.PROTECT)
    
    # Demo mode flag
    is_demo = models.BooleanField(default=False)
    
    # Trade details
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    strike_price = models.DecimalField(max_digits=20, decimal_places=8)
    final_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    # Payout and house edge
    base_payout_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    adjusted_payout_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    house_edge_applied = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Timing
    expiry_seconds = models.IntegerField()
    opened_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Metadata
    execution_delay_ms = models.IntegerField(default=0)
    user_win_streak = models.IntegerField(default=0)
    user_total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.asset.symbol} {self.direction.upper()} ${self.amount}"



class UserTradingStats(models.Model):
    """Track user trading statistics for house edge calculation"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trading_stats')
    
    # Win/Loss tracking
    total_trades = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    current_win_streak = models.IntegerField(default=0)
    current_loss_streak = models.IntegerField(default=0)
    max_win_streak = models.IntegerField(default=0)
    
    # Financial tracking
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_volume = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Risk flags
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True, null=True)
    flagged_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Stats"
    
    @property
    def win_rate(self):
        if self.total_trades == 0:
            return 0
        return (self.total_wins / self.total_trades) * 100


class AssetPrice(models.Model):
    """Real-time price tracking for assets"""
    asset = models.ForeignKey(TradingAsset, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.asset.symbol} - ${self.price} at {self.timestamp}"
