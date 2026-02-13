from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model"""
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.FileField(upload_to='avatars/', blank=True, null=True)  # Changed from ImageField
    
    # Profile fields
    location = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Verification
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    reset_token = models.UUIDField(null=True, blank=True)
    reset_token_created = models.DateTimeField(null=True, blank=True)
    
    # Referral
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def save(self, *args, **kwargs):
        # Generate referral code if not exists
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class Referral(models.Model):
    """Model for tracking referrals"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_from')
    
    # Reward
    reward_amount = models.DecimalField(max_digits=12, decimal_places=2, default=5.00)
    reward_claimed = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = ('referrer', 'referred_user')
    
    def __str__(self):
        return f"{self.referrer.email} referred {self.referred_user.email}"
    
    def claim_reward(self):
        """Claim the referral reward"""
        if not self.reward_claimed:
            self.referrer.balance += self.reward_amount
            self.referrer.save()
            self.reward_claimed = True
            self.status = 'active'
            self.save()
            return True
        return False


class UserSettings(models.Model):
    """User settings and preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # General
    theme = models.CharField(max_length=10, choices=[('dark', 'Dark'), ('light', 'Light')], default='dark')
    currency = models.CharField(max_length=3, default='USD')
    language = models.CharField(max_length=5, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    price_alerts = models.BooleanField(default=True)
    transaction_alerts = models.BooleanField(default=True)
    referral_alerts = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    login_alerts = models.BooleanField(default=True)
    session_timeout = models.IntegerField(default=30)  # minutes
    
    # Privacy
    profile_visible = models.BooleanField(default=True)
    portfolio_visible = models.BooleanField(default=False)
    activity_sharing = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')
    
    def __str__(self):
        return f"Settings for {self.user.email}"
