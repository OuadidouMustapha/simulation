# Generated by Django 3.0.2 on 2021-01-14 10:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stock', '0002_auto_20210106_1318'),
        ('forecasting', '0006_auto_20210113_1221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='version',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='version',
            name='created_by',
        ),
        migrations.AlterField(
            model_name='version',
            name='status',
            field=models.CharField(choices=[('Created', 'Created'), ('Active', 'Active'), ('Archived', 'Archived')], default='Created', max_length=32),
        ),
        migrations.CreateModel(
            name='VersionDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Auto Generated', 'Auto Generated'), ('Confirmed', 'Confirmed'), ('Sent For Review', 'Sent For Review'), ('Validated', 'Validated')], default='Auto Generated', max_length=32)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_versions', to=settings.AUTH_USER_MODEL)),
                ('circuit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stock.Circuit')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_versions', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stock.Product')),
                ('version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='forecasting.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
