# Generated by Django 3.0.5 on 2020-05-17 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200509_2104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='session_id',
        ),
        migrations.AddField(
            model_name='session',
            name='session_started',
            field=models.DateTimeField(default='2000-05-16 00:00'),
            preserve_default=False,
        ),
    ]
