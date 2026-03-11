"""
Demo Mode Utilities
Centralized functions for handling demo vs real mode across all trading components
"""
from decimal import Decimal
from .models import DemoAccount


def get_balance(user, is_demo=False):
    """Get user balance based on mode"""
    if is_demo:
        demo_account, _ = DemoAccount.objects.get_or_create(
            user=user,
            defaults={'balance': Decimal('10000.00')}
        )
        return demo_account.balance
    return user.balance


def update_balance(user, amount, is_demo=False):
    """
    Update user balance based on mode
    amount: positive to add, negative to subtract
    """
    if is_demo:
        demo_account, _ = DemoAccount.objects.get_or_create(
            user=user,
            defaults={'balance': Decimal('10000.00')}
        )
        demo_account.balance += Decimal(str(amount))
        demo_account.save(update_fields=['balance'])
        return demo_account.balance
    else:
        user.balance += Decimal(str(amount))
        user.save(update_fields=['balance'])
        return user.balance


def check_balance(user, required_amount, is_demo=False):
    """
    Check if user has sufficient balance
    Returns: (has_balance: bool, current_balance: Decimal)
    """
    balance = get_balance(user, is_demo)
    return balance >= Decimal(str(required_amount)), balance


def get_balance_info(user):
    """
    Get both real and demo balances
    Returns: dict with real_balance and demo_balance
    """
    demo_account, _ = DemoAccount.objects.get_or_create(
        user=user,
        defaults={'balance': Decimal('10000.00')}
    )
    
    return {
        'real_balance': float(user.balance),
        'demo_balance': float(demo_account.balance)
    }
