# Generated migration for platform settings

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_name', models.CharField(default='GrowFund', help_text='Platform name displayed to users', max_length=100)),
                ('platform_email', models.EmailField(default='support@growfund.com', help_text='Support email address', max_length=254)),
                ('maintenance_mode', models.BooleanField(default=False, help_text='Enable to block non-admin access')),
                ('min_deposit', models.DecimalField(decimal_places=2, default=Decimal('100.00'), help_text='Minimum deposit amount', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('max_deposit', models.DecimalField(decimal_places=2, default=Decimal('100000.00'), help_text='Maximum deposit amount', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('min_withdrawal', models.DecimalField(decimal_places=2, default=Decimal('50.00'), help_text='Minimum withdrawal amount', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('max_withdrawal', models.DecimalField(decimal_places=2, default=Decimal('50000.00'), help_text='Maximum withdrawal amount', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('deposit_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Deposit fee percentage (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))])),
                ('withdrawal_fee', models.DecimalField(decimal_places=2, default=Decimal('2.00'), help_text='Withdrawal fee percentage (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))])),
                ('auto_approve_deposits', models.BooleanField(default=False, help_text='Auto-approve deposits within limit')),
                ('auto_approve_withdrawals', models.BooleanField(default=False, help_text='Auto-approve withdrawals within limit')),
                ('auto_approve_deposit_limit', models.DecimalField(decimal_places=2, default=Decimal('1000.00'), help_text='Auto-approve deposits up to this amount', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('auto_approve_withdrawal_limit', models.DecimalField(decimal_places=2, default=Decimal('500.00'), help_text='Auto-approve withdrawals up to this amount', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('email_notifications', models.BooleanField(default=True, help_text='Enable email notifications')),
                ('sms_notifications', models.BooleanField(default=False, help_text='Enable SMS notifications')),
                ('referral_bonus', models.DecimalField(decimal_places=2, default=Decimal('50.00'), help_text='Bonus amount for successful referrals', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='settings_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Platform Settings',
                'verbose_name_plural': 'Platform Settings',
            },
        ),
        migrations.CreateModel(
            name='SettingsHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('setting_name', models.CharField(max_length=100)),
                ('old_value', models.TextField(blank=True, null=True)),
                ('new_value', models.TextField()),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Settings History',
                'verbose_name_plural': 'Settings History',
                'ordering': ['-changed_at'],
            },
        ),
    ]
