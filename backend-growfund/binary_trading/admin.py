from django.contrib import admin
from .models import TradingAsset, BinaryTrade, UserTradingStats, AssetPrice, HouseEdgeConfig


@admin.register(TradingAsset)
class TradingAssetAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'asset_type', 'base_payout', 'volatility', 'is_active']
    list_filter = ['asset_type', 'is_active']
    search_fields = ['symbol', 'name']
    ordering = ['symbol']


@admin.register(BinaryTrade)
class BinaryTradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'asset_symbol', 'direction', 'amount', 'status', 'profit_loss', 'opened_at']
    list_filter = ['status', 'direction', 'asset']
    search_fields = ['user__email', 'asset__symbol']
    readonly_fields = ['id', 'opened_at', 'closed_at']
    ordering = ['-opened_at']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def asset_symbol(self, obj):
        return obj.asset.symbol
    asset_symbol.short_description = 'Asset'


@admin.register(UserTradingStats)
class UserTradingStatsAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'total_trades', 'total_wins', 'total_losses', 'win_rate_display', 'net_profit', 'is_flagged']
    list_filter = ['is_flagged']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def win_rate_display(self, obj):
        return f"{obj.win_rate:.2f}%"
    win_rate_display.short_description = 'Win Rate'


@admin.register(AssetPrice)
class AssetPriceAdmin(admin.ModelAdmin):
    list_display = ['asset_symbol', 'price', 'timestamp']
    list_filter = ['asset', 'timestamp']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def asset_symbol(self, obj):
        return obj.asset.symbol
    asset_symbol.short_description = 'Asset'


@admin.register(HouseEdgeConfig)
class HouseEdgeConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'updated_at']
    list_filter = ['is_active']
    fieldsets = (
        ('General', {
            'fields': ('name', 'is_active')
        }),
        ('Payout Reduction', {
            'fields': (
                'win_streak_3_reduction', 'win_streak_5_reduction',
                'high_amount_threshold', 'high_amount_reduction',
                'very_high_amount_threshold', 'very_high_amount_reduction',
                'high_profit_threshold', 'high_profit_reduction'
            )
        }),
        ('Strike Price Manipulation', {
            'fields': ('strike_price_adjustment',)
        }),
        ('Execution Delay', {
            'fields': ('min_delay_ms', 'max_delay_ms')
        }),
        ('Risk Limits', {
            'fields': (
                'max_open_trades_per_user',
                'max_exposure_per_asset',
                'max_total_exposure'
            )
        }),
    )
