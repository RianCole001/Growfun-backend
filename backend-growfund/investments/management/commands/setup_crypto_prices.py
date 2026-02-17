from django.core.management.base import BaseCommand
from investments.admin_models import AdminCryptoPrice
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup initial crypto prices for testing'

    def handle(self, *args, **options):
        # Get admin user
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            self.stdout.write(self.style.ERROR('❌ No admin user found. Please create an admin first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'✅ Using admin: {admin.email}'))
        
        # Create initial crypto prices
        cryptos = [
            {
                'coin': 'EXACOIN',
                'name': 'Exacoin',
                'buy_price': Decimal('62.00'),
                'sell_price': Decimal('59.50'),
                'change_24h': Decimal('3.33'),
                'change_7d': Decimal('12.80'),
                'change_30d': Decimal('89.50')
            },
            {
                'coin': 'BTC',
                'name': 'Bitcoin',
                'buy_price': Decimal('65000.00'),
                'sell_price': Decimal('63050.00'),
                'change_24h': Decimal('2.10'),
                'change_7d': Decimal('-1.50'),
                'change_30d': Decimal('8.70')
            },
            {
                'coin': 'ETH',
                'name': 'Ethereum',
                'buy_price': Decimal('3200.00'),
                'sell_price': Decimal('3104.00'),
                'change_24h': Decimal('1.80'),
                'change_7d': Decimal('3.20'),
                'change_30d': Decimal('15.40')
            },
            {
                'coin': 'USDT',
                'name': 'Tether',
                'buy_price': Decimal('1.00'),
                'sell_price': Decimal('0.97'),
                'change_24h': Decimal('0.00'),
                'change_7d': Decimal('0.00'),
                'change_30d': Decimal('0.00')
            }
        ]
        
        for crypto_data in cryptos:
            price, created = AdminCryptoPrice.objects.update_or_create(
                coin=crypto_data['coin'],
                defaults={
                    'name': crypto_data['name'],
                    'buy_price': crypto_data['buy_price'],
                    'sell_price': crypto_data['sell_price'],
                    'change_24h': crypto_data['change_24h'],
                    'change_7d': crypto_data['change_7d'],
                    'change_30d': crypto_data['change_30d'],
                    'is_active': True,
                    'updated_by': admin
                }
            )
            
            action = "Created" if created else "Updated"
            spread = price.buy_price - price.sell_price
            spread_pct = (spread / price.buy_price) * 100
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} {price.coin}: Buy ${price.buy_price} / Sell ${price.sell_price} (Spread: {spread_pct:.2f}%)"
                )
            )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Crypto prices setup complete!'))
        self.stdout.write(
            self.style.SUCCESS(
                f"Total active coins: {AdminCryptoPrice.objects.filter(is_active=True).count()}"
            )
        )
