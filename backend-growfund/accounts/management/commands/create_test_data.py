"""
Management command to create fresh test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from transactions.models import Transaction
from investments.models import Trade, CapitalInvestmentPlan
from notifications.models import Notification
import uuid
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create fresh test data for the platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🎨 Creating fresh test data...\n'))

        # Get or create test users
        users = []
        test_users_data = [
            {
                'email': 'user1@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'testpass123'
            },
            {
                'email': 'user2@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'testpass123'
            },
            {
                'email': 'user3@example.com',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'password': 'testpass123'
            },
        ]

        for user_data in test_users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_verified': True,
                    'balance': Decimal('0.00')
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Created user: {user.email}'))
            else:
                self.stdout.write(f'ℹ️  User already exists: {user.email}')
            users.append(user)

        # Create deposits for users
        self.stdout.write('\n💰 Creating deposits...')
        deposits_created = 0
        for i, user in enumerate(users):
            amounts = [1000, 500, 2000]
            amount = Decimal(str(amounts[i]))
            
            # Use mobile money payment methods instead of admin credits
            payment_methods = ['mpesa', 'mtn_momo', 'airtel_money']
            payment_method = payment_methods[i % 3]
            
            # Create deposit transaction with mobile money
            deposit = Transaction.objects.create(
                user=user,
                transaction_type='deposit',
                amount=amount,
                payment_method=payment_method,
                status='completed',
                reference=f'{payment_method.upper()}-{user.id}-{amount}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                created_at=timezone.now() - timedelta(days=10)
            )
            
            # Update user balance
            user.balance += amount
            user.save()
            
            deposits_created += 1
            self.stdout.write(f'  ✅ Created {payment_method} deposit of ${amount} for {user.email}')

        self.stdout.write(self.style.SUCCESS(f'✅ Created {deposits_created} deposit transactions'))

        # Create capital investment plans
        self.stdout.write('\n📈 Creating capital investment plans...')
        plans_created = 0
        plan_types = ['basic', 'standard', 'advance']
        plan_amounts = [500, 1000, 1500]
        
        for i, user in enumerate(users):
            plan_type = plan_types[i % 3]
            amount = Decimal(str(plan_amounts[i % 3]))
            
            # Deduct from balance
            if user.balance >= amount:
                plan = CapitalInvestmentPlan.objects.create(
                    user=user,
                    plan_type=plan_type,
                    initial_amount=amount,
                    period_months=6,
                    growth_rate=Decimal('20.0') if plan_type == 'basic' else Decimal('30.0') if plan_type == 'standard' else Decimal('40.0'),
                    status='active',
                    start_date=timezone.now() - timedelta(days=5)
                )
                
                # Create investment transaction
                Transaction.objects.create(
                    user=user,
                    transaction_type='investment',
                    amount=amount,
                    status='completed',
                    reference=f'CAPITAL-PLAN-{plan.id}',
                    created_at=timezone.now() - timedelta(days=5)
                )
                
                # Update user balance
                user.balance -= amount
                user.save()
                
                plans_created += 1
                self.stdout.write(f'  ✅ Created {plan_type} plan of ${amount} for {user.email}')

        self.stdout.write(self.style.SUCCESS(f'✅ Created {plans_created} capital investment plans'))

        # Create crypto trades
        self.stdout.write('\n💎 Creating crypto trades...')
        trades_created = 0
        crypto_assets = ['gold', 'usdt']
        crypto_prices = [2000, 1]
        
        for i, user in enumerate(users[:2]):  # Only first 2 users
            asset = crypto_assets[i % 2]
            price = Decimal(str(crypto_prices[i % 2]))
            quantity = Decimal('0.1') if asset == 'gold' else Decimal('100')
            amount = price * quantity
            
            # Reload user to get updated balance
            user.refresh_from_db()
            
            if user.balance >= amount:
                trade = Trade.objects.create(
                    user=user,
                    asset=asset,
                    trade_type='buy',
                    quantity=quantity,
                    entry_price=price,
                    current_price=price * Decimal('1.05'),  # 5% profit
                    status='open',
                    created_at=timezone.now() - timedelta(days=3)
                )
                
                # Create investment transaction
                Transaction.objects.create(
                    user=user,
                    transaction_type='investment',
                    amount=amount,
                    status='completed',
                    reference=f'CRYPTO-BUY-{trade.id}',
                    metadata={'asset': asset, 'quantity': str(quantity), 'price_at_purchase': str(price)},
                    created_at=timezone.now() - timedelta(days=3)
                )
                
                # Update user balance
                user.balance -= amount
                user.save()
                
                trades_created += 1
                self.stdout.write(f'  ✅ Created {asset} trade of {quantity} @ ${price} for {user.email}')
                self.stdout.write(f'  ✅ Created {asset} trade of {quantity} @ ${price} for {user.email}')

        self.stdout.write(self.style.SUCCESS(f'✅ Created {trades_created} crypto trades'))

        # Create some withdrawals
        self.stdout.write('\n💸 Creating withdrawals...')
        withdrawals_created = 0
        for user in users[:1]:  # Only first user
            if user.balance >= 100:
                withdrawal = Transaction.objects.create(
                    user=user,
                    transaction_type='withdrawal',
                    amount=Decimal('100.00'),
                    payment_method='bank_transfer',
                    status='pending',
                    reference=f'WITHDRAWAL-{user.id}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    created_at=timezone.now() - timedelta(days=1)
                )
                withdrawals_created += 1
                self.stdout.write(f'  ✅ Created withdrawal of $100 for {user.email}')

        self.stdout.write(self.style.SUCCESS(f'✅ Created {withdrawals_created} withdrawal requests'))

        # Create notifications
        self.stdout.write('\n🔔 Creating notifications...')
        notifications_created = 0
        for user in users:
            # Welcome notification
            Notification.objects.create(
                user=user,
                title='Welcome to GrowFund!',
                message='Thank you for joining GrowFund. Start investing today!',
                type='info',
                read=False,
                created_at=timezone.now() - timedelta(days=10)
            )
            
            # Deposit notification
            Notification.objects.create(
                user=user,
                title='Deposit Successful',
                message=f'Your deposit has been credited to your account.',
                type='success',
                read=True,
                created_at=timezone.now() - timedelta(days=9)
            )
            
            notifications_created += 2

        self.stdout.write(self.style.SUCCESS(f'✅ Created {notifications_created} notifications'))

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ Test data creation complete!\n'
                f'\n📊 Summary:'
                f'\n  - Users: {len(users)}'
                f'\n  - Deposits: {deposits_created}'
                f'\n  - Capital Plans: {plans_created}'
                f'\n  - Crypto Trades: {trades_created}'
                f'\n  - Withdrawals: {withdrawals_created}'
                f'\n  - Notifications: {notifications_created}'
                f'\n\n🔑 Test User Credentials:'
                f'\n  Email: user1@example.com | Password: testpass123'
                f'\n  Email: user2@example.com | Password: testpass123'
                f'\n  Email: user3@example.com | Password: testpass123'
                f'\n'
            )
        )
