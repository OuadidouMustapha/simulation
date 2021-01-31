from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from forecasting.models import Version, Forecast
from stock.models import OrderDetail
from datetime import date, datetime
from django_pandas.io import read_frame
import pandas as pd

class Command(BaseCommand):
    # TODO The command should be running each year 1st December
    help = "Generate forecast version table of upcomming year with attributes (reference, year, month, type)."

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--clean',
            help='Wipe existing data from the database before creating new ones.',
            action='store_true',
            default=False,
        )

    def handle(self, *args, **kwargs):
        # Create a version
        version_obj, created = Version.objects.get_or_create(
            reference='200101_demo',
            version_date=datetime(2020, 1, 1)
        )
        if kwargs['clean'] and not created:
            # Delete old data
            self.stdout.write('Deleting existing forecast...')
            forecast_objs = Forecast.objects.filter(version=version_obj)
            forecast_objs.delete()
            self.stdout.write('Existing forecast deleted')
            
        # Get past orders
        order_qs = OrderDetail.objects.values(
            'warehouse__id', 'product__id', 'category__id', 'circuit__id', 'customer__id', 'ordered_quantity', 'order__ordered_at')
        order_df = read_frame(order_qs)
        order_df['ordered_quantity'] = order_df['ordered_quantity'].astype('int32')
        self.stdout.write('Version object created')

        # Create forecast dataframe
        forecast_df = order_df.rename(columns={
            'ordered_quantity': 'forecasted_quantity',
            'order__ordered_at': 'forecast_date',
        })
        # Generate different values based on defined rate
        forecast_df['forecasted_quantity'] = pd.to_numeric(
            forecast_df['forecasted_quantity'] * 0.7)
        forecast_df['edited_forecasted_quantity'] = pd.to_numeric(
            forecast_df['forecasted_quantity'] * 1.3)

        self.stdout.write('Creating forecasts...')
        forecast_objs= [
            Forecast(
                warehouse_id=row['warehouse__id'],
                product_id=row['product__id'],
                category_id=row['category__id'],
                circuit_id=row['circuit__id'],
                customer_id=row['customer__id'],
                version_id=version_obj.id,
                forecast_date=row['forecast_date'],
                forecasted_quantity=row['forecasted_quantity'],
                edited_forecasted_quantity=row['edited_forecasted_quantity'],
            ) for i, row in forecast_df.iterrows()
        ]
        Forecast.objects.bulk_create(forecast_objs)

        self.stdout.write(self.style.SUCCESS(
            'Forecasts created successfully' ))
