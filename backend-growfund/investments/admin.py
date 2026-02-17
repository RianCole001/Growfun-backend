from django.contrib import admin
from .models import Trade, TradeHistory


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'asset', 'trade_type', 'status', 'entry_price', 'quantity', 'profit_loss', 'created_at')
    list_filter = ('asset', 'trade_type', 'status', 'created_at')
    search_fields = ('user__email', 'asset')
    readonly_fields = ('id', 'created_at', 'updated_at', 'closed_at')
    
    fieldsets = (
        ('Trade Information', {
            'fields': ('id', 'user', 'asset', 'trade_type', 'status')
        }),
        ('Pricing', {
            'fields': ('entry_price', 'current_price', 'exit_price', 'quantity')
        }),
        ('Risk Management', {
            'fields': ('stop_loss', 'take_profit', 'timeframe', 'expires_at')
        }),
        ('Performance', {
            'fields': ('profit_loss', 'profit_loss_percentage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at')
        }),
    )


@admin.register(TradeHistory)
class TradeHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'asset', 'trade_type', 'entry_price', 'exit_price', 'profit_loss', 'close_reason', 'closed_at')
    list_filter = ('asset', 'trade_type', 'close_reason', 'closed_at')
    search_fields = ('user__email', 'asset')
    readonly_fields = ('id', 'closed_at')
    
    fieldsets = (
        ('Trade Information', {
            'fields': ('id', 'user', 'asset', 'trade_type')
        }),
        ('Pricing', {
            'fields': ('entry_price', 'exit_price', 'quantity')
        }),
        ('Performance', {
            'fields': ('profit_loss', 'profit_loss_percentage')
        }),
        ('Details', {
            'fields': ('close_reason', 'opened_at', 'closed_at')
        }),
    )


# Admin Crypto Price Management
from .admin_models import AdminCryptoPrice, CryptoPriceHistory


@admin.register(AdminCryptoPrice)
class AdminCryptoPriceAdmin(admin.ModelAdmin):
    """Admin interface for crypto price management"""
    list_display = ('coin', 'name', 'buy_price', 'sell_price', 'spread_display', 'spread_pct_display', 'is_active', 'last_updated', 'updated_by')
    list_filter = ('is_active', 'last_updated')
    search_fields = ('coin', 'name')
    readonly_fields = ('spread_display', 'spread_pct_display', 'last_updated', 'created_at')
    
    fieldsets = (
        ('Coin Information', {
            'fields': ('coin', 'name', 'is_active')
        }),
        ('Pricing', {
            'fields': ('buy_price', 'sell_price', 'spread_display', 'spread_pct_display')
        }),
        ('Market Data', {
            'fields': ('change_24h', 'change_7d', 'change_30d')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'last_updated', 'created_at')
        }),
    )
    
    def spread_display(self, obj):
        return f"${obj.spread:.2f}"
    spread_display.short_description = 'Spread'
    
    def spread_pct_display(self, obj):
        return f"{obj.spread_percentage:.2f}%"
    spread_pct_display.short_description = 'Spread %'
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CryptoPriceHistory)
class CryptoPriceHistoryAdmin(admin.ModelAdmin):
    """Admin interface for price history"""
    list_display = ('coin', 'buy_price', 'sell_price', 'change_24h', 'updated_by', 'created_at')
    list_filter = ('coin', 'created_at')
    search_fields = ('coin',)
    readonly_fields = ('coin', 'buy_price', 'sell_price', 'change_24h', 'updated_by', 'created_at')
    
    def has_add_permission(self, request):
        return False  # History is auto-created
    
    def has_change_permission(self, request, obj=None):
        return False  # History cannot be modified