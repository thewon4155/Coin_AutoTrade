# Generated by Django 5.0.6 on 2024-06-10 21:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0004_alter_signal_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='signal',
            options={'managed': False},
        ),
    ]