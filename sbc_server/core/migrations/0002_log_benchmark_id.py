# Generated by Django 3.0.5 on 2020-05-03 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='benchmark_id',
            field=models.FloatField(default=0),
        ),
    ]
