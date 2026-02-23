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
        parser.add_argument('--username', type=str, help='Admin username')

    def handle(self, *args, **options):
        email = options.get('email')
        username = options.get('username')
        
        if not email:
            email = input('Enter admin email: ')
        
        if not username:
            username = input('Enter admin username: ')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists')
            )
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User with username {username} already exists')
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
                # Create admin user
                admin_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=True,
                    is_superuser=True,
                    first_name='Admin',
                    last_name='User'
                )
                
                # Create or get Admin group
                admin_group, created = Group.objects.get_or_create(name='Admin')
                admin_user.groups.add(admin_group)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created admin user: {username} ({email})'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )