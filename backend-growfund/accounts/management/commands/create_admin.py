from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a secure admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email address')
        parser.add_argument('--first-name', type=str, help='Admin first name')
        parser.add_argument('--last-name', type=str, help='Admin last name')

    def handle(self, *args, **options):
        email = options.get('email')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        
        if not email:
            email = input('Enter admin email: ')
        
        if not first_name:
            first_name = input('Enter admin first name (optional, press Enter to skip): ') or 'Admin'
        
        if not last_name:
            last_name = input('Enter admin last name (optional, press Enter to skip): ') or 'User'
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists')
            )
            return
        
        # Get password securely
        password = getpass.getpass('Enter admin password: ')
        password_confirm = getpass.getpass('Confirm admin password: ')
        
        if password != password_confirm:
            self.stdout.write(
                self.style.ERROR('Passwords do not match')
            )
            return
        
        if len(password) < 8:
            self.stdout.write(
                self.style.ERROR('Password must be at least 8 characters long')
            )
            return
        
        try:
            with transaction.atomic():
                # Create admin user (no username field needed)
                admin_user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=True,
                    is_verified=True
                )
                
                # Create or get Admin group
                admin_group, created = Group.objects.get_or_create(name='Admin')
                admin_user.groups.add(admin_group)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created admin user: {email}'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Name: {first_name} {last_name}'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Staff: {admin_user.is_staff}, Superuser: {admin_user.is_superuser}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )