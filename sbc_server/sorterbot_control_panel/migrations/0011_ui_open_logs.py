# Generated by Django 3.0.5 on 2020-04-20 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sorterbot_control_panel', '0010_session_enabled_log_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='ui',
            name='open_logs',
            field=models.CharField(default='', max_length=40),
        ),
    ]