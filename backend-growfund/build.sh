#!/usr/bin/env bash
# Render Build Script - Runs on every deployment
# exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build completed successfully!"
echo "ℹ️  Database migrations will run automatically on startup"
