# Generated by Django 3.0.2 on 2021-01-22 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_warehouse_shipping_capacity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouse',
            name='available_trucks',
        ),
        migrations.AddField(
            model_name='warehouse',
            name='warehouse_type',
            field=models.CharField(choices=[('RDC', 'RDC'), ('CDC', 'CDC')], default='RDC', max_length=32),
        ),
    ]
