# Generated by Django 3.0.5 on 2020-04-18 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sorterbot_control_panel', '0005_log'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='arm',
            new_name='arm_id',
        ),
        migrations.RenameField(
            model_name='log',
            old_name='session',
            new_name='session_id',
        ),
    ]
