from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0001_initial'),
    ]

    operations = [
        # Add current_price to DemoInvestment for live portfolio value
        migrations.AddField(
            model_name='demoinvestment',
            name='current_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        # Expand DemoTransaction type choices to include binary trade events
        migrations.AlterField(
            model_name='demotransaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('deposit', 'Deposit'),
                    ('withdrawal', 'Withdrawal'),
                    ('crypto_buy', 'Crypto Purchase'),
                    ('crypto_sell', 'Crypto Sale'),
                    ('investment', 'Investment'),
                    ('return', 'Investment Return'),
                    ('binary_trade_open', 'Binary Trade Open'),
                    ('binary_trade_win', 'Binary Trade Win'),
                    ('binary_trade_loss', 'Binary Trade Loss'),
                ],
                max_length=20,
            ),
        ),
    ]
