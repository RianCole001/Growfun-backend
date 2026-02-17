"""
Setup initial crypto prices for testing
Run with: python manage.py shell < setup_crypto_prices.py
"""
from investments.admin_models import AdminCryptoPrice
from django.contrib.auth import get_user_model

User = get_user_model()

# Get admin user
try:
    admin = User.objects.filter(is_staff=True).first()
    if not admin:
        print("❌ No admin user found. Please create an admin first.")
        exit()
    
    print(f"✅ Using admin: {admin.email}")
    
    # Create initial crypto prices
    cryptos = [
        {
            'coin': 'EXACOIN',
            'name': 'Exacoin',
            'buy_price': 62.00,
            'sell_price': 59.50,
            'change_24h': 3.33,
            'change_7d': 12.80,
            'change_30d': 89.50
        },
        {
            'coin': 'BTC',
            'name': 'Bitcoin',
            'buy_price': 65000.00,
            'sell_price': 63050.00,
            'change_24h': 2.10,
            'change_7d': -1.50,
            'change_30d': 8.70
        },
        {
            'coin': 'ETH',
            'name': 'Ethereum',
            'buy_price': 3200.00,
            'sell_price': 3104.00,
            'change_24h': 1.80,
            'change_7d': 3.20,
            'change_30d': 15.40
        },
        {
            'coin': 'USDT',
            'name': 'Tether',
            'buy_price': 1.00,
            'sell_price': 0.97,
            'change_24h': 0.00,
            'change_7d': 0.00,
            'change_30d': 0.00
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
        
        print(f"{action} {price.coin}: Buy ${price.buy_price} / Sell ${price.sell_price} (Spread: {spread_pct:.2f}%)")
    
    print("\n✅ Crypto prices setup complete!")
    print(f"Total active coins: {AdminCryptoPrice.objects.filter(is_active=True).count()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
