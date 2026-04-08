# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD python manage.py migrate --noinput && \
    python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@growfund.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')
if not User.objects.filter(is_staff=True).exists():
    User.objects.create_superuser(email=email, password=password, first_name='Admin', last_name='GrowFund', is_verified=True)
    print('Superuser created')
" && \
    python manage.py setup_platform_settings && \
    python manage.py setup_crypto_prices && \
    gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 growfund.wsgi:application
