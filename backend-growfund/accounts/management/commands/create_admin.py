from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin superusers if they do not exist'

    def handle(self, *args, **options):
        admins = [
            {
                'email': 'admin@growfund.com',
                'password': 'Admin123!',
                'first_name': 'Admin',
                'last_name': 'User'
            },
            {
                'email': 'admin001@gmail.com',
                'password': 'Buffers316!',
                'first_name': 'Admin',
                'last_name': 'One'
            }
        ]
        
        for admin_data in admins:
            email = admin_data['email']
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    email=email,
                    password=admin_data['password'],
                    first_name=admin_data['first_name'],
                    last_name=admin_data['last_name']
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Superuser created: {email}'))
                self.stdout.write(f'  Password: {admin_data["password"]}')
            else:
                user = User.objects.get(email=email)
                # Ensure user is staff and superuser
                if not user.is_staff or not user.is_superuser:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Admin user updated: {email}'))
                else:
                    self.stdout.write(f'✓ Admin user already exists: {email}')
