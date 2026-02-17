from rest_framework import serializers
from .models import PlatformSettings, SettingsHistory
from decimal import Decimal


class PlatformSettingsSerializer(serializers.ModelSerializer):
    """Serializer for platform settings with camelCase field names"""
    
    platformName = serializers.CharField(source='platform_name')
    platformEmail = serializers.EmailField(source='platform_email')
    minDeposit = serializers.DecimalField(source='min_deposit', max_digits=12, decimal_places=2)
    maxDeposit = serializers.DecimalField(source='max_deposit', max_digits=12, decimal_places=2)
    minWithdrawal = serializers.DecimalField(source='min_withdrawal', max_digits=12, decimal_places=2)
    maxWithdrawal = serializers.DecimalField(source='max_withdrawal', max_digits=12, decimal_places=2)
    depositFee = serializers.DecimalField(source='deposit_fee', max_digits=5, decimal_places=2)
    withdrawalFee = serializers.DecimalField(source='withdrawal_fee', max_digits=5, decimal_places=2)
    referralBonus = serializers.DecimalField(source='referral_bonus', max_digits=12, decimal_places=2)
    maintenanceMode = serializers.BooleanField(source='maintenance_mode')
    emailNotifications = serializers.BooleanField(source='email_notifications')
    smsNotifications = serializers.BooleanField(source='sms_notifications')
    autoApproveDeposits = serializers.BooleanField(source='auto_approve_deposits')
    autoApproveWithdrawals = serializers.BooleanField(source='auto_approve_withdrawals')
    autoApproveDepositLimit = serializers.DecimalField(
        source='auto_approve_deposit_limit', 
        max_digits=12, 
        decimal_places=2,
        required=False
    )
    autoApproveWithdrawalLimit = serializers.DecimalField(
        source='auto_approve_withdrawal_limit', 
        max_digits=12, 
        decimal_places=2,
        required=False
    )
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    updatedBy = serializers.SerializerMethodField()
    
    class Meta:
        model = PlatformSettings
        fields = [
            'platformName', 'platformEmail', 'minDeposit', 'maxDeposit',
            'minWithdrawal', 'maxWithdrawal', 'depositFee', 'withdrawalFee',
            'referralBonus', 'maintenanceMode', 'emailNotifications',
            'smsNotifications', 'autoApproveDeposits', 'autoApproveWithdrawals',
            'autoApproveDepositLimit', 'autoApproveWithdrawalLimit',
            'updatedAt', 'updatedBy'
        ]
    
    def get_updatedBy(self, obj):
        if obj.updated_by:
            return obj.updated_by.email
        return None
    
    def validate(self, data):
        """Validate settings data"""
        errors = {}
        
        # Get values (use existing if not provided)
        min_deposit = data.get('min_deposit', self.instance.min_deposit if self.instance else Decimal('100'))
        max_deposit = data.get('max_deposit', self.instance.max_deposit if self.instance else Decimal('100000'))
        min_withdrawal = data.get('min_withdrawal', self.instance.min_withdrawal if self.instance else Decimal('50'))
        max_withdrawal = data.get('max_withdrawal', self.instance.max_withdrawal if self.instance else Decimal('50000'))
        
        # Validate deposit limits
        if min_deposit >= max_deposit:
            errors['minDeposit'] = 'Minimum deposit must be less than maximum deposit'
        
        # Validate withdrawal limits
        if min_withdrawal >= max_withdrawal:
            errors['minWithdrawal'] = 'Minimum withdrawal must be less than maximum withdrawal'
        
        # Validate fees
        deposit_fee = data.get('deposit_fee', Decimal('0'))
        withdrawal_fee = data.get('withdrawal_fee', Decimal('2'))
        
        if deposit_fee < 0 or deposit_fee > 100:
            errors['depositFee'] = 'Deposit fee must be between 0 and 100'
        
        if withdrawal_fee < 0 or withdrawal_fee > 100:
            errors['withdrawalFee'] = 'Withdrawal fee must be between 0 and 100'
        
        # Validate auto-approve limits
        auto_deposit_limit = data.get('auto_approve_deposit_limit', self.instance.auto_approve_deposit_limit if self.instance else Decimal('1000'))
        auto_withdrawal_limit = data.get('auto_approve_withdrawal_limit', self.instance.auto_approve_withdrawal_limit if self.instance else Decimal('500'))
        
        if auto_deposit_limit > max_deposit:
            errors['autoApproveDepositLimit'] = 'Auto-approve limit cannot exceed maximum deposit'
        
        if auto_withdrawal_limit > max_withdrawal:
            errors['autoApproveWithdrawalLimit'] = 'Auto-approve limit cannot exceed maximum withdrawal'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class SettingsHistorySerializer(serializers.ModelSerializer):
    """Serializer for settings history"""
    
    changedBy = serializers.SerializerMethodField()
    changedAt = serializers.DateTimeField(source='changed_at')
    settingName = serializers.CharField(source='setting_name')
    oldValue = serializers.CharField(source='old_value')
    newValue = serializers.CharField(source='new_value')
    
    class Meta:
        model = SettingsHistory
        fields = ['id', 'settingName', 'oldValue', 'newValue', 'changedBy', 'changedAt']
    
    def get_changedBy(self, obj):
        if obj.changed_by:
            return obj.changed_by.email
        return None
