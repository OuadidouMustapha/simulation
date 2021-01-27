import random
import numpy as np
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from stock.models import Warehouse, Product
from inventory.models import StockCheck
from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
import pandas as pd


class Command(BaseCommand):
    help = "Generate demo data for stockcheck model using exiting warehouse and product models."
    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--check_date',
            type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
            help='Manually specify the check date.',
        )
        parser.add_argument(
            '-c', '--clean',
            help='Wipe existing data from the database before generating new data.',
            action='store_true',
            default=False,
        )
        # )

    def handle(self, *args, **kwargs):
        # if clean parameter is provided then delete data before proceeding
        if kwargs['clean']:
            StockCheck.objects.all().delete()
        # Get date parameter or define one
        if kwargs['check_date']:
            check_date = kwargs['check_date']
        else:
            check_date = datetime.today()

        # Get querysets
        _rdc_warehouses_id = Warehouse.objects.filter(warehouse_type='RDC')
        _cdc_warehouses_id = Warehouse.objects.filter(warehouse_type='CDC')
        _products_id = Product.objects.all()

        self.stdout.write('Generating data...')

        _stockcheck_objects = []
        for p in _products_id:
            # Generate data for rdc warehouses
            for w in _rdc_warehouses_id:
                stockcheck_rdc_objects = [
                    StockCheck(
                        product=p,
                        warehouse=w,
                        check_date=check_date,
                        quantity=random.randint(0, 500),
                    )
                ]
                _stockcheck_objects.extend(stockcheck_rdc_objects)

            # Generate data for cdc warehouses
            for w in _cdc_warehouses_id:
                stockcheck_cdc_objects = [
                    StockCheck(
                        product=p,
                        warehouse=w,
                        check_date=check_date,
                        quantity=random.randint(1000000, 1000000),
                    )
                ]
                _stockcheck_objects.extend(stockcheck_cdc_objects)

        # Bulk update in database
        self.stdout.write('Updating database...')
        StockCheck.objects.bulk_create(_stockcheck_objects)

        # Output success message
        self.stdout.write(self.style.SUCCESS('Data generated successfully'))
    
    

