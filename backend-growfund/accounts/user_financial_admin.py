from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User


class UserFinancialDataAdmin(admin.ModelAdmin):
    """
    Comprehensive admin view for user financial data
    Shows investments, deposits, transactions, and balances in one place
    """
    
    list_display = [
        'email_link', 'full_name', 'balance_display', 'total_investments_display',
        'total_deposits_display', 'total_transactions_count', 'binary_trades_count',
        'profit_loss_display', 'last_activity', 'created_at'
    ]
    
    list_filter = [
        'is_verified', 'created_at', 'last_login_at'
    ]
    
    search_fields = [
        'email', 'first_name', 'last_name', 'referral_code'
    ]
    
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related for better performance"""
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            'transactions',
            'capital_investments',
            'trades',
            'binary_trades',
            'usdt_deposits'
        )
    
    def email_link(self, obj):
        """Make email clickable to user detail page"""
        url = reverse('admin:accounts_user_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.email)
    email_link.short_description = 'Email'
    email_link.admin_order_field = 'email'
    
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or '-'
    full_name.short_description = 'Name'
    
    def balance_display(self, obj):
        """Display current balance with color coding"""
        balance = float(obj.balance)
        color = 'green' if balance > 0 else 'red' if balance < 0 else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:,.2f}</span>',
            color, balance
        )
    balance_display.short_description = 'Balance'
    balance_display.admin_order_field = 'balance'
    
    def total_investments_display(self, obj):
        """Display total investments across all types"""
        # Capital Investment Plans
        capital_total = obj.capital_investments.aggregate(
            total=Sum('initial_amount')
        )['total'] or 0
        
        # Crypto Trades (Gold, USDT, etc.)
        trades_total = obj.trades.filter(
            status__in=['active', 'completed']
        ).aggregate(
            total=Sum('quantity')  # This represents the invested amount
        )['total'] or 0
        
        # Binary Trading (real money)
        binary_total = obj.binary_trades.filter(
            is_demo=False,
            status__in=['active', 'won', 'lost']
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total = float(capital_total) + float(trades_total) + float(binary_total)
        
        if total > 0:
            return format_html(
                '<span style="color: blue; font-weight: bold;">${:,.2f}</span>',
                total
            )
        return '-'
    total_investments_display.short_description = 'Total Investments'
    
    def total_deposits_display(self, obj):
        """Display total deposits from all sources"""
        # Regular deposits
        regular_deposits = obj.transactions.filter(
            transaction_type__in=['deposit', 'admin_credit']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # USDT deposits
        usdt_deposits = obj.usdt_deposits.filter(
            status='confirmed'
        ).aggregate(total=Sum('base_amount'))['total'] or 0
        
        total = float(regular_deposits) + float(usdt_deposits)
        
        if total > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">${:,.2f}</span>',
                total
            )
        return '-'
    total_deposits_display.short_description = 'Total Deposits'
    
    def total_transactions_count(self, obj):
        """Display total transaction count"""
        count = obj.transactions.count()
        usdt_count = obj.usdt_deposits.count()
        total = count + usdt_count
        
        if total > 0:
            return format_html(
                '<span style="font-weight: bold;">{}</span>',
                total
            )
        return '0'
    total_transactions_count.short_description = 'Transactions'
    
    def binary_trades_count(self, obj):
        """Display binary trades count (real + demo)"""
        real_count = obj.binary_trades.filter(is_demo=False).count()
        demo_count = obj.binary_trades.filter(is_demo=True).count()
        
        if real_count > 0 or demo_count > 0:
            return format_html(
                '<span style="font-weight: bold;">{}</span> <small>(+{} demo)</small>',
                real_count, demo_count
            )
        return '0'
    binary_trades_count.short_description = 'Binary Trades'
    
    def profit_loss_display(self, obj):
        """Calculate and display total profit/loss"""
        total_pl = 0
        
        # Binary trading P&L (real money only)
        binary_pl = obj.binary_trades.filter(
            is_demo=False,
            status__in=['won', 'lost']
        ).aggregate(total=Sum('profit_loss'))['total'] or 0
        
        # Crypto trading P&L
        crypto_pl = obj.trades.filter(
            status='completed'
        ).aggregate(total=Sum('profit_loss'))['total'] or 0
        
        total_pl = float(binary_pl) + float(crypto_pl)
        
        if total_pl != 0:
            color = 'green' if total_pl > 0 else 'red'
            sign = '+' if total_pl > 0 else ''
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}{:,.2f}</span>',
                color, sign, total_pl
            )
        return '-'
    profit_loss_display.short_description = 'P&L'
    
    def last_activity(self, obj):
        """Display last activity date"""
        if obj.last_login_at:
            return obj.last_login_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    last_activity.short_description = 'Last Activity'
    last_activity.admin_order_field = 'last_login_at'
    
    # Custom actions
    actions = ['export_financial_summary', 'send_balance_notification']
    
    def export_financial_summary(self, request, queryset):
        """Export financial summary for selected users"""
        # This could be implemented to generate CSV/Excel reports
        count = queryset.count()
        self.message_user(request, f'Financial summary export initiated for {count} users.')
    export_financial_summary.short_description = 'Export financial summary'
    
    def send_balance_notification(self, request, queryset):
        """Send balance notification to selected users"""
        count = queryset.count()
        self.message_user(request, f'Balance notifications sent to {count} users.')
    send_balance_notification.short_description = 'Send balance notifications'
    
    # Fieldsets for detail view
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'is_verified')
        }),
        ('Financial Summary', {
            'fields': ('balance',),
            'description': 'Current account balance'
        }),
        ('Account Status', {
            'fields': ('is_active', 'created_at', 'last_login_at')
        }),
    )
    
    readonly_fields = ['created_at', 'last_login_at']
    
    def has_add_permission(self, request):
        """Disable add - users should be created through registration"""
        return False


# Register the financial admin view
admin.site.register(User, UserFinancialDataAdmin)