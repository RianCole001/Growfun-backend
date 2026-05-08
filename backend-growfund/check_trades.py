#!/usr/bin/env python
"""Check trades in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from investments.models import Trade
from django.contrib.auth import get_user_model
from transactions.models import Transaction

User = get_user_model()

print('=== TRADE MODEL CHECK ===')
print(f'Total trades in database: {Trade.objects.count()}')
print(f'Open trades: {Trade.objects.filter(status="open").count()}')
print(f'Closed trades: {Trade.objects.filter(status="closed").count()}')

print('\n=== RECENT TRADES ===')
recent_trades = Trade.objects.all().order_by('-created_at')[:5]
for trade in recent_trades:
    amount = trade.entry_price * trade.quantity if trade.entry_price and trade.quantity else 0
    print(f'ID: {trade.id}, User: {trade.user.email}, Asset: {trade.asset}, Status: {trade.status}, Amount: ${amount:.2f}')

print('\n=== USERS WITH TRADES ===')
users_with_trades = User.objects.filter(trade_set__isnull=False).distinct()
for user in users_with_trades:
    trade_count = user.trade_set.count()
    open_count = user.trade_set.filter(status='open').count()
    print(f'{user.email}: {trade_count} total trades, {open_count} open')

print('\n=== INVESTMENT TRANSACTIONS ===')
investment_txns = Transaction.objects.filter(transaction_type='investment').order_by('-created_at')[:5]
for txn in investment_txns:
    print(f'User: {txn.user.email}, Amount: ${txn.amount}, Status: {txn.status}, Date: {txn.created_at}')

print('\n=== ADMIN CREDIT TRANSACTIONS ===')
admin_credits = Transaction.objects.filter(transaction_type='admin_credit').order_by('-created_at')[:5]
for txn in admin_credits:
    print(f'User: {txn.user.email}, Amount: ${txn.amount}, Status: {txn.status}, Date: {txn.created_at}')