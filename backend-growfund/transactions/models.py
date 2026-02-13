from django.db import models
from django.conf import settings
from decimal import Decimal

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
        ('profit', 'Profit'),
        ('referral_bonus', 'Referral Bonus'),
    )
    
    PAYMENT_METHODS = (
        ('momo', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['reference']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.net_amount:
            self.net_amount = self.amount - self.fee
        super().save(*args, **kwargs)


class MoMoPayment(models.Model):
    """MTN Mobile Money specific payment details"""
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='momo_payment')
    phone_number = models.CharField(max_length=20)
    network = models.CharField(max_length=50, default='MTN')
    momo_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    momo_reference = models.CharField(max_length=100, null=True, blank=True)
    callback_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MoMo - {self.phone_number} - {self.transaction.amount}"
