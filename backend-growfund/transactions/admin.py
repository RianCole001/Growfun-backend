from django.contrib import admin
from .models import Transaction, MoMoPayment

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'payment_method', 'created_at']
    search_fields = ['reference', 'user__email', 'phone_number', 'external_reference']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'transaction_type', 'payment_method', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'fee', 'net_amount')
        }),
        ('References', {
            'fields': ('reference', 'external_reference', 'phone_number')
        }),
        ('Additional Info', {
            'fields': ('description', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(MoMoPayment)
class MoMoPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'phone_number', 'network', 'momo_reference', 'created_at']
    list_filter = ['network', 'created_at']
    search_fields = ['phone_number', 'momo_reference', 'momo_transaction_id']
    readonly_fields = ['created_at', 'updated_at']
