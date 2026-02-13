# Generated migration for CapitalInvestmentPlan model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CapitalInvestmentPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('plan_type', models.CharField(choices=[('basic', 'Basic'), ('standard', 'Standard'), ('advance', 'Advance')], max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('initial_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('period_months', models.IntegerField()),
                ('growth_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('total_return', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('final_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('monthly_growth', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investment_plans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Capital Investment Plan',
                'verbose_name_plural': 'Capital Investment Plans',
                'ordering': ['-created_at'],
            },
        ),
    ]
