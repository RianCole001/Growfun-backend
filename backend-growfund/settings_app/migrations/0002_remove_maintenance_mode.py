# Generated migration to remove maintenance_mode field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='platformsettings',
            name='maintenance_mode',
        ),
    ]
