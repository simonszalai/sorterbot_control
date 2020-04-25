# Generated by Django 3.0.5 on 2020-04-18 15:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sorterbot_control_panel', '0007_auto_20200418_1638'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='step',
            new_name='log_type',
        ),
        migrations.AlterField(
            model_name='log',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sorterbot_control_panel.Session'),
        ),
    ]