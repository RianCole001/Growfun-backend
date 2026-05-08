from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from .models import User, UserSettings, Referral


# Inline admin classes for related models
class TransactionInline(admin.TabularInline):
    """Inline display of user transactions"""
    from transactions.models import Transaction
    model = Transaction
    extra = 0
    readonly_fields = ['reference', 'transaction_type', 'amount', 'status', 'created_at']
    fields = ['reference', 'transaction_type', 'amount', 'status', 'created_at']
    fk_name = 'user'
    
    def has_add_permission(self, request, obj=None):
        return False


class CapitalInvestmentInline(admin.TabularInline):
    """Inline display of capital investments"""
    from investments.models import CapitalInvestmentPlan
    model = CapitalInvestmentPlan
    extra = 0
    readonly_fields = ['plan_type', 'initial_amount', 'growth_rate', 'period_months', 'status', 'created_at']
    fields = ['plan_type', 'initial_amount', 'growth_rate', 'period_months', 'status', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


class BinaryTradeInline(admin.TabularInline):
    """Inline display of binary trades"""
    from binary_trading.models import BinaryTrade
    model = BinaryTrade
    extra = 0
    readonly_fields = ['asset', 'direction', 'amount', 'status', 'profit_loss', 'is_demo', 'opened_at']
    fields = ['asset', 'direction', 'amount', 'status', 'profit_loss', 'is_demo', 'opened_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model with financial data"""
    
    list_display = (
        'email', 'full_name_display', 'is_verified', 'balance_display', 
        'total_investments_display', 'total_deposits_display', 'transactions_count',
        'created_at'
    )
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'referral_code')
    ordering = ('-created_at',)
    
    # Add inlines to show related financial data
    inlines = []  # We'll add these conditionally in get_inlines
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Profile'), {'fields': ('location', 'occupation', 'company', 'website', 'bio')}),
        (_('Account'), {'fields': ('balance', 'is_verified', 'referral_code', 'referred_by')}),
        (_('Financial Summary'), {
            'fields': ('financial_summary_display',),
            'description': 'Overview of user financial activity'
        }),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'last_login_at', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_login_at', 'verification_token', 'financial_summary_display')
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related for better performance"""
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            'transactions',
            'capitalinvestmentplan_set', 
            'trade_set',
            'binarytrade_set',
            'usdtdepositrequest_set'
        )
    
    def get_inlines(self, request, obj):
        """Conditionally add inlines based on available models"""
        inlines = []
        
        # Only add inlines if we're viewing an existing user
        if obj:
            try:
                # Check if models exist and add appropriate inlines
                from transactions.models import Transaction
                from investments.models import CapitalInvestmentPlan
                from binary_trading.models import BinaryTrade
                
                # Add transaction inline
                class TransactionInlineLocal(admin.TabularInline):
                    model = Transaction
                    extra = 0
                    max_num = 10
                    readonly_fields = ['reference', 'transaction_type', 'amount', 'status', 'created_at']
                    fields = ['reference', 'transaction_type', 'amount', 'status', 'created_at']
                    
                    def has_add_permission(self, request, obj=None):
                        return False
                
                # Add capital investment inline
                class CapitalInvestmentInlineLocal(admin.TabularInline):
                    model = CapitalInvestmentPlan
                    extra = 0
                    max_num = 10
                    readonly_fields = ['plan_type', 'initial_amount', 'growth_rate', 'status', 'created_at']
                    fields = ['plan_type', 'initial_amount', 'growth_rate', 'status', 'created_at']
                    
                    def has_add_permission(self, request, obj=None):
                        return False
                
                # Add binary trade inline
                class BinaryTradeInlineLocal(admin.TabularInline):
                    model = BinaryTrade
                    extra = 0
                    max_num = 10
                    readonly_fields = ['asset', 'direction', 'amount', 'status', 'profit_loss', 'opened_at']
                    fields = ['asset', 'direction', 'amount', 'status', 'profit_loss', 'opened_at']
                    
                    def has_add_permission(self, request, obj=None):
                        return False
                
                inlines = [TransactionInlineLocal, CapitalInvestmentInlineLocal, BinaryTradeInlineLocal]
                
            except ImportError:
                pass
        
        return inlines
    
    def financial_summary_display(self, obj):
        """Display comprehensive financial summary"""
        if not obj.pk:
            return '-'
        
        try:
            # Get transaction summary
            transactions = obj.transactions.all()
            total_deposits = transactions.filter(
                transaction_type__in=['deposit', 'admin_credit']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            total_withdrawals = transactions.filter(
                transaction_type__in=['withdrawal', 'admin_debit']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Get investment summary
            capital_investments = getattr(obj, 'capitalinvestmentplan_set', None)
            if capital_investments:
                capital_total = capital_investments.aggregate(
                    total=Sum('initial_amount')
                )['total'] or 0
            else:
                capital_total = 0
            
            # Get binary trading summary
            binary_trades = getattr(obj, 'binarytrade_set', None)
            if binary_trades:
                binary_real = binary_trades.filter(is_demo=False)
                binary_invested = binary_real.aggregate(total=Sum('amount'))['total'] or 0
                binary_pl = binary_real.filter(
                    status__in=['won', 'lost']
                ).aggregate(total=Sum('profit_loss'))['total'] or 0
            else:
                binary_invested = 0
                binary_pl = 0
            
            # USDT deposits
            usdt_deposits = getattr(obj, 'usdtdepositrequest_set', None)
            if usdt_deposits:
                usdt_total = usdt_deposits.filter(
                    status='confirmed'
                ).aggregate(total=Sum('base_amount'))['total'] or 0
            else:
                usdt_total = 0
            
            # Create summary HTML
            summary_html = f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h4 style="margin-top: 0; color: #333;">Financial Summary</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <strong>Deposits & Credits:</strong><br>
                        Regular Deposits: <span style="color: green;">${total_deposits:,.2f}</span><br>
                        USDT Deposits: <span style="color: green;">${usdt_total:,.2f}</span><br>
                        Withdrawals: <span style="color: red;">${total_withdrawals:,.2f}</span>
                    </div>
                    <div>
                        <strong>Investments:</strong><br>
                        Capital Plans: <span style="color: blue;">${capital_total:,.2f}</span><br>
                        Binary Trading: <span style="color: purple;">${binary_invested:,.2f}</span><br>
                        Binary P&L: <span style="color: {'green' if binary_pl >= 0 else 'red'};">${binary_pl:,.2f}</span>
                    </div>
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                    <strong>Current Balance: <span style="color: {'green' if obj.balance >= 0 else 'red'}; font-size: 16px;">${obj.balance:,.2f}</span></strong>
                </div>
            </div>
            """
            
            return format_html(summary_html)
            
        except Exception as e:
            return format_html('<div style="color: red;">Error loading financial data: {}</div>', str(e))
    
    financial_summary_display.short_description = 'Financial Summary'
    
    def full_name_display(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or '-'
    full_name_display.short_description = 'Name'
    
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
        try:
            # Capital Investment Plans
            capital_total = getattr(obj, 'capitalinvestmentplan_set', obj.capitalinvestmentplan_set).aggregate(
                total=Sum('initial_amount')
            )['total'] or 0
            
            # Crypto Trades (Gold, USDT, etc.)
            trades_total = getattr(obj, 'trade_set', obj.trade_set).filter(
                status__in=['active', 'completed']
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            # Binary Trading (real money)
            binary_total = getattr(obj, 'binarytrade_set', obj.binarytrade_set).filter(
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
        except Exception:
            pass
        return '-'
    total_investments_display.short_description = 'Investments'
    
    def total_deposits_display(self, obj):
        """Display total deposits from all sources"""
        try:
            # Regular deposits and admin credits
            regular_deposits = obj.transactions.filter(
                transaction_type__in=['deposit', 'admin_credit']
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # USDT deposits
            usdt_deposits = getattr(obj, 'usdtdepositrequest_set', obj.usdtdepositrequest_set).filter(
                status='confirmed'
            ).aggregate(total=Sum('base_amount'))['total'] or 0
            
            total = float(regular_deposits) + float(usdt_deposits)
            
            if total > 0:
                return format_html(
                    '<span style="color: green; font-weight: bold;">${:,.2f}</span>',
                    total
                )
        except Exception:
            pass
        return '-'
    total_deposits_display.short_description = 'Deposits'
    
    def transactions_count(self, obj):
        """Display total transaction count"""
        try:
            count = obj.transactions.count()
            usdt_count = getattr(obj, 'usdtdepositrequest_set', obj.usdtdepositrequest_set).count()
            total = count + usdt_count
            
            if total > 0:
                return format_html('<span style="font-weight: bold;">{}</span>', total)
        except Exception:
            pass
        return '0'
    transactions_count.short_description = 'Transactions'


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

