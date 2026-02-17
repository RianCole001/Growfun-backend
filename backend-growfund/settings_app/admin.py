from django.contrib import admin
from .models import PlatformSettings, SettingsHistory


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ['platform_name', 'maintenance_mode', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'created_at', 'updated_by']
    
    fieldsets = (
        ('General Settings', {
            'fields': ('platform_name', 'platform_email', 'maintenance_mode')
        }),
        ('Transaction Limits', {
            'fields': ('min_deposit', 'max_deposit', 'min_withdrawal', 'max_withdrawal')
        }),
        ('Fees', {
            'fields': ('deposit_fee', 'withdrawal_fee')
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
