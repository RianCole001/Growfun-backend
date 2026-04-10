import random
import time
from decimal import Decimal
from .usdt_models import USDTDepositRequest


def generate_unique_amount(base_amount: float) -> Decimal:
    base = Decimal(str(base_amount))
    for _ in range(20):
        suffix = Decimal(str(random.randint(1, 99))) / Decimal('100')
        unique = base + suffix
        if not USDTDepositRequest.objects.filter(expected_amount=unique, status='pending').exists():
            return unique
    micro = Decimal(str(int(time.time() * 1000) % 100)) / Decimal('100')
    return base + micro
