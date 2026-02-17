# Generated migration for admin crypto prices

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investments', '0002_capital_investment_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminCryptoPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coin', models.CharField(help_text='Coin symbol (e.g., EXACOIN, BTC)', max_length=10, unique=True)),
                ('name', models.CharField(default='', help_text='Full coin name', max_length=50)),
                ('buy_price', models.DecimalField(decimal_places=2, help_text='Price users pay to buy', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('sell_price', models.DecimalField(decimal_places=2, help_text='Price users receive when selling', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('change_24h', models.DecimalField(decimal_places=4, default=0, help_text='24-hour price change percentage', max_digits=8)),
                ('change_7d', models.DecimalField(decimal_places=4, default=0, help_text='7-day price change percentage', max_digits=8)),
                ('change_30d', models.DecimalField(decimal_places=4, default=0, help_text='30-day price change percentage', max_digits=8)),
                ('is_active', models.BooleanField(default=True, help_text='Enable/disable trading for this coin')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='price_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Admin Crypto Price',
                'verbose_name_plural': 'Admin Crypto Prices',
                'ordering': ['coin'],
            },
        ),
        migrations.CreateModel(
            name='CryptoPriceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coin', models.CharField(db_index=True, max_length=10)),
                ('buy_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('sell_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('change_24h', models.DecimalField(decimal_places=4, default=0, max_digits=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Crypto Price History',
                'verbose_name_plural': 'Crypto Price History',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='admincryptoprice',
            index=models.Index(fields=['coin'], name='investments_coin_idx'),
        ),
        migrations.AddIndex(
            model_name='admincryptoprice',
            index=models.Index(fields=['is_active'], name='investments_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='cryptopricehistory',
            index=models.Index(fields=['coin', '-created_at'], name='investments_coin_created_idx'),
        ),
    ]