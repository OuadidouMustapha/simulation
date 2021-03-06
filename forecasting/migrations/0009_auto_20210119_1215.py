# Generated by Django 3.0.2 on 2021-01-19 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0008_auto_20210118_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventdetail',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eventdetail',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='versiondetail',
            name='status',
            field=models.CharField(choices=[('Auto Generated', 'Auto Generated'), ('Confirmed', 'Confirmed'), ('Sent For Review', 'Sent For Review'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Auto Generated', max_length=32),
        ),
    ]
