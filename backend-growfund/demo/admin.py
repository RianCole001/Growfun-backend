from django.contrib import admin
from django.utils.html import format_html
from .models import DemoAccount, DemoInvestment, DemoTransaction


@admin.register(DemoAccount)
class DemoAccountAdmin(admin.ModelAdmin):
    """Admin interface for Demo Accounts"""
    list_display = ('user', 'balance', 'is_active', 'investment_count', 'transaction_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'investment_count', 'transaction_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'balance', 'is_active')
        }),
        ('Statistics', {
            'fields': ('investment_count', 'transaction_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def investment_count(self, obj):
        """Display number of investments"""
        count = obj.investments.count()
        return format_html('<strong>{}</strong> investments', count)
    investment_count.short_description = 'Investments'
    
    def transaction_count(self, obj):
        """Display number of transactions"""
        count = obj.transactions.count()
        return format_html('<strong>{}</strong> transactions', count)
    transaction_count.short_description = 'Transactions'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(DemoInvestment)
class DemoInvestmentAdmin(admin.ModelAdmin):
    """Admin interface for Demo Investments"""
    list_display = ('demo_account', 'investment_type', 'asset_name', 'amount', 'quantity', 'status', 'created_at')
    list_filter = ('investment_type', 'status', 'created_at')
    search_fields = ('demo_account__user__email', 'asset_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Investment Information', {
            'fields': ('demo_account', 'investment_type', 'asset_name', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'quantity', 'price_at_purchase', 'current_price')
        }),
        ('Plan Details (for Capital Plans)', {
            'fields': ('monthly_rate', 'duration_months'),
            'description': 'These fields are only used for capital plan investments.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('demo_account', 'demo_account__user')


@admin.register(DemoTransaction)
class DemoTransactionAdmin(admin.ModelAdmin):
    """Admin interface for Demo Transactions"""
    list_display = ('demo_account', 'transaction_type', 'amount', 'asset', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('demo_account__user__email', 'asset', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('demo_account', 'transaction_type', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount', 'asset', 'quantity', 'price')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('demo_account', 'demo_account__user')
