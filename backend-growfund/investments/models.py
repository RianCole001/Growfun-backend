from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

# Import admin models
from .admin_models import AdminCryptoPrice, CryptoPriceHistory


class CapitalInvestmentPlan(models.Model):
    """Model for capital investment plans with monthly periods and growth rates"""
    
    PLAN_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('advance', 'Advance'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Growth rates for each plan type
    GROWTH_RATES = {
        'basic': 20,      # 20% per month
        'standard': 30,   # 30% per month
        'advance': 40,    # 40% per month (minimum for advance)
    }
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_plans')
    
    # Plan details
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Investment amount
    initial_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Period in months
    period_months = models.IntegerField()  # e.g., 3, 6, 12 months
    
    # Growth rate (percentage per month)
    growth_rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 40.00 for 40%
    
    # Calculated values
    total_return = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Monthly breakdown
    monthly_growth = models.JSONField(default=dict)  # Stores monthly growth details
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Capital Investment Plan'
        verbose_name_plural = 'Capital Investment Plans'
    
    def __str__(self):
        return f"{self.user.email} - {self.plan_type.upper()} - ${self.initial_amount}"
    
    def calculate_returns(self):
        """Calculate monthly returns and final amount"""
        monthly_breakdown = []
        current_amount = float(self.initial_amount)
        growth_rate = float(self.growth_rate) / 100
        
        for month in range(1, self.period_months + 1):
            monthly_gain = current_amount * growth_rate
            current_amount += monthly_gain
            
            monthly_breakdown.append({
                'month': month,
                'starting_amount': float(self.initial_amount) if month == 1 else monthly_breakdown[month-2]['ending_amount'],
                'growth_rate': float(self.growth_rate),
                'monthly_gain': round(monthly_gain, 2),
                'ending_amount': round(current_amount, 2)
            })
        
        self.monthly_growth = monthly_breakdown
        self.total_return = round(current_amount - float(self.initial_amount), 2)
        self.final_amount = round(current_amount, 2)
        
        return self.monthly_growth
    
    def save(self, *args, **kwargs):
        # Calculate end date based on period in months
        if not self.end_date:
            from datetime import datetime, timedelta
            # Calculate end date by adding months
            month = self.start_date.month + self.period_months
            year = self.start_date.year
            
            # Handle year overflow
            while month > 12:
                month -= 12
                year += 1
            
            # Create end date
            try:
                self.end_date = self.start_date.replace(year=year, month=month)
            except ValueError:
                # Handle day overflow (e.g., Jan 31 + 1 month)
                if month == 2:
                    # February - use last day of month
                    self.end_date = self.start_date.replace(year=year, month=month, day=28)
                else:
                    self.end_date = self.start_date.replace(year=year, month=month, day=1) - timedelta(days=1)
        
        # Calculate returns if not already calculated
        if not self.monthly_growth:
            self.calculate_returns()
        
        super().save(*args, **kwargs)


class Trade(models.Model):
    """Model for storing trades (Gold, USDT, etc.)"""
    
    TRADE_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    ASSET_CHOICES = [
        ('gold', 'Gold'),
        ('usdt', 'USDT'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
        ('stop_loss_hit', 'Stop Loss Hit'),
        ('take_profit_hit', 'Take Profit Hit'),
        ('expired', 'Expired'),
    ]
    
    TIMEFRAME_CHOICES = [
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('15m', '15 Minutes'),
        ('30m', '30 Minutes'),
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    
    # Trade details
    asset = models.CharField(max_length=10, choices=ASSET_CHOICES)
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Price information
    entry_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    exit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Quantity
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    
    # Risk management
    stop_loss = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Time-based expiry
    timeframe = models.CharField(max_length=10, choices=TIMEFRAME_CHOICES, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # P&L
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Trade'
        verbose_name_plural = 'Trades'
    
    def __str__(self):
        return f"{self.user.email} - {self.asset.upper()} {self.trade_type.upper()} @ {self.entry_price}"
    
    def calculate_pnl(self, current_price):
        """Calculate profit/loss based on current price"""
        if self.trade_type == 'buy':
            pnl = (current_price - self.entry_price) * self.quantity
        else:  # sell
            pnl = (self.entry_price - current_price) * self.quantity
        
        pnl_percentage = (pnl / (self.entry_price * self.quantity)) * 100 if self.entry_price else 0
        
        return pnl, pnl_percentage
    
    def check_expiry(self):
        """Check if trade has expired"""
        if self.expires_at and timezone.now() >= self.expires_at:
            return True
        return False


class TradeHistory(models.Model):
    """Model for storing closed trades history"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trade_history')
    
    # Trade details
    asset = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=10)
    
    # Prices
    entry_price = models.DecimalField(max_digits=12, decimal_places=2)
    exit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    
    # P&L
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2)
    profit_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Close reason
    close_reason = models.CharField(max_length=50)  # manual, stop_loss, take_profit, expired
    
    # Timestamps
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-closed_at']
        verbose_name = 'Trade History'
        verbose_name_plural = 'Trade Histories'
    
    def __str__(self):
        return f"{self.user.email} - {self.asset.upper()} {self.trade_type.upper()}"
