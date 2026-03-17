from rest_framework import serializers
from .models import TradingAsset, BinaryTrade, UserTradingStats, AssetPrice, HouseEdgeConfig, DemoTradingStats
from decimal import Decimal


class TradingAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingAsset
        fields = [
            'id', 'symbol', 'name', 'asset_type', 'base_payout',
            'volatility', 'is_active', 'min_trade_amount', 'max_trade_amount'
        ]


class AssetPriceSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source='asset.symbol', read_only=True)
    
    class Meta:
        model = AssetPrice
        fields = ['asset_symbol', 'price', 'timestamp']


class OpenTradeSerializer(serializers.Serializer):
    asset_symbol = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=['buy', 'sell'])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('10.00'))
    expiry_seconds = serializers.IntegerField(min_value=60, max_value=3600)
    is_demo = serializers.BooleanField(default=False)
    
    def validate_asset_symbol(self, value):
        try:
            asset = TradingAsset.objects.get(symbol=value.upper(), is_active=True)
        except TradingAsset.DoesNotExist:
            raise serializers.ValidationError("Asset not found or inactive")
        return value.upper()


class BinaryTradeSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source='asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    potential_profit = serializers.SerializerMethodField()
    
    class Meta:
        model = BinaryTrade
        fields = [
            'id', 'asset_symbol', 'asset_name', 'direction', 'amount',
            'strike_price', 'final_price', 'adjusted_payout_percentage',
            'expiry_seconds', 'opened_at', 'expires_at', 'closed_at',
            'status', 'profit_loss', 'time_remaining', 'potential_profit',
            'is_demo'
        ]
    
    def get_time_remaining(self, obj):
        if obj.status == 'active':
            from django.utils import timezone
            remaining = (obj.expires_at - timezone.now()).total_seconds()
            return max(0, int(remaining))
        return 0
    
    def get_potential_profit(self, obj):
        if obj.status in ['active', 'pending']:
            return obj.amount * (obj.adjusted_payout_percentage / 100)
        return obj.profit_loss


class UserTradingStatsSerializer(serializers.ModelSerializer):
    win_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = UserTradingStats
        fields = [
            'total_trades', 'total_wins', 'total_losses',
            'current_win_streak', 'max_win_streak', 'win_rate',
            'total_profit', 'total_loss', 'net_profit', 'total_volume'
        ]


# Reuse same field layout for demo stats
class DemoTradingStatsSerializer(serializers.ModelSerializer):
    win_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = DemoTradingStats
        fields = [
            'total_trades', 'total_wins', 'total_losses',
            'current_win_streak', 'max_win_streak', 'win_rate',
            'total_profit', 'total_loss', 'net_profit', 'total_volume'
        ]


class HouseEdgeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseEdgeConfig
        fields = '__all__'
