# Generated by Django 3.0.5 on 2020-04-17 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sorterbot_control_panel', '0003_auto_20200417_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_id',
            field=models.CharField(max_length=40),
        ),
    ]
