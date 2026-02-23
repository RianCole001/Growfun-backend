from rest_framework import serializers
from .models import DemoAccount, DemoInvestment, DemoTransaction

class DemoAccountSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = DemoAccount
        fields = ['id', 'user_email', 'balance', 'is_active', 'created_at', 'updated_at']

class DemoInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoInvestment
        fields = [
            'id', 'investment_type', 'asset_name', 'amount', 'quantity', 
            'price_at_purchase', 'monthly_rate', 'duration_months', 
            'status', 'created_at', 'updated_at'
        ]

class DemoTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'asset', 'quantity', 
            'price', 'status', 'description', 'created_at'
        ]