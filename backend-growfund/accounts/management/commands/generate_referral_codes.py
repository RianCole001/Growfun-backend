from django.core.management.base import BaseCommand
from accounts.models import User
import uuid


class Command(BaseCommand):
    help = 'Generate referral codes for users who don\'t have one'

    def handle(self, *args, **options):
        users_without_code = User.objects.filter(referral_code__isnull=True) | User.objects.filter(referral_code='')
        count = 0
        
        for user in users_without_code:
            # Generate unique referral code
            while True:
                code = str(uuid.uuid4())[:8].upper()
                if not User.objects.filter(referral_code=code).exists():
                    user.referral_code = code
                    user.save()
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Generated code for {user.email}: {code}')
                    )
                    break
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully generated {count} referral codes')
        )
