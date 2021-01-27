import random
import numpy as np
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from stock.models import Warehouse, Customer
from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
import pandas as pd


class Command(BaseCommand):
    help = "Generate customer missing data."
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '-y', '--year',
    #         type=int,
    #         help='Manually select the year of the version to be generated.',
    #         # action='store_true', # True if year is provided
    #         # default=False,
    #     )
    #     parser.add_argument(
    #         '-m', '--month',
    #         type=int,
    #         help='Manually select the month of the version to be generated.',
    #     )

    def handle(self, *args, **kwargs):
        warehouse_ids = list(Warehouse.objects.filter(
            warehouse_type='RDC').values_list('id', flat=True))
        # Get the queryset
        customer_qs = Customer.objects.all()

        self.stdout.write('Updating database...')
        # Bulk update classification in database
        customer_objects = [
            Customer(
                id=c.id,
                warehouse_id=random.choice(warehouse_ids),
            )
            for c in customer_qs.iterator(chunk_size=1000)
        ]
        self.stdout.write('Bulk update...')
        Customer.objects.bulk_update(
            customer_objects, ['warehouse_id'], batch_size=1000)

        # Output success message
        self.stdout.write(self.style.SUCCESS(
            'All customers are linked to a warehouse randomly'))
