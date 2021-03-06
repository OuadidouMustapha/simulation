# Generated by Django 3.0.2 on 2021-01-12 08:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0002_forecast_edited_forecasted_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventdetail',
            old_name='date',
            new_name='end_date',
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('Promo', 'Promo'), ('Action Marketing', 'Action Marketing'), ('Holiday', 'Holiday')], default='Promo', max_length=32),
        ),
        migrations.AddField(
            model_name='eventdetail',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
