from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('binary_trading', '0002_add_demo_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='houseedgeconfig',
            name='atm_is_loss',
            field=models.BooleanField(
                default=True,
                help_text='If final price == strike price, treat as loss (True) or refund stake (False)'
            ),
        ),
    ]
