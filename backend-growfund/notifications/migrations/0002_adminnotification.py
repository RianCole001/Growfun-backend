# Generated migration for AdminNotification model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')], default='info', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')], default='normal', max_length=20)),
                ('target', models.CharField(choices=[('all', 'All Users'), ('verified_users', 'Verified Users'), ('specific_users', 'Specific Users')], default='all', max_length=20)),
                ('target_users', models.TextField(blank=True, help_text='Comma-separated emails for specific_users target')),
                ('sent_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('failed', 'Failed')], default='sent', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='adminnotification',
            index=models.Index(fields=['-created_at'], name='notificatio_created_idx'),
        ),
        migrations.AddIndex(
            model_name='adminnotification',
            index=models.Index(fields=['status'], name='notificatio_status_idx'),
        ),
    ]
