from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class AdminCryptoPrice(models.Model):
    """Admin-controlled cryptocurrency prices with buy/sell spread"""
    
    coin = models.CharField(max_length=10, unique=True, help_text="Coin symbol (e.g., EXACOIN, BTC)")
    name = models.CharField(max_length=50, default="", help_text="Full coin name")
    
    # Pricing
    buy_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price users pay to buy"
    )
    sell_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price users receive when selling"
    )
    
    # Market data
    change_24h = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=0,
        help_text="24-hour price change percentage"
    )
    change_7d = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=0,
        help_text="7-day price change percentage"
    )
    change_30d = models.DecimalField(
        max_digits=8, 
        decimal_places=4, 
        default=0,
        help_text="30-day price change percentage"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True, help_text="Enable/disable trading for this coin")
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='price_updates')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['coin']
        verbose_name = 'Admin Crypto Price'
        verbose_name_plural = 'Admin Crypto Prices'
        indexes = [
            models.Index(fields=['coin']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.coin} - Buy: ${self.buy_price} / Sell: ${self.sell_price}"
    
    @property
    def spread(self):
        """Calculate the spread between buy and sell prices"""
        return self.buy_price - self.sell_price
    
    @property
    def spread_percentage(self):
        """Calculate spread as percentage of buy price"""
        if self.buy_price > 0:
            return (self.spread / self.buy_price) * 100
        return 0
    
    def clean(self):
        """Validate that sell price is less than buy price"""
        from django.core.exceptions import ValidationError
        if self.sell_price >= self.buy_price:
            raise ValidationError({
                'sell_price': 'Sell price must be less than buy price to maintain spread.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CryptoPriceHistory(models.Model):
    """Track price changes for audit trail"""
    
    coin = models.CharField(max_length=10, db_index=True)
    buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    change_24h = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Crypto Price History'
        verbose_name_plural = 'Crypto Price History'
        indexes = [
            models.Index(fields=['coin', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.coin} - ${self.buy_price} at {self.created_at}"