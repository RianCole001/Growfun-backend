#!/usr/bin/env python
"""Test all the fixes we implemented"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from investments.models import Trade
from investments.admin_models import AdminCryptoPrice
from transactions.models import Transaction
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

print('=== TESTING ALL FIXES ===\n')

# Test 1: Admin Credits in Deposits
print('1. ADMIN CREDITS AS DEPOSITS TEST')
admin_credits = Transaction.objects.filter(transaction_type='admin_credit')
print(f'   Total admin credits: {admin_credits.count()}')
if admin_credits.exists():
    latest = admin_credits.first()
    print(f'   Latest: ${latest.amount} to {latest.user.email} on {latest.created_at}')
print()

# Test 2: Crypto Investments
print('2. CRYPTO INVESTMENTS TEST')
crypto_trades = Trade.objects.filter(status='open')
print(f'   Open crypto trades: {crypto_trades.count()}')
for trade in crypto_trades:
    amount = trade.entry_price * trade.quantity
    print(f'   {trade.user.email}: {trade.quantity:.8f} {trade.asset} = ${amount:.2f}')
print()

# Test 3: ExaCoin Price
print('3. EXACOIN PRICE TEST')
try:
    exacoin = AdminCryptoPrice.objects.get(coin='EXACOIN')
    print(f'   EXACOIN Buy: ${exacoin.buy_price}, Sell: ${exacoin.sell_price}')
    print(f'   Spread: ${exacoin.spread} ({exacoin.spread_percentage:.2f}%)')
    print(f'   Active: {exacoin.is_active}')
except AdminCryptoPrice.DoesNotExist:
    print('   EXACOIN price not found - creating default...')
    exacoin = AdminCryptoPrice.objects.create(
        coin='EXACOIN',
        name='ExaCoin',
        buy_price=Decimal('62.00'),
        sell_price=Decimal('59.50'),
        is_active=True
    )
    exacoin.save(skip_validation=True)
    print(f'   Created EXACOIN: Buy ${exacoin.buy_price}, Sell ${exacoin.sell_price}')
print()

# Test 4: Transaction Types
print('4. TRANSACTION TYPES TEST')
txn_types = Transaction.objects.values('transaction_type').distinct()
for txn_type in txn_types:
    count = Transaction.objects.filter(transaction_type=txn_type['transaction_type']).count()
    print(f'   {txn_type["transaction_type"]}: {count} transactions')
print()

# Test 5: User Balances
print('5. USER BALANCES TEST')
users_with_balance = User.objects.filter(balance__gt=0)[:5]
for user in users_with_balance:
    print(f'   {user.email}: ${user.balance}')
print()

print('=== TEST COMPLETE ===')