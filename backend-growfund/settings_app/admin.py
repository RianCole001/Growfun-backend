from django.contrib import admin
from .models import PlatformSettings, SettingsHistory


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ['platform_name', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'created_at', 'updated_by']
    
    fieldsets = (
        ('General Settings', {
            'fields': ('platform_name', 'platform_email')
        }),
        ('Transaction Limits', {
            'fields': ('min_deposit', 'max_deposit', 'min_withdrawal', 'max_withdrawal')
        }),
        ('Fees', {
            'fields': ('deposit_fee', 'withdrawal_fee')
        }),
        ('Investment Minimums', {
            'fields': ('min_capital_plan_investment', 'min_crypto_investment', 'min_real_estate_investment'),
            'description': 'General minimum investment amounts for each investment type'
        }),
        ('Capital Plan Minimums', {
            'fields': ('capital_basic_min', 'capital_standard_min', 'capital_advance_min'),
            'description': 'Minimum investment amounts for each capital plan tier'
        }),
        ('Real Estate Minimums', {
            'fields': ('real_estate_starter_min', 'real_estate_premium_min', 'real_estate_luxury_min'),
            'description': 'Minimum investment amounts for each real estate tier'
        }),
        ('Automation', {
            'fields': ('auto_approve_deposits', 'auto_approve_withdrawals', 
                      'auto_approve_deposit_limit', 'auto_approve_withdrawal_limit')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Referral Program', {
            'fields': ('referral_bonus',)
        }),
        ('Metadata', {
            'fields': ('updated_at', 'created_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not PlatformSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SettingsHistory)
class SettingsHistoryAdmin(admin.ModelAdmin):
    list_display = ['setting_name', 'old_value', 'new_value', 'changed_by', 'changed_at']
    list_filter = ['setting_name', 'changed_at']
    search_fields = ['setting_name', 'changed_by__email']
    readonly_fields = ['setting_name', 'old_value', 'new_value', 'changed_by', 'changed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
