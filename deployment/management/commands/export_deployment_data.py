from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from deployment.models import TruckCategory, TruckAvailability
from inventory.models import StockCheck
from stock.models import Product
from forecasting.models import Forecast, Version
from django_pandas.io import read_frame


class Command(BaseCommand):
    help = "Export data used to calculate deployment in a csv format."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            help='Wipe existing data from the database before loading fixtures.',
            action='store_true',
            default=False,
        )

    def handle(self, *args, **options):
        version_id = 22
        check_date = '2021-01-25'

        # Get queries
        product_qs = Product.objects.all()

        forecast_qs = Forecast.objects.filter(version__id=version_id)
        forecast_qs = forecast_qs.values(
            'id', 'forecast_date', 'forecasted_quantity', 'edited_forecasted_quantity', 'product__id', 'circuit__id', 'customer__id', 'customer__warehouse__id', 'version__id')
            
        stockcheck_qs = StockCheck.objects.filter(check_date=check_date).values(
            'id', 'product__id', 'check_date', 'warehouse__id', 'warehouse__warehouse_type', 'quantity')

        truckavailability_qs = TruckAvailability.objects.values(
            'id', 'warehouse__id', 'available_truck', 'category__capacity', 'category__cost', 'category__truck_type')
        # Convert to csv
        product_df = read_frame(product_qs).to_csv('tmp/product_df.csv')
        forecast_df = read_frame(forecast_qs).to_csv('tmp/forecast_df.csv')
        stockcheck_df = read_frame(stockcheck_qs).to_csv('tmp/stockcheck_df.csv')
        truckavailability_df = read_frame(
            truckavailability_qs).to_csv('tmp/truckavailability_df.csv')
        # Output success message
        self.stdout.write(self.style.SUCCESS('CSV files generated successfully'))

