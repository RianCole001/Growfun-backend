#!/usr/bin/env bash
# Render Start Script - Runs when the service starts
# This runs AFTER build, when database is accessible

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "⚙️ Setting up platform settings..."
python manage.py setup_platform_settings || true

echo "💰 Setting up crypto prices..."
python manage.py setup_crypto_prices || true

echo "🚀 Starting Gunicorn server..."
gunicorn growfund.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
