from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import models
from .models import UserSettings, Referral

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    referral_code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'referral_code')
    
    def validate_first_name(self, value):
        """Validate first name"""
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters.")
        if len(value.strip()) > 50:
            raise serializers.ValidationError("First name must not exceed 50 characters.")
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters.")
        if len(value.strip()) > 50:
            raise serializers.ValidationError("Last name must not exceed 50 characters.")
        return value.strip()
    
    def validate_email(self, value):
        """Validate email"""
        if not value or not value.strip():
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower().strip()
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if len(value) > 128:
            raise serializers.ValidationError("Password must not exceed 128 characters.")
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        # Check for at least one lowercase letter
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        # Check for at least one digit
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        # Check for at least one special character
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?).")
        return value
    
    def validate(self, attrs):
        """Validate password match and referral code"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        
        # Validate referral code if provided
        referral_code = attrs.get('referral_code', '').strip()
        if referral_code:
            try:
                User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                raise serializers.ValidationError({"referral_code": "Invalid referral code."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        referral_code = validated_data.pop('referral_code', '').strip()
        
        # Find referrer if code provided
        referred_by = None
        if referral_code:
            try:
                referred_by = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                pass
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            referred_by=referred_by
        )
        
        # Create user settings
        UserSettings.objects.create(user=user)
        
        # Create referral record and claim reward if referrer exists
        if referred_by:
            referral = Referral.objects.create(
                referrer=referred_by,
                referred_user=user,
                reward_amount=5.00,
                status='pending'
            )
            # Automatically claim the reward
            referral.claim_reward()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'avatar', 'location', 'occupation', 'company',
            'website', 'bio', 'balance', 'is_verified', 'referral_code',
            'created_at', 'last_login_at', 'is_staff', 'is_superuser'
        )
        read_only_fields = ('id', 'email', 'balance', 'is_verified', 'referral_code', 'created_at', 'is_staff', 'is_superuser')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    website = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'avatar',
            'location', 'occupation', 'company', 'website', 'bio'
        )
    
    def validate_website(self, value):
        """Allow empty website field"""
        if not value or value == '':
            return None
        return value


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user settings"""
    
    class Meta:
        model = UserSettings
        exclude = ('id', 'user', 'created_at', 'updated_at')


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset"""
    
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    
    token = serializers.UUIDField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for referral information"""
    
    referrer_email = serializers.CharField(source='referrer.email', read_only=True)
    referred_user_email = serializers.CharField(source='referred_user.email', read_only=True)
    referred_user_name = serializers.CharField(source='referred_user.get_full_name', read_only=True)
    
    class Meta:
        model = Referral
        fields = (
            'id', 'referrer_email', 'referred_user_email', 'referred_user_name',
            'reward_amount', 'reward_claimed', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserReferralsSerializer(serializers.ModelSerializer):
    """Serializer for user with referral information"""
    
    referrals_made = ReferralSerializer(many=True, read_only=True)
    total_referrals = serializers.SerializerMethodField()
    total_referral_earnings = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'referral_code',
            'balance', 'referrals_made', 'total_referrals', 'total_referral_earnings'
        )
        read_only_fields = ('id', 'email', 'referral_code', 'balance')
    
    def get_total_referrals(self, obj):
        """Get total number of referrals"""
        return obj.referrals_made.count()
    
    def get_total_referral_earnings(self, obj):
        """Get total referral earnings"""
        total = obj.referrals_made.filter(reward_claimed=True).aggregate(
            total=models.Sum('reward_amount')
        )['total'] or 0
        return float(total)
