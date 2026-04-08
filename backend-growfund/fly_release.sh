#!/usr/bin/env bash
set -e

echo "🗄️ Running migrations..."
python manage.py migrate --noinput

echo "👤 Creating superuser if none exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@growfund.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')
if not User.objects.filter(is_staff=True).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name='Admin',
        last_name='GrowFund',
        is_verified=True,
    )
    print(f'Superuser created: {email}')
else:
    print('Superuser already exists.')
"

echo "⚙️ Setting up platform settings..."
python manage.py setup_platform_settings || true

echo "💰 Setting up crypto prices..."
python manage.py setup_crypto_prices || true

echo "✅ Release complete!"
