from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class DemoAccount(models.Model):
    """Demo account for users to practice trading"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='demo_account')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Demo Account - {self.user.email} (${self.balance})"

class DemoInvestment(models.Model):
    """Demo investments for practice"""
    INVESTMENT_TYPES = [
        ('crypto', 'Cryptocurrency'),
        ('capital_plan', 'Capital Plan'),
        ('real_estate', 'Real Estate'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    demo_account = models.ForeignKey(DemoAccount, on_delete=models.CASCADE, related_name='investments')
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES)
    asset_name = models.CharField(max_length=100)  # e.g., 'EXACOIN', 'Premium Property'
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)  # For crypto
    price_at_purchase = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    monthly_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # For plans
    duration_months = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Demo {self.investment_type}: {self.asset_name} - ${self.amount}"

class DemoTransaction(models.Model):
    """Demo transaction history"""
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('crypto_buy', 'Crypto Purchase'),
        ('crypto_sell', 'Crypto Sale'),
        ('investment', 'Investment'),
        ('return', 'Investment Return'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    
    demo_account = models.ForeignKey(DemoAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    asset = models.CharField(max_length=100, null=True, blank=True)  # e.g., 'EXACOIN', 'BTC'
    quantity = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Demo {self.transaction_type}: ${self.amount} - {self.demo_account.user.email}"