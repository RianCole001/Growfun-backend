# Generated migration for Trade models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('asset', models.CharField(choices=[('gold', 'Gold'), ('usdt', 'USDT')], max_length=10)),
                ('trade_type', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell')], max_length=10)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('cancelled', 'Cancelled'), ('stop_loss_hit', 'Stop Loss Hit'), ('take_profit_hit', 'Take Profit Hit'), ('expired', 'Expired')], default='open', max_length=20)),
                ('entry_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('current_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('exit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=12)),
                ('stop_loss', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('take_profit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('timeframe', models.CharField(blank=True, choices=[('1m', '1 Minute'), ('5m', '5 Minutes'), ('15m', '15 Minutes'), ('30m', '30 Minutes'), ('1h', '1 Hour'), ('4h', '4 Hours'), ('1d', '1 Day')], max_length=10, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('profit_loss', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('profit_loss_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Trade',
                'verbose_name_plural': 'Trades',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TradeHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('asset', models.CharField(max_length=10)),
                ('trade_type', models.CharField(max_length=10)),
                ('entry_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('exit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=12)),
                ('profit_loss', models.DecimalField(decimal_places=2, max_digits=12)),
                ('profit_loss_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('close_reason', models.CharField(max_length=50)),
                ('opened_at', models.DateTimeField()),
                ('closed_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Trade History',
                'verbose_name_plural': 'Trade Histories',
                'ordering': ['-closed_at'],
            },
        ),
    ]
