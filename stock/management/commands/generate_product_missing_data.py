import numpy as np
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from stock.models import DeliveryDetail, Product, ProductCategory
from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
import pandas as pd


class Command(BaseCommand):
    help = "Generate product missing data."
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
        # Get the queryset
        product_qs = Product.objects.values('id', 'weight', 'volume', 'pallet_size', 'product_type')
        category_objects = list(ProductCategory.objects.values_list('id', flat=True))

        # Convert qs to dataframe
        product_df = read_frame(product_qs)
        
        # Generate missing data for selected columns
        df_length = product_df.shape[0]
        product_df['weight'] = np.random.randint(100, 1000, df_length)
        product_df['volume'] = np.random.randint(10, 100, df_length)
        product_df['profit_margin'] = np.random.randint(1, 10, df_length)
        product_df['pallet_size'] = np.random.randint(10, 50, df_length)
        product_df['unit_size'] = (product_df['pallet_size'] // 10) + 1
        product_df['product_type'] = np.random.choice(
            ['Food', 'Non Food', None], df_length, p=[0.5, 0.4, 0.1])
        product_df['category_id'] = np.random.choice(category_objects, df_length)


        self.stdout.write('Updating database...')
        # Bulk update classification in database
        product_objects = [
            Product(
                id=row['id'],
                weight=row['weight'],
                volume=row['volume'],
                profit_margin=row['profit_margin'],
                unit_size=row['unit_size'],
                pallet_size=row['pallet_size'],
                product_type=row['product_type'],
                category_id=row['category_id'],
            )
            for i, row in product_df.iterrows()
        ]
        Product.objects.bulk_update(
            product_objects, ['weight', 'volume', 'profit_margin',
                              'unit_size', 'pallet_size', 'product_type', 'category_id'])

        # Output success message
        self.stdout.write(self.style.SUCCESS('Products have been updated'))
    
    

