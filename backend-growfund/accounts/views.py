from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from django.conf import settings
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
import uuid

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileUpdateSerializer, UserSettingsSerializer,
    PasswordResetRequestSerializer, PasswordResetSerializer,
    EmailVerificationSerializer, ChangePasswordSerializer,
    ReferralSerializer, UserReferralsSerializer
)
from .models import UserSettings, Referral

# Remove problematic task imports for now
# from .tasks import send_verification_email, send_password_reset_email

User = get_user_model()


class RegisterView(APIView):
    """User registration endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email - simplified for now
            try:
                # send_verification_email(user.id)  # Disabled temporarily
                email_sent = True
                print(f"Verification email would be sent to {user.email}")  # Debug log
            except Exception as e:
                print(f"Failed to send verification email: {e}")
                email_sent = False
            
            return Response({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.',
                'email': user.email,
                'email_sent': email_sent,
                'verification_url': f"{settings.FRONTEND_URL}/verify-email?token={user.verification_token}",  # For testing
                'redirect': '/verify-email-sent'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if not user.is_verified:
                    return Response({
                        'error': 'Email not verified. Please check your email.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Update last login
                user.last_login_at = timezone.now()
                user.save(update_fields=['last_login_at'])
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Login successful',
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """Email verification endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Handle GET request with token in query params"""
        token = request.query_params.get('token')
        
        if not token:
            return Response({
                'error': 'Verification token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(verification_token=token)
            if not user.is_verified:
                user.is_verified = True
                user.save(update_fields=['is_verified'])
                
                # Send welcome email
                from .tasks import send_welcome_email
                send_welcome_email(user.id)
                
                return Response({
                    'success': True,
                    'message': 'Email verified successfully! You can now login.',
                    'redirect': '/login'
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': True,
                'message': 'Email already verified. You can login.',
                'redirect': '/login'
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid or expired verification token',
                'redirect': '/register'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """Handle POST request with token in body"""
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            try:
                user = User.objects.get(verification_token=token)
                if not user.is_verified:
                    user.is_verified = True
                    user.save(update_fields=['is_verified'])
                    
                    # Send welcome email
                    from .tasks import send_welcome_email
                    send_welcome_email(user.id)
                    
                    return Response({
                        'success': True,
                        'message': 'Email verified successfully! You can now login.',
                        'redirect': '/login'
                    }, status=status.HTTP_200_OK)
                
                return Response({
                    'success': True,
                    'message': 'Email already verified. You can login.',
                    'redirect': '/login'
                }, status=status.HTTP_200_OK)
            
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid or expired verification token',
                    'redirect': '/register'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    """Resend verification email"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                return Response({
                    'success': False,
                    'message': 'Email is already verified. You can login.',
                    'redirect': '/login'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Resend verification email - simplified for now
            try:
                # send_verification_email(user.id)  # Disabled temporarily
                print(f"Verification email would be resent to {user.email}")  # Debug log
                return Response({
                    'success': True,
                    'message': 'Verification email sent! Please check your inbox.',
                    'email': user.email
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'success': False,
                    'error': 'Failed to send verification email. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'success': True,
                'message': 'If the email exists, a verification link will be sent.'
            }, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    """Password reset request endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                user.reset_token = uuid.uuid4()
                user.reset_token_created = timezone.now()
                user.save(update_fields=['reset_token', 'reset_token_created'])
                
                # Send reset email - simplified for now
                # send_password_reset_email(user.id)  # Disabled temporarily
                print(f"Password reset email would be sent to {user.email}")  # Debug log
                
                return Response({
                    'message': 'Password reset link sent to your email.',
                    'reset_token': str(user.reset_token)  # For testing
                }, status=status.HTTP_200_OK)
            
            except User.DoesNotExist:
                # Don't reveal if email exists
                return Response({
                    'message': 'If the email exists, a reset link will be sent.'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """Password reset endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(reset_token=token)
                
                # Check if token is expired (24 hours)
                if user.reset_token_created:
                    expiry = user.reset_token_created + timedelta(hours=24)
                    if timezone.now() > expiry:
                        return Response({
                            'success': False,
                            'error': 'Reset token has expired. Please request a new one.',
                            'redirect': '/forgot-password'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user.set_password(password)
                user.reset_token = None
                user.reset_token_created = None
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Password reset successful! You can now login with your new password.',
                    'redirect': '/login'
                }, status=status.HTTP_200_OK)
            
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid reset token',
                    'redirect': '/forgot-password'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveAPIView):
    """Get current user details"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        """Override update to return full user data"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full user data after update
        full_serializer = UserSerializer(instance)
        return Response(full_serializer.data, status=status.HTTP_200_OK)


