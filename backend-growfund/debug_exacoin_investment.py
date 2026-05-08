#!/usr/bin/env python
"""Debug ExaCoin investment issue"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model
from investments.models import Trade
from investments.admin_models import AdminCryptoPrice
from transactions.models import Transaction

User = get_user_model()

print('=== DEBUGGING EXACOIN INVESTMENT ===')

# Check if ExaCoin price exists
try:
    exacoin = AdminCryptoPrice.objects.get(coin='EXACOIN')
    print(f'✓ ExaCoin price found:')
    print(f'  Buy Price: ${exacoin.buy_price}')
    print(f'  Sell Price: ${exacoin.sell_price}')
    print(f'  Active: {exacoin.is_active}')
except AdminCryptoPrice.DoesNotExist:
    print('✗ ExaCoin price not found - creating it...')
    from decimal import Decimal
    exacoin = AdminCryptoPrice.objects.create(
        coin='EXACOIN',
        name='ExaCoin',
        buy_price=Decimal('62.00'),
        sell_price=Decimal('59.50'),
        is_active=True
    )
    exacoin.save(skip_validation=True)
    print(f'✓ Created ExaCoin: Buy ${exacoin.buy_price}, Sell ${exacoin.sell_price}')

# Check all users with ExaCoin trades
print(f'\n=== EXACOIN TRADES ===')
exacoin_trades = Trade.objects.filter(asset='EXACOIN')
print(f'Total ExaCoin trades: {exacoin_trades.count()}')

for trade in exacoin_trades:
    print(f'  User: {trade.user.email}')
    print(f'  Quantity: {trade.quantity}')
    print(f'  Entry Price: ${trade.entry_price}')
    print(f'  Status: {trade.status}')
    print(f'  Created: {trade.created_at}')
    print('  ---')

# Check ExaCoin investment transactions
print(f'\n=== EXACOIN INVESTMENT TRANSACTIONS ===')
exacoin_txns = Transaction.objects.filter(
    description__icontains='EXACOIN'
).order_by('-created_at')

print(f'ExaCoin transactions: {exacoin_txns.count()}')
for txn in exacoin_txns:
    print(f'  User: {txn.user.email}')
    print(f'  Type: {txn.transaction_type}')
    print(f'  Amount: ${txn.amount}')
    print(f'  Description: {txn.description}')
    print(f'  Status: {txn.status}')
    print('  ---')

# Check specific user
try:
    user = User.objects.get(email='migwibrian316@gmail.com')
    print(f'\n=== USER: {user.email} ===')
    print(f'Balance: ${user.balance}')
    
    user_trades = Trade.objects.filter(user=user)
    print(f'Total trades: {user_trades.count()}')
    
    user_exacoin = Trade.objects.filter(user=user, asset='EXACOIN')
    print(f'ExaCoin trades: {user_exacoin.count()}')
    
    for trade in user_exacoin:
        amount = trade.entry_price * trade.quantity
        print(f'  ExaCoin: {trade.quantity} @ ${trade.entry_price} = ${amount:.2f} (Status: {trade.status})')
        
except User.DoesNotExist:
    print('User migwibrian316@gmail.com not found')

print('\n=== DEBUG COMPLETE ===')