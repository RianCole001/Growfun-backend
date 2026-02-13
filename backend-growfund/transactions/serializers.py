from rest_framework import serializers
from .models import Transaction, MoMoPayment

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'payment_method', 'amount', 'fee',
            'net_amount', 'status', 'reference', 'external_reference',
            'phone_number', 'description', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'reference', 'fee', 'net_amount', 'status', 'created_at', 'updated_at', 'completed_at']


class MoMoDepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=100)
    phone_number = serializers.CharField(max_length=20)
    
    def validate_phone_number(self, value):
        # Basic phone number validation
        cleaned = value.replace('+', '').replace(' ', '').replace('-', '')
        if not cleaned.isdigit():
            raise serializers.ValidationError("Invalid phone number format")
        if len(cleaned) < 9 or len(cleaned) > 15:
            raise serializers.ValidationError("Phone number must be between 9 and 15 digits")
        return value


class MoMoWithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=50)
    phone_number = serializers.CharField(max_length=20)
    
    def validate_phone_number(self, value):
        cleaned = value.replace('+', '').replace(' ', '').replace('-', '')
        if not cleaned.isdigit():
            raise serializers.ValidationError("Invalid phone number format")
        if len(cleaned) < 9 or len(cleaned) > 15:
            raise serializers.ValidationError("Phone number must be between 9 and 15 digits")
        return value
    
    def validate_amount(self, value):
        user = self.context['request'].user
        if value > user.balance:
            raise serializers.ValidationError("Insufficient balance")
        return value


class CheckPaymentStatusSerializer(serializers.Serializer):
    reference_id = serializers.CharField(max_length=100)
