# Generated migration for Referral model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reward_amount', models.DecimalField(decimal_places=2, default=5.0, max_digits=12)),
                ('reward_claimed', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('active', 'Active'), ('inactive', 'Inactive')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('referred_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referral_from', to=settings.AUTH_USER_MODEL)),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals_made', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Referral',
                'verbose_name_plural': 'Referrals',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='referral',
            unique_together={('referrer', 'referred_user')},
        ),
    ]
