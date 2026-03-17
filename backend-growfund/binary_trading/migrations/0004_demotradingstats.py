from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('binary_trading', '0003_houseedgeconfig_atm_is_loss'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemoTradingStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_trades', models.IntegerField(default=0)),
                ('total_wins', models.IntegerField(default=0)),
                ('total_losses', models.IntegerField(default=0)),
                ('current_win_streak', models.IntegerField(default=0)),
                ('max_win_streak', models.IntegerField(default=0)),
                ('total_profit', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_loss', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('net_profit', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total_volume', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='demo_trading_stats',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
        ),
    ]
