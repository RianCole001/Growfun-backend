#!/usr/bin/env python
"""Verify user data in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from investments.models import Trade, CapitalInvestmentPlan
from transactions.models import Transaction

User = get_user_model()

print('=== VERIFYING USER DATA ===')

try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    print(f'✓ Found user: {user.email}')
    print(f'  Balance: ${user.balance}')
    print(f'  Verified: {user.is_verified}')
    print(f'  Staff: {user.is_staff}')
    
    # Check trades
    trades = Trade.objects.filter(user=user)
    print(f'\n=== TRADES ===')
    print(f'Total trades: {trades.count()}')
    for trade in trades:
        print(f'  {trade.asset}: {trade.quantity} @ ${trade.entry_price} (Status: {trade.status})')
    
    # Check capital plans
    plans = CapitalInvestmentPlan.objects.filter(user=user)
    print(f'\n=== CAPITAL PLANS ===')
    print(f'Total plans: {plans.count()}')
    for plan in plans:
        print(f'  {plan.plan_type}: ${plan.initial_amount} (Status: {plan.status})')
    
    # Check transactions
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:10]
    print(f'\n=== RECENT TRANSACTIONS ===')
    print(f'Total transactions: {Transaction.objects.filter(user=user).count()}')
    for txn in transactions:
        print(f'  {txn.transaction_type}: ${txn.amount} - {txn.description[:50]}... ({txn.status})')
    
    # Check investment transactions specifically
    investment_txns = Transaction.objects.filter(user=user, transaction_type='investment')
    print(f'\n=== INVESTMENT TRANSACTIONS ===')
    print(f'Investment transactions: {investment_txns.count()}')
    for txn in investment_txns:
        print(f'  ${txn.amount} - {txn.description} (Ref: {txn.reference})')
    
except User.DoesNotExist:
    print('✗ User not found')
    
    # List all users
    print('\n=== ALL USERS ===')
    for user in User.objects.all()[:10]:
        print(f'  {user.email} (Balance: ${user.balance})')

print('\n=== VERIFICATION COMPLETE ===')