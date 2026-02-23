from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification, AdminNotification

User = get_user_model()


class Command(BaseCommand):
    help = 'Test notification system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test',
            action='store_true',
            help='Create test notifications',
        )
        parser.add_argument(
            '--check-status',
            action='store_true',
            help='Check notification system status',
        )

    def handle(self, *args, **options):
        if options['create_test']:
            self.create_test_notifications()
        
        if options['check_status']:
            self.check_status()

    def create_test_notifications(self):
        """Create test notifications for all active users"""
        self.stdout.write('Creating test notifications...')
        
        # Get admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found'))
            return
        
        # Get active users
        users = User.objects.filter(is_active=True)
        user_count = users.count()
        
        self.stdout.write(f'Found {user_count} active users')
        
        # Create admin notification record
        admin_notification = AdminNotification.objects.create(
            title='Test Notification from Management Command',
            message='This is a test notification created by the management command to verify the notification system is working properly.',
            type='info',
            priority='normal',
            target='all',
            created_by=admin_user,
            status='sent',
            sent_count=user_count
        )
        
        # Create individual notifications for each user
        notifications_created = 0
        for user in users:
            notification = Notification.create_notification(
                user=user,
                title='Test Notification from Management Command',
                message='This is a test notification created by the management command to verify the notification system is working properly.',
                notification_type='info'
            )
            notifications_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {notifications_created} notifications for {user_count} users'
            )
        )
        self.stdout.write(f'Admin notification ID: {admin_notification.id}')

    def check_status(self):
        """Check notification system status"""
        self.stdout.write('Checking notification system status...')
        
        # Check users
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_users = User.objects.filter(is_staff=True).count()
        
        self.stdout.write(f'Total users: {total_users}')
        self.stdout.write(f'Active users: {active_users}')
        self.stdout.write(f'Admin users: {admin_users}')
        
        # Check notifications
        total_notifications = Notification.objects.count()
        unread_notifications = Notification.objects.filter(read=False).count()
        
        self.stdout.write(f'Total user notifications: {total_notifications}')
        self.stdout.write(f'Unread notifications: {unread_notifications}')
        
        # Check admin notifications
        admin_notifications = AdminNotification.objects.count()
        self.stdout.write(f'Admin notifications sent: {admin_notifications}')
        
        # Recent notifications
        recent_notifications = Notification.objects.order_by('-created_at')[:5]
        self.stdout.write('\nRecent notifications:')
        for notif in recent_notifications:
            self.stdout.write(f'  - {notif.user.email}: {notif.title} ({notif.created_at})')
        
        # Recent admin notifications
        recent_admin_notifications = AdminNotification.objects.order_by('-created_at')[:3]
        self.stdout.write('\nRecent admin notifications:')
        for admin_notif in recent_admin_notifications:
            self.stdout.write(f'  - {admin_notif.title} (sent to {admin_notif.sent_count} users)')