from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserSettings, Referral


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    
    list_display = ('email', 'first_name', 'last_name', 'is_verified', 'balance', 'created_at')
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'referral_code')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Profile'), {'fields': ('location', 'occupation', 'company', 'website', 'bio')}),
        (_('Account'), {'fields': ('balance', 'is_verified', 'referral_code', 'referred_by')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'last_login_at', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_login_at', 'verification_token')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for UserSettings model"""
    
    list_display = ('user', 'theme', 'currency', 'email_notifications', 'two_factor_enabled')
    list_filter = ('theme', 'currency', 'email_notifications', 'two_factor_enabled')
    search_fields = ('user__email',)
    
    fieldsets = (
        (_('General'), {'fields': ('user', 'theme', 'currency', 'language', 'timezone')}),
        (_('Notifications'), {'fields': ('email_notifications', 'push_notifications', 'price_alerts', 'transaction_alerts', 'referral_alerts', 'marketing_emails')}),
        (_('Security'), {'fields': ('two_factor_enabled', 'login_alerts', 'session_timeout')}),
        (_('Privacy'), {'fields': ('profile_visible', 'portfolio_visible', 'activity_sharing')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    """Admin configuration for Referral model"""
    
    list_display = ('referrer', 'referred_user', 'reward_amount', 'reward_claimed', 'status', 'created_at')
    list_filter = ('status', 'reward_claimed', 'created_at')
    search_fields = ('referrer__email', 'referred_user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Referral Info'), {'fields': ('id', 'referrer', 'referred_user')}),
        (_('Reward'), {'fields': ('reward_amount', 'reward_claimed')}),
        (_('Status'), {'fields': ('status',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['claim_rewards']
    
    def claim_rewards(self, request, queryset):
        """Admin action to claim rewards"""
        count = 0
        for referral in queryset:
            if referral.claim_reward():
                count += 1
        self.message_user(request, f'{count} referral rewards claimed successfully.')
    
    claim_rewards.short_description = 'Claim selected referral rewards'

