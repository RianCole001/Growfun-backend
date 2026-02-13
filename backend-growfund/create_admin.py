import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growfund.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email='admin@growfund.com').exists():
    User.objects.create_superuser(
        email='admin@growfund.com',
        password='Admin123!',
        first_name='Admin',
        last_name='User'
    )
    print("✓ Superuser created successfully!")
    print("Email: admin@growfund.com")
    print("Password: Admin123!")
else:
    print("Superuser already exists!")
