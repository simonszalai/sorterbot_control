# Generated by Django 3.0.5 on 2020-04-16 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sorterbot_control_panel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ui',
            name='start_session',
            field=models.BooleanField(default=False),
        ),
    ]
