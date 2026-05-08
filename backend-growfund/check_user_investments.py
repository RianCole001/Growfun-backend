#!/usr/bin/env python
"""Check specific user investments"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from investments.models import Trade
from transactions.models import Transaction

User = get_user_model()

try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    print(f'=== USER: {user.email} ===')
    print(f'Balance: ${user.balance}')
    print(f'Total trades: {user.trade_set.count()}')
    print(f'Open trades: {user.trade_set.filter(status="open").count()}')
    print(f'Investment transactions: {user.transactions.filter(transaction_type="investment").count()}')

    print('\n=== TRADES ===')
    for trade in user.trade_set.all():
        amount = trade.entry_price * trade.quantity if trade.entry_price and trade.quantity else 0
        print(f'  ID: {trade.id}')
        print(f'  Asset: {trade.asset}')
        print(f'  Quantity: {trade.quantity}')
        print(f'  Entry Price: ${trade.entry_price}')
        print(f'  Amount: ${amount:.2f}')
        print(f'  Status: {trade.status}')
        print(f'  Created: {trade.created_at}')
        print('  ---')

    print('\n=== INVESTMENT TRANSACTIONS ===')
    for txn in user.transactions.filter(transaction_type='investment'):
        print(f'  Amount: ${txn.amount}')
        print(f'  Description: {txn.description}')
        print(f'  Status: {txn.status}')
        print(f'  Reference: {txn.reference}')
        print(f'  Created: {txn.created_at}')
        print('  ---')

    print('\n=== ALL TRANSACTIONS ===')
    for txn in user.transactions.all()[:5]:
        print(f'  Type: {txn.transaction_type}')
        print(f'  Amount: ${txn.amount}')
        print(f'  Status: {txn.status}')
        print(f'  Created: {txn.created_at}')
        print('  ---')

except User.DoesNotExist:
    print('User not found')
except Exception as e:
    print(f'Error: {e}')