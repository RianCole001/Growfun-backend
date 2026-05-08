from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Transaction, MoMoPayment
from .usdt_models import USDTDepositRequest

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'transaction_type', 'amount', 'status', 'created_at', 'is_admin_transaction']
    list_filter = ['transaction_type', 'status', 'payment_method', 'created_at']
    search_fields = ['reference', 'user__email', 'user__first_name', 'user__last_name', 'phone_number', 'external_reference', 'description']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'transaction_type', 'payment_method', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'fee', 'net_amount'),
            'description': 'Edit these fields to update the transaction amounts. Changes will be reflected in transaction history.'
        }),
        ('References', {
            'fields': ('reference', 'external_reference', 'phone_number')
        }),
        ('Additional Info', {
            'fields': ('description', 'metadata'),
            'description': 'Description is editable and will be shown in user transaction history.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def is_admin_transaction(self, obj):
        """Display if this is an admin credit/debit"""
        if obj.transaction_type in ['admin_credit', 'admin_debit']:
            color = 'green' if obj.transaction_type == 'admin_credit' else 'orange'
            return format_html(
                '<span style="color: {}; font-weight: bold;">✓ Admin</span>',
                color
            )
        return '-'
    is_admin_transaction.short_description = 'Admin Transaction'
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields editable for admin transactions"""
        readonly = list(self.readonly_fields)
        
        # If it's an existing admin credit/debit transaction, allow editing more fields
        if obj and obj.transaction_type in ['admin_credit', 'admin_debit']:
            # Only keep reference, created_at, and updated_at as readonly
            return ['reference', 'created_at', 'updated_at']
        
        # For other transactions, keep more fields readonly
        if obj:
            readonly.extend(['user', 'transaction_type', 'payment_method'])
        
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Handle saving with balance adjustments if amounts changed"""
        if change and obj.transaction_type in ['admin_credit', 'admin_debit']:
            # Get the old transaction to compare
            old_obj = Transaction.objects.get(pk=obj.pk)
            
            # If amount changed, adjust user balance
            if old_obj.amount != obj.amount:
                amount_diff = obj.amount - old_obj.amount
                
                if obj.transaction_type == 'admin_credit':
                    obj.user.balance += amount_diff
                else:  # admin_debit
                    obj.user.balance -= amount_diff
                
                obj.user.save(update_fields=['balance'])
                
                # Update description to note the edit
                if not obj.description or 'Edited by admin' not in obj.description:
                    obj.description = f"{obj.description or ''}\nEdited by admin {request.user.email} on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Update completed_at if status changed to completed
        if obj.status == 'completed' and not obj.completed_at:
            obj.completed_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(MoMoPayment)
class MoMoPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'phone_number', 'network', 'momo_reference', 'created_at']
    list_filter = ['network', 'created_at']
    search_fields = ['phone_number', 'momo_reference', 'momo_transaction_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(USDTDepositRequest)
class USDTDepositRequestAdmin(admin.ModelAdmin):
    """Admin interface for USDT Deposit Requests"""
    list_display = ['user_email', 'base_amount', 'expected_amount', 'status', 'tx_hash_short', 'created_at', 'confirmed_at']
    list_filter = ['status', 'created_at', 'confirmed_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'tx_hash', 'wallet_address']
    readonly_fields = ['id', 'created_at', 'expires_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Deposit Information', {
            'fields': ('id', 'user', 'status')
        }),
        ('Amount Details', {
            'fields': ('base_amount', 'expected_amount')
        }),
        ('Blockchain Details', {
            'fields': ('wallet_address', 'tx_hash')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'confirmed_at', 'expires_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def tx_hash_short(self, obj):
        if obj.tx_hash:
            return f"{obj.tx_hash[:10]}...{obj.tx_hash[-10:]}" if len(obj.tx_hash) > 20 else obj.tx_hash
        return '-'
    tx_hash_short.short_description = 'Transaction Hash'
    
    actions = ['mark_confirmed', 'mark_failed']
    
    def mark_confirmed(self, request, queryset):
        """Mark selected deposits as confirmed"""
        count = queryset.filter(status='pending').update(
            status='confirmed',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'Marked {count} deposits as confirmed.')
    mark_confirmed.short_description = 'Mark selected deposits as confirmed'
    
    def mark_failed(self, request, queryset):
        """Mark selected deposits as failed"""
        count = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'Marked {count} deposits as failed.')
    mark_failed.short_description = 'Mark selected deposits as failed'
