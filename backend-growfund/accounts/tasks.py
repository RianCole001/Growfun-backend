from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


# Simple email functions (no Celery for now)
def send_verification_email(user_id):
    """Send email verification link"""
    try:
        user = User.objects.get(id=user_id)
        verification_url = f"{settings.FRONTEND_URL}/verify?token={user.verification_token}"
        
        subject = f'Verify your {settings.PLATFORM_NAME} account'
        message = f"""
        Hello {user.get_full_name()},
        
        Thank you for registering with {settings.PLATFORM_NAME}!
        
        Please click the link below to verify your email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        The {settings.PLATFORM_NAME} Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Verification email sent to {user.email}"
    
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


def send_password_reset_email(user_id):
    """Send password reset link"""
    try:
        user = User.objects.get(id=user_id)
        reset_url = f"{settings.FRONTEND_URL}/reset?token={user.reset_token}"
        
        subject = f'Reset your {settings.PLATFORM_NAME} password'
        message = f"""
        Hello {user.get_full_name()},
        
        We received a request to reset your password for your {settings.PLATFORM_NAME} account.
        
        Please click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        The {settings.PLATFORM_NAME} Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Password reset email sent to {user.email}"
    
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


def send_welcome_email(user_id):
    """Send welcome email after verification"""
    try:
        user = User.objects.get(id=user_id)
        
        subject = f'Welcome to {settings.PLATFORM_NAME}!'
        message = f"""
        Hello {user.get_full_name()},
        
        Welcome to {settings.PLATFORM_NAME}! Your account has been successfully verified.
        
        You can now:
        - Invest in cryptocurrencies
        - Explore real estate opportunities
        - Join capital appreciation plans
        - Refer friends and earn bonuses
        
        Your referral code: {user.referral_code}
        
        Get started: {settings.FRONTEND_URL}/app
        
        Best regards,
        The {settings.PLATFORM_NAME} Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Welcome email sent to {user.email}"
    
    except User.DoesNotExist:
        return f"User with id {user_id} not found"
