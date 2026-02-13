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
