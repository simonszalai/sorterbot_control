# Generated by Django 3.0.5 on 2020-05-03 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_log_benchmark_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='benchmark_id',
            new_name='bm_id',
        ),
    ]
