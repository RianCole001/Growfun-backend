import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings

PLATFORM_WALLET = getattr(settings, 'USDT_WALLET_ADDRESS', 'TNGbuN1FPWJDsxd9wtoyoAqeRvCVuPuDXm')


class USDTDepositRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usdt_deposits')
    base_amount = models.DecimalField(max_digits=18, decimal_places=2)
    expected_amount = models.DecimalField(max_digits=18, decimal_places=6)
    wallet_address = models.CharField(max_length=100, default=PLATFORM_WALLET)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tx_hash = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.expected_amount} USDT - {self.status}"