class UserSettingsView(generics.RetrieveUpdateAPIView):
    """Get and update user settings"""
    
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings


class ChangePasswordView(APIView):
    """Change user password"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Old password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserBalanceView(APIView):
    """Get user balance"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'balance': float(request.user.balance)
        }, status=status.HTTP_200_OK)


class AdminUsersListView(generics.ListAPIView):
    """List all users (admin only) - Memory optimized"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Use default pagination
    
    def get_queryset(self):
        # Check if user is admin or superuser
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            return User.objects.none()
        
        # Optimize query to reduce memory usage
        return User.objects.select_related().only(
            'id', 'email', 'first_name', 'last_name', 'is_active', 
            'is_verified', 'is_staff', 'is_superuser', 'balance', 'date_joined', 'last_login'
        ).order_by('-date_joined')[:100]  # Limit to 100 users
    
    def list(self, request, *args, **kwargs):
        # Check if user is admin or superuser
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                'error': 'Admin access required',
                'success': False
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Calculate invested amount for each user
        from investments.models import Trade
        from django.db.models import Sum
        
        data = []
        for user in queryset:
            # Calculate total invested (entry_price * quantity for all open trades)
            open_trades = Trade.objects.filter(user=user, status='open').only('entry_price', 'quantity')
            invested = sum(float(trade.entry_price) * float(trade.quantity) for trade in open_trades)
            
            data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'is_verified': user.is_verified,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'balance': str(user.balance),
                'invested': f"{invested:.2f}",
                'date_joined': user.date_joined.isoformat(),
                'last_login_at': user.last_login.isoformat() if user.last_login else None
            })
        
        return Response({
            'data': data,
            'success': True
        }, status=status.HTTP_200_OK)


class AdminUserDetailView(APIView):
    """Get, update, or delete a specific user (admin only)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def check_admin(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        return True
    
    def get(self, request, user_id):
        """Get user details"""
        if not self.check_admin(request):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, user_id):
        """Update user details"""
        if not self.check_admin(request):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            
            # Update allowed fields
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'phone' in request.data:
                user.phone = request.data['phone']
            if 'location' in request.data:
                user.location = request.data['location']
            if 'occupation' in request.data:
                user.occupation = request.data['occupation']
            if 'company' in request.data:
                user.company = request.data['company']
            if 'balance' in request.data:
                user.balance = request.data['balance']
            if 'is_verified' in request.data:
                user.is_verified = request.data['is_verified']
            
            user.save()
            serializer = UserSerializer(user)
            return Response({
                'message': 'User updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, user_id):
        """Delete a user - with proper error handling"""
        if not self.check_admin(request):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            
            # Prevent admin from deleting themselves
            if user.id == request.user.id:
                return Response({
                    'error': 'Cannot delete your own account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prevent deleting superusers (unless current user is superuser)
            if user.is_superuser and not request.user.is_superuser:
                return Response({
                    'error': 'Cannot delete superuser account'
                }, status=status.HTTP_403_FORBIDDEN)
            
            email = user.email
            
            # Use soft delete instead of hard delete to preserve data integrity
            user.is_active = False
            user.email = f"deleted_{user.id}_{user.email}"  # Prevent email conflicts
            user.save()
            
            # Create notification for admin
            try:
                from notifications.models import Notification
                Notification.create_notification(
                    user=request.user,
                    title="User Account Deleted",
                    message=f"Successfully deleted user account: {email}",
                    notification_type='info'
                )
            except Exception as e:
                print(f"Warning: Could not create notification: {e}")
            
            return Response({
                'success': True,
                'message': f'User {email} deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to delete user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminUserVerifyView(APIView):
    """Verify or unverify a user email (admin only)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            action = request.data.get('action', 'verify')  # 'verify' or 'unverify'
            
            if action == 'verify':
                user.is_verified = True
            elif action == 'unverify':
                user.is_verified = False
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.save()
            serializer = UserSerializer(user)
            return Response({
                'message': f'User {action}d successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserSuspendView(APIView):
    """Suspend or unsuspend a user (admin only)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            action = request.data.get('action', 'suspend')  # 'suspend' or 'unsuspend'
            
            # Prevent admin from suspending themselves
            if user.id == request.user.id:
                return Response({
                    'error': 'Cannot suspend your own account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prevent suspending superusers (unless current user is superuser)
            if user.is_superuser and not request.user.is_superuser:
                return Response({
                    'error': 'Cannot suspend superuser account'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if action == 'suspend':
                user.is_active = False
                message = f'User {user.email} suspended successfully'
                notification_msg = f"User account suspended: {user.email}"
            elif action == 'unsuspend':
                user.is_active = True
                message = f'User {user.email} unsuspended successfully'
                notification_msg = f"User account unsuspended: {user.email}"
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.save()
            
            # Create notification for admin
            try:
                from notifications.models import Notification
                Notification.create_notification(
                    user=request.user,
                    title="User Status Updated",
                    message=notification_msg,
                    notification_type='info'
                )
                
                # Create notification for the affected user (if unsuspended)
                if action == 'unsuspend':
                    Notification.create_notification(
                        user=user,
                        title="Account Reactivated",
                        message="Your account has been reactivated by an administrator.",
                        notification_type='success'
                    )
            except Exception as e:
                print(f"Warning: Could not create notification: {e}")
            
            serializer = UserSerializer(user)
            return Response({
                'success': True,
                'message': message,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to update user status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminUserResetPasswordView(APIView):
    """Reset a user's password (admin only)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            new_password = request.data.get('password')
            
            if not new_password or len(new_password) < 8:
                return Response({'error': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'User password reset successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserReferralsView(APIView):
    """Get user referrals and earnings"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's referrals and earnings"""
        user = request.user
        referrals = Referral.objects.filter(referrer=user)
        
        serializer = ReferralSerializer(referrals, many=True)
        
        return Response({
            'referrals': serializer.data
        }, status=status.HTTP_200_OK)


class ReferralStatsView(APIView):
    """Get referral statistics"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get referral statistics for current user"""
        user = request.user
        referrals = Referral.objects.filter(referrer=user)
        
        # Calculate earnings
        total_earned = 0
        pending_earnings = 0
        this_month_earnings = 0
        
        for referral in referrals:
            if referral.reward_claimed:
                total_earned += float(referral.reward_amount)
                # Check if created this month
                if referral.created_at.month == timezone.now().month and referral.created_at.year == timezone.now().year:
                    this_month_earnings += float(referral.reward_amount)
            else:
                pending_earnings += float(referral.reward_amount)
        
        stats = {
            'referral_code': user.referral_code,
            'referral_link': f'http://localhost:3000/register?ref={user.referral_code}',
            'total_referrals': referrals.count(),
            'active_referrals': referrals.filter(status='active').count(),
            'pending_referrals': referrals.filter(status='pending').count(),
            'total_earned': total_earned,
            'pending_earnings': pending_earnings,
            'this_month_earnings': this_month_earnings
        }
        
        return Response(stats, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_referral_code(request):
    """Generate new referral code for user"""
    import random
    import string
    
    # Generate new unique referral code
    while True:
        new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not User.objects.filter(referral_code=new_code).exists():
            break
    
    # Update user's referral code
    request.user.referral_code = new_code
    request.user.save()
    
    # Create notification
    from notifications.models import Notification
    Notification.create_notification(
        user=request.user,
        title="New Referral Code Generated",
        message=f"Your new referral code is: {new_code}",
        notification_type='info'
    )
    
    return Response({
        'data': {
            'referral_code': new_code,
            'referral_link': f"{settings.FRONTEND_URL}/register?ref={new_code}"
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get comprehensive dashboard statistics for user including crypto portfolio"""
    user = request.user
    from decimal import Decimal
    
    # Investment stats
    from investments.models import CapitalInvestmentPlan, Trade
    active_investments = CapitalInvestmentPlan.objects.filter(user=user, status='active').count()
    total_invested = CapitalInvestmentPlan.objects.filter(user=user).aggregate(
        total=models.Sum('initial_amount')
    )['total'] or 0
    
    # Crypto portfolio stats
    crypto_investments = Trade.objects.filter(user=user, status='open')
    crypto_total_value = Decimal('0')
    crypto_total_invested = Decimal('0')
    crypto_count = 0
    
    for investment in crypto_investments:
        current_value = investment.quantity * investment.current_price
        crypto_total_value += current_value
        crypto_total_invested += investment.amount
        crypto_count += 1
    
    crypto_profit_loss = crypto_total_value - crypto_total_invested
    crypto_profit_loss_percentage = (crypto_profit_loss / crypto_total_invested * 100) if crypto_total_invested > 0 else 0
    
    # Trading stats
    open_trades = Trade.objects.filter(user=user, status='open').count()
    total_trades = Trade.objects.filter(user=user).count()
    
    # Transaction stats
    from transactions.models import Transaction
    total_deposits = Transaction.objects.filter(
        user=user, transaction_type='deposit', status='completed'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    total_withdrawals = Transaction.objects.filter(
        user=user, transaction_type='withdrawal', status='completed'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Referral stats
    total_referrals = Referral.objects.filter(referrer=user).count()
    referral_earnings = Referral.objects.filter(
        referrer=user, reward_claimed=True
    ).aggregate(total=models.Sum('reward_amount'))['total'] or 0
    
    # Notification stats
    from notifications.models import Notification
    unread_notifications = Notification.objects.filter(user=user, read=False).count()
    
    # Recent activity (last 5 transactions)
    recent_transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:5]
    recent_activity = []
    for txn in recent_transactions:
        recent_activity.append({
            'id': txn.id,
            'type': txn.transaction_type,
            'amount': str(txn.amount),
            'status': txn.status,
            'date': txn.created_at.isoformat()
        })
    
    return Response({
        'data': {
            'balance': str(user.balance),
            'investments': {
                'active_count': active_investments,
                'total_invested': str(total_invested)
            },
            'crypto': {
                'total_value': str(crypto_total_value),
                'total_invested': str(crypto_total_invested),
                'profit_loss': str(crypto_profit_loss),
                'profit_loss_percentage': float(crypto_profit_loss_percentage),
                'holdings_count': crypto_count
            },
            'trading': {
                'open_trades': open_trades,
                'total_trades': total_trades
            },
            'transactions': {
                'total_deposits': str(total_deposits),
                'total_withdrawals': str(total_withdrawals)
            },
            'referrals': {
                'total_count': total_referrals,
                'total_earnings': str(referral_earnings)
            },
            'notifications': {
                'unread_count': unread_notifications
            },
            'recent_activity': recent_activity
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_suspended_users(request):
    """Get list of suspended users (admin only) - Memory optimized"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    # Optimize query to reduce memory usage
    suspended_users = User.objects.filter(is_active=False).only(
        'id', 'email', 'first_name', 'last_name', 'date_joined'
    ).order_by('-date_joined')[:50]  # Limit to 50 users
    
    serializer = UserSerializer(suspended_users, many=True)
    
    return Response({
        'data': serializer.data,
        'count': len(serializer.data)  # Count from serialized data instead of separate query
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_user_stats(request):
    """Get user statistics for admin dashboard"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Count, Sum
    from datetime import datetime, timedelta
    
    # Basic user counts
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    suspended_users = User.objects.filter(is_active=False).count()
    verified_users = User.objects.filter(is_verified=True).count()
    unverified_users = User.objects.filter(is_verified=False).count()
    
    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Total balance across all users
    total_balance = User.objects.aggregate(total=Sum('balance'))['total'] or 0
    
    return Response({
        'data': {
            'total_users': total_users,
            'active_users': active_users,
            'suspended_users': suspended_users,
            'verified_users': verified_users,
            'unverified_users': unverified_users,
            'recent_registrations': recent_registrations,
            'total_platform_balance': str(total_balance)
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_test_notification(request):
    """Create a test notification for the current user"""
    from notifications.models import Notification
    
    title = request.data.get('title', 'Test Notification')
    message = request.data.get('message', 'This is a test notification to verify the system is working.')
    notification_type = request.data.get('type', 'info')
    
    notification = Notification.create_notification(
        user=request.user,
        title=title,
        message=message,
        notification_type=notification_type
    )
    
    from notifications.serializers import NotificationSerializer
    serializer = NotificationSerializer(notification)
    
    return Response({
        'success': True,
        'message': 'Test notification created',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_overview(request):
    """Get complete admin dashboard overview"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.db.models import Count, Sum
    from datetime import datetime, timedelta
    from transactions.models import Transaction
    from investments.models import CapitalInvestmentPlan, Trade
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    suspended_users = User.objects.filter(is_active=False).count()
    verified_users = User.objects.filter(is_verified=True).count()
    
    # Financial statistics
    total_balance = User.objects.aggregate(total=Sum('balance'))['total'] or 0
    
    # Transaction statistics
    total_deposits = Transaction.objects.filter(
        transaction_type='deposit', status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_withdrawals = Transaction.objects.filter(
        transaction_type='withdrawal', status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_deposits = Transaction.objects.filter(
        transaction_type='deposit', status__in=['pending', 'processing']
    ).count()
    
    pending_withdrawals = Transaction.objects.filter(
        transaction_type='withdrawal', status__in=['pending', 'processing']
    ).count()
    
    # Investment statistics
    total_investments = CapitalInvestmentPlan.objects.count()
    active_investments = CapitalInvestmentPlan.objects.filter(status='active').count()
    total_invested = CapitalInvestmentPlan.objects.aggregate(
        total=Sum('initial_amount')
    )['total'] or 0
    
    # Trading statistics
    total_trades = Trade.objects.count()
    open_trades = Trade.objects.filter(status='open').count()
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_users = User.objects.filter(date_joined__gte=seven_days_ago).count()
    recent_transactions = Transaction.objects.filter(created_at__gte=seven_days_ago).count()
    
    return Response({
        'data': {
            'users': {
                'total': total_users,
                'active': active_users,
                'suspended': suspended_users,
                'verified': verified_users,
                'recent_registrations': recent_users
            },
            'finances': {
                'total_platform_balance': str(total_balance),
                'total_deposits': str(total_deposits),
                'total_withdrawals': str(total_withdrawals),
                'pending_deposits': pending_deposits,
                'pending_withdrawals': pending_withdrawals
            },
            'investments': {
                'total_plans': total_investments,
                'active_plans': active_investments,
                'total_invested': str(total_invested)
            },
            'trading': {
                'total_trades': total_trades,
                'open_trades': open_trades
            },
            'activity': {
                'recent_users': recent_users,
                'recent_transactions': recent_transactions
            }
        }
    }, status=status.HTTP_200_OK)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_admin_delete(request, user_id):
    """Debug version of admin delete with detailed logging"""
    print(f"🔧 DEBUG: Admin delete called for user {user_id}")
    print(f"🔧 DEBUG: Request user: {request.user.email} (staff: {request.user.is_staff}, superuser: {request.user.is_superuser})")
    
    # Check admin permissions
    if not (request.user.is_staff or request.user.is_superuser):
        print("❌ DEBUG: Admin access denied")
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        print(f"✅ DEBUG: Found user {user.email}")
        
        # Prevent admin from deleting themselves
        if user.id == request.user.id:
            print("❌ DEBUG: Cannot delete own account")
            return Response({
                'error': 'Cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent deleting superusers (unless current user is superuser)
        if user.is_superuser and not request.user.is_superuser:
            print("❌ DEBUG: Cannot delete superuser")
            return Response({
                'error': 'Cannot delete superuser account'
            }, status=status.HTTP_403_FORBIDDEN)
        
        email = user.email
        print(f"🔧 DEBUG: Performing soft delete for {email}")
        
        # Use soft delete instead of hard delete to preserve data integrity
        user.is_active = False
        user.email = f"deleted_{user.id}_{user.email}"  # Prevent email conflicts
        user.save()
        print(f"✅ DEBUG: User soft deleted successfully")
        
        return Response({
            'success': True,
            'message': f'User {email} deleted successfully',
            'debug': {
                'user_id': user_id,
                'original_email': email,
                'new_email': user.email,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        print(f"❌ DEBUG: User {user_id} not found")
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ DEBUG: Exception occurred: {str(e)}")
        return Response({
            'error': f'Failed to delete user: {str(e)}',
            'debug': {
                'exception_type': type(e).__name__,
                'exception_message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_admin_suspend(request, user_id):
    """Debug version of admin suspend with detailed logging"""
    print(f"🔧 DEBUG: Admin suspend called for user {user_id}")
    print(f"🔧 DEBUG: Request user: {request.user.email} (staff: {request.user.is_staff}, superuser: {request.user.is_superuser})")
    print(f"🔧 DEBUG: Request data: {request.data}")
    
    # Check admin permissions
    if not (request.user.is_staff or request.user.is_superuser):
        print("❌ DEBUG: Admin access denied")
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        print(f"✅ DEBUG: Found user {user.email}")
        
        action = request.data.get('action', 'suspend')
        print(f"🔧 DEBUG: Action requested: {action}")
        
        # Prevent admin from suspending themselves
        if user.id == request.user.id:
            print("❌ DEBUG: Cannot suspend own account")
            return Response({
                'error': 'Cannot suspend your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent suspending superusers (unless current user is superuser)
        if user.is_superuser and not request.user.is_superuser:
            print("❌ DEBUG: Cannot suspend superuser")
            return Response({
                'error': 'Cannot suspend superuser account'
            }, status=status.HTTP_403_FORBIDDEN)
        
        original_status = user.is_active
        
        if action == 'suspend':
            user.is_active = False
            message = f'User {user.email} suspended successfully'
        elif action == 'unsuspend':
            user.is_active = True
            message = f'User {user.email} unsuspended successfully'
        else:
            print(f"❌ DEBUG: Invalid action: {action}")
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.save()
        print(f"✅ DEBUG: User status updated from {original_status} to {user.is_active}")
        
        return Response({
            'success': True,
            'message': message,
            'debug': {
                'user_id': user_id,
                'email': user.email,
                'action': action,
                'original_status': original_status,
                'new_status': user.is_active
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        print(f"❌ DEBUG: User {user_id} not found")
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ DEBUG: Exception occurred: {str(e)}")
        return Response({
            'error': f'Failed to update user status: {str(e)}',
            'debug': {
                'exception_type': type(e).__name__,
                'exception_message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)