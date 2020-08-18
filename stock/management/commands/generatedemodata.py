from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from stock.factories import ProductCategoryFactory
from stock.models import (ProductCategory, Product, Warehouse, Stock, StockPolicy,
                           StockControl, Customer, Order, OrderDetail, Sale, SaleDetail, Circuit)
from forecasting.models import StockForecast

'''
Command 'generatedemodata' parameters file
'''

class Command(BaseCommand):
    help = "Populate the app with sample data. Generates products and product_category."


    def _load_fixtures(self):
        # ProductCategoryFactory.create_batch(size=10)
        # WarehouseFactory.create_batch(size=3)
        cat = ProductCategory.objects.create(reference='cat_parent', name='category_parent')
        ProductCategoryFactory.create_batch(
            size=3, create_products=3, parent=cat)  

        # # Create `ProductCategory`
        # parent_1 = ProductCategoryFactory.create(
        #     reference='parent_1')
        # parent_2 = ProductCategoryFactory.create(
        #     reference='parent_2')
        # parent_3 = ProductCategoryFactory.create(
        #     reference='parent_3')
        # parent_1_1 = ProductCategoryFactory.create(
        #     reference='parent_1_1',
        #     parent=parent_1
        # )
        # parent_1_2 = ProductCategoryFactory.create(
        #     reference='parent_1_2',
        #     parent=parent_1
        # )

    def _clean_db(self):
        for model in [
                ProductCategory, Product, Warehouse, Stock, StockPolicy,
                StockControl, Customer, Order, OrderDetail, Sale, SaleDetail, StockForecast, Circuit
            ]:
            model.objects.all().delete()

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options['clean']:
                    self._clean_db()
                self._load_fixtures()

        except Exception as e:
            raise CommandError(
                f"{e}\n\nTransaction was not committed due to the above exception.")


    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            help='Wipe existing data from the database before loading fixtures.',
            action='store_true',
            default=False,
        )



