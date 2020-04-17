# Generated by Django 3.0.5 on 2020-04-17 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sorterbot_control_panel', '0002_ui_start_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='after_img_url',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='session',
            name='before_img_url',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='session',
            name='log_filenames',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='logs_base_url',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
