from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from django.conf import settings
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
from .tasks import send_verification_email, send_password_reset_email

User = get_user_model()


class RegisterView(APIView):
    """User registration endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email
            try:
                send_verification_email(user.id)
                email_sent = True
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
            
            # Resend verification email
            try:
                send_verification_email(user.id)
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
                
                # Send reset email
                send_password_reset_email(user.id)
                
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
    """List all users (admin only)"""
    
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if user is admin or superuser
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            return User.objects.none()
        return User.objects.all().order_by('-date_joined')
    
    def list(self, request, *args, **kwargs):
        # Check if user is admin or superuser
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)


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
        """Delete a user"""
        if not self.check_admin(request):
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id)
            email = user.email
            user.delete()
            return Response({
                'message': f'User {email} deleted successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


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
            
            if action == 'suspend':
                user.is_active = False
            elif action == 'unsuspend':
                user.is_active = True
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.save()
            serializer = UserSerializer(user)
            return Response({
                'message': f'User {action}ed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


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
