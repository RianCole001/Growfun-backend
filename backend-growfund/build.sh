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

echo "💰 Setting up crypto prices..."
python manage.py setup_crypto_prices || echo "⚠️ Crypto prices already exist or setup skipped"

echo "✅ Build complete!"
