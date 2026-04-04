#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superuser if none exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
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
    print('Superuser already exists, skipping.')
"

echo "⚙️ Setting up platform settings..."
python manage.py setup_platform_settings || echo "⚠️ Platform settings setup skipped"

echo "💰 Setting up crypto prices..."
python manage.py setup_crypto_prices || echo "⚠️ Crypto prices setup skipped"

echo "✅ Build complete!"
