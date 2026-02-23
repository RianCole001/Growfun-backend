from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class PlatformSettings(models.Model):
    """Platform-wide settings for GrowFund"""
    
    # General Settings
    platform_name = models.CharField(
        max_length=100, 
        default='GrowFund',
        help_text='Platform name displayed to users'
    )
    platform_email = models.EmailField(
        default='support@growfund.com',
        help_text='Support email address'
    )
    maintenance_mode = models.BooleanField(
        default=False,
        help_text='Enable to block non-admin access'
    )
    
    # Transaction Limits
    min_deposit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum deposit amount'
    )
    max_deposit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('100000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Maximum deposit amount'
    )
    min_withdrawal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('50.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum withdrawal amount'
    )
    max_withdrawal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('50000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Maximum withdrawal amount'
    )
    
    # Fees (Percentage)
    deposit_fee = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text='Deposit fee percentage (0-100)'
    )
    withdrawal_fee = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('2.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text='Withdrawal fee percentage (0-100)'
    )
    
    # Automation
    auto_approve_deposits = models.BooleanField(
        default=False,
        help_text='Auto-approve deposits within limit'
    )
    auto_approve_withdrawals = models.BooleanField(
        default=False,
        help_text='Auto-approve withdrawals within limit'
    )
    auto_approve_deposit_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('1000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Auto-approve deposits up to this amount'
    )
    auto_approve_withdrawal_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('500.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Auto-approve withdrawals up to this amount'
    )
    
    # Notifications
    email_notifications = models.BooleanField(
        default=True,
        help_text='Enable email notifications'
    )
    sms_notifications = models.BooleanField(
        default=False,
        help_text='Enable SMS notifications'
    )
    
    # Referral Program
    referral_bonus = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('50.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Bonus amount for successful referrals'
    )
    
    # Investment Limits
    min_capital_plan_investment = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('500.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum amount for capital plan investments'
    )
    min_real_estate_investment = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('1000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum amount for real estate investments'
    )
    min_crypto_investment = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('50.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum amount for crypto investments'
    )
    
    # Capital Plan Individual Minimums
    capital_basic_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum investment for Basic capital plan'
    )
    capital_standard_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('500.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum investment for Standard capital plan'
    )
    capital_advance_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('2000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum investment for Advance capital plan'
    )
    
    # Real Estate Individual Minimums
    real_estate_starter_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('1000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum investment for Starter Property'
    )
    real_estate_premium_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('5000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum investment for Premium Property'
    )
    real_estate_luxury_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('20000.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Minimum investment for Luxury Estate'
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='settings_updates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Platform Settings'
        verbose_name_plural = 'Platform Settings'
    
    def __str__(self):
        return f"{self.platform_name} Settings"
    
    def clean(self):
        """Validate settings"""
        from django.core.exceptions import ValidationError
        
        errors = {}
        
        # Validate deposit limits
        if self.min_deposit >= self.max_deposit:
            errors['min_deposit'] = 'Minimum deposit must be less than maximum deposit'
        
        # Validate withdrawal limits
        if self.min_withdrawal >= self.max_withdrawal:
            errors['min_withdrawal'] = 'Minimum withdrawal must be less than maximum withdrawal'
        
        # Validate auto-approve limits
        if self.auto_approve_deposit_limit > self.max_deposit:
            errors['auto_approve_deposit_limit'] = 'Auto-approve limit cannot exceed maximum deposit'
        
        if self.auto_approve_withdrawal_limit > self.max_withdrawal:
            errors['auto_approve_withdrawal_limit'] = 'Auto-approve limit cannot exceed maximum withdrawal'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Only run validation on updates, not initial creation
        if self.pk:
            self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create singleton settings instance"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings


class SettingsHistory(models.Model):
    """Track settings changes for audit trail"""
    
    setting_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Settings History'
        verbose_name_plural = 'Settings History'
    
    def __str__(self):
        return f"{self.setting_name} changed by {self.changed_by} at {self.changed_at}"
