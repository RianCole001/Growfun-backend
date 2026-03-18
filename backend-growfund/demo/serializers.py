from rest_framework import serializers
from .models import DemoAccount, DemoInvestment, DemoTransaction

class DemoAccountSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = DemoAccount
        fields = ['id', 'user_email', 'balance', 'is_active', 'created_at', 'updated_at']

class DemoInvestmentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=8, read_only=True)
    price_at_purchase = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    monthly_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    current_price = serializers.SerializerMethodField()

    def get_current_price(self, obj):
        try:
            return str(obj.current_price) if obj.current_price is not None else None
        except Exception:
            return None

    class Meta:
        model = DemoInvestment
        fields = [
            'id', 'investment_type', 'asset_name', 'amount', 'quantity',
            'price_at_purchase', 'current_price', 'monthly_rate', 'duration_months',
            'status', 'created_at', 'updated_at'
        ]

class DemoTransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=8, read_only=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = DemoTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'asset', 'quantity', 
            'price', 'status', 'description', 'created_at'
        ]