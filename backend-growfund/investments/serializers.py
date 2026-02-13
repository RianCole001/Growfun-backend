from rest_framework import serializers
from .models import Trade, TradeHistory, CapitalInvestmentPlan
from django.utils import timezone
from datetime import timedelta


class CapitalInvestmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for Capital Investment Plan"""
    
    class Meta:
        model = CapitalInvestmentPlan
        fields = [
            'id', 'plan_type', 'status', 'initial_amount', 'period_months',
            'growth_rate', 'total_return', 'final_amount', 'monthly_growth',
            'created_at', 'start_date', 'end_date', 'completed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_return', 'final_amount', 'monthly_growth', 'created_at', 'updated_at']


class CreateCapitalInvestmentPlanSerializer(serializers.Serializer):
    """Serializer for creating capital investment plans"""
    
    PLAN_CHOICES = [
        ('basic', 'Basic - 20% monthly growth'),
        ('standard', 'Standard - 30% monthly growth'),
        ('advance', 'Advance - 40%, 50%, or 60% monthly growth'),
    ]
    
    plan_type = serializers.ChoiceField(choices=['basic', 'standard', 'advance'])
    initial_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    period_months = serializers.IntegerField(min_value=1, max_value=60)
    growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    
    def validate(self, data):
        """Validate investment plan data"""
        if data['initial_amount'] <= 0:
            raise serializers.ValidationError("Initial amount must be greater than 0")
        
        plan_type = data['plan_type']
        
        # Set default growth rates based on plan type
        if plan_type == 'basic':
            data['growth_rate'] = 20.00
        elif plan_type == 'standard':
            data['growth_rate'] = 30.00
        elif plan_type == 'advance':
            # For advance, allow custom growth rates (40, 50, 60)
            if 'growth_rate' not in data or data['growth_rate'] is None:
                data['growth_rate'] = 40.00  # Default to 40%
            else:
                # Validate advance growth rates
                if data['growth_rate'] not in [40, 50, 60]:
                    raise serializers.ValidationError(
                        "Advance plan growth rate must be 40%, 50%, or 60%"
                    )
        
        return data


class CapitalInvestmentPlanDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for capital investment plans with monthly breakdown"""
    
    monthly_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = CapitalInvestmentPlan
        fields = [
            'id', 'plan_type', 'status', 'initial_amount', 'period_months',
            'growth_rate', 'total_return', 'final_amount', 'monthly_breakdown',
            'created_at', 'start_date', 'end_date', 'completed_at'
        ]
    
    def get_monthly_breakdown(self, obj):
        """Return formatted monthly breakdown"""
        return obj.monthly_growth if obj.monthly_growth else []


class TradeSerializer(serializers.ModelSerializer):
    """Serializer for Trade model"""
    
    class Meta:
        model = Trade
        fields = [
            'id', 'asset', 'trade_type', 'status', 'entry_price', 'current_price',
            'exit_price', 'quantity', 'stop_loss', 'take_profit', 'timeframe',
            'expires_at', 'profit_loss', 'profit_loss_percentage', 'created_at',
            'closed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'profit_loss', 'profit_loss_percentage', 'created_at', 'closed_at', 'updated_at']


class CreateTradeSerializer(serializers.Serializer):
    """Serializer for creating new trades"""
    
    asset = serializers.ChoiceField(choices=['gold', 'usdt'])
    trade_type = serializers.ChoiceField(choices=['buy', 'sell'])
    entry_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=4)
    stop_loss = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    take_profit = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    timeframe = serializers.ChoiceField(
        choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
        required=False,
        allow_null=True
    )
    
    def validate(self, data):
        """Validate trade data"""
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        
        if data['entry_price'] <= 0:
            raise serializers.ValidationError("Entry price must be greater than 0")
        
        # Validate stop loss and take profit
        if data.get('stop_loss') and data.get('stop_loss') <= 0:
            raise serializers.ValidationError("Stop loss must be greater than 0")
        
        if data.get('take_profit') and data.get('take_profit') <= 0:
            raise serializers.ValidationError("Take profit must be greater than 0")
        
        # For buy trades: stop loss should be below entry, take profit above
        if data['trade_type'] == 'buy':
            if data.get('stop_loss') and data['stop_loss'] >= data['entry_price']:
                raise serializers.ValidationError("For buy trades, stop loss must be below entry price")
            if data.get('take_profit') and data['take_profit'] <= data['entry_price']:
                raise serializers.ValidationError("For buy trades, take profit must be above entry price")
        
        # For sell trades: stop loss should be above entry, take profit below
        if data['trade_type'] == 'sell':
            if data.get('stop_loss') and data['stop_loss'] <= data['entry_price']:
                raise serializers.ValidationError("For sell trades, stop loss must be above entry price")
            if data.get('take_profit') and data['take_profit'] >= data['entry_price']:
                raise serializers.ValidationError("For sell trades, take profit must be below entry price")
        
        return data


class CloseTradeSerializer(serializers.Serializer):
    """Serializer for closing trades"""
    
    exit_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    close_reason = serializers.ChoiceField(choices=['manual', 'stop_loss', 'take_profit', 'expired'])


class TradeHistorySerializer(serializers.ModelSerializer):
    """Serializer for TradeHistory model"""
    
    class Meta:
        model = TradeHistory
        fields = [
            'id', 'asset', 'trade_type', 'entry_price', 'exit_price', 'quantity',
            'profit_loss', 'profit_loss_percentage', 'close_reason', 'opened_at', 'closed_at'
        ]
        read_only_fields = ['id', 'closed_at']
