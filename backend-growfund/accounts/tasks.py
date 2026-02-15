from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

User = get_user_model()


def send_verification_email(user_id):
    """Send email verification link"""
    try:
        user = User.objects.get(id=user_id)
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.verification_token}"
        
        subject = f'Verify your {settings.PLATFORM_NAME} account'
        
        # Plain text version
        text_content = f"""
Hello {user.get_full_name()},

Thank you for registering with {settings.PLATFORM_NAME}!

Please click the link below to verify your email address:
{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The {settings.PLATFORM_NAME} Team
        """
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{settings.PLATFORM_NAME}</h1>
            <p>Welcome aboard! 🎉</p>
        </div>
        <div class="content">
            <h2>Hello {user.get_full_name()},</h2>
            <p>Thank you for registering with {settings.PLATFORM_NAME}!</p>
            <p>Please verify your email address to activate your account and start investing.</p>
            <center>
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </center>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you didn't create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 {settings.PLATFORM_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Send email with both text and HTML versions
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return f"Verification email sent to {user.email}"
    
    except User.DoesNotExist:
        return f"User with id {user_id} not found"
    except Exception as e:
        print(f"Error sending verification email: {e}")
        raise


def send_password_reset_email(user_id):
    """Send password reset link"""
    try:
        user = User.objects.get(id=user_id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={user.reset_token}"
        
        subject = f'Reset your {settings.PLATFORM_NAME} password'
        
        # Plain text version
        text_content = f"""
Hello {user.get_full_name()},

We received a request to reset your password for your {settings.PLATFORM_NAME} account.

Please click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request a password reset, please ignore this email.

Best regards,
The {settings.PLATFORM_NAME} Team
        """
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{settings.PLATFORM_NAME}</h1>
            <p>Password Reset Request 🔐</p>
        </div>
        <div class="content">
            <h2>Hello {user.get_full_name()},</h2>
            <p>We received a request to reset your password for your {settings.PLATFORM_NAME} account.</p>
            <center>
                <a href="{reset_url}" class="button">Reset Password</a>
            </center>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
            <div class="warning">
                <strong>⚠️ Security Notice:</strong> This link will expire in 24 hours.
            </div>
            <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
        </div>
        <div class="footer">
            <p>© 2024 {settings.PLATFORM_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return f"Password reset email sent to {user.email}"
    
    except User.DoesNotExist:
        return f"User with id {user_id} not found"
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        raise


def send_welcome_email(user_id):
    """Send welcome email after verification"""
    try:
        user = User.objects.get(id=user_id)
        
        subject = f'Welcome to {settings.PLATFORM_NAME}! 🎉'
        
        # Plain text version
        text_content = f"""
Hello {user.get_full_name()},

Welcome to {settings.PLATFORM_NAME}! Your account has been successfully verified.

You can now:
- Invest in cryptocurrencies
- Explore real estate opportunities
- Join capital appreciation plans
- Refer friends and earn bonuses

Your referral code: {user.referral_code}
Share it with friends and earn rewards!

Get started: {settings.FRONTEND_URL}/login

Best regards,
The {settings.PLATFORM_NAME} Team
        """
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .features {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .feature {{ margin: 15px 0; padding-left: 30px; position: relative; }}
        .feature:before {{ content: "✓"; position: absolute; left: 0; color: #667eea; font-weight: bold; font-size: 20px; }}
        .referral-box {{ background: #e8f5e9; border: 2px dashed #4caf50; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0; }}
        .referral-code {{ font-size: 24px; font-weight: bold; color: #4caf50; letter-spacing: 2px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to {settings.PLATFORM_NAME}!</h1>
            <p>Your account is now active</p>
        </div>
        <div class="content">
            <h2>Hello {user.get_full_name()},</h2>
            <p>Congratulations! Your email has been verified and your account is now active.</p>
            
            <div class="features">
                <h3>What you can do now:</h3>
                <div class="feature">Invest in cryptocurrencies</div>
                <div class="feature">Explore real estate opportunities</div>
                <div class="feature">Join capital appreciation plans</div>
                <div class="feature">Refer friends and earn bonuses</div>
            </div>
            
            <div class="referral-box">
                <p><strong>🎁 Your Referral Code</strong></p>
                <p class="referral-code">{user.referral_code}</p>
                <p>Share it with friends and earn rewards!</p>
            </div>
            
            <center>
                <a href="{settings.FRONTEND_URL}/login" class="button">Get Started</a>
            </center>
        </div>
        <div class="footer">
            <p>© 2024 {settings.PLATFORM_NAME}. All rights reserved.</p>
            <p>Need help? Contact us at support@growfund.com</p>
        </div>
    </div>
</body>
</html>
        """
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return f"Welcome email sent to {user.email}"
    
    except User.DoesNotExist:
        return f"User with id {user_id} not found"
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        # Don't raise exception for welcome email
        return f"Failed to send welcome email: {e}"
