from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """User notifications model"""
    
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type='info'):
        """Helper method to create notifications"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type
        )


class AdminNotification(models.Model):
    """Admin-created notifications tracking"""
    
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]
    
    TARGET_CHOICES = [
        ('all', 'All Users'),
        ('verified_users', 'Verified Users'),
        ('specific_users', 'Specific Users'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    target_users = models.TextField(blank=True, help_text="Comma-separated emails for specific_users target")
    sent_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.target} ({self.sent_count} users)"

