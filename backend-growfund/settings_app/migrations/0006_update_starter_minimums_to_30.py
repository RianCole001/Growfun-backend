# Generated migration to update starter plan minimums to $30

from django.db import migrations
from decimal import Decimal


def update_minimums(apps, schema_editor):
    """Update minimum investment amounts for starter plans to $30"""
    PlatformSettings = apps.get_model('settings_app', 'PlatformSettings')
    
    # Get or create settings
    settings, created = PlatformSettings.objects.get_or_create(id=1)
    
    # Update starter plan minimums to $30
    settings.capital_basic_min = Decimal('30.00')
    settings.real_estate_starter_min = Decimal('30.00')
    settings.min_crypto_investment = Decimal('30.00')
    
    settings.save()
    
    print('✓ Updated minimum investments to $30 for starter plans')


def reverse_minimums(apps, schema_editor):
    """Reverse the changes (optional)"""
    PlatformSettings = apps.get_model('settings_app', 'PlatformSettings')
    
    settings = PlatformSettings.objects.get(id=1)
    settings.capital_basic_min = Decimal('30.00')  # Keep at 30
    settings.real_estate_starter_min = Decimal('1000.00')  # Original value
    settings.min_crypto_investment = Decimal('50.00')  # Original value
    settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ('settings_app', '0005_update_capital_plan_minimums'),
    ]

    operations = [
        migrations.RunPython(update_minimums, reverse_minimums),
    ]
