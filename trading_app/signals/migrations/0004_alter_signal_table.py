# Generated by Django 5.0.6 on 2024-06-10 21:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0003_alter_signal_options_alter_signal_amount_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='signal',
            table='signals_signal',
        ),
    ]