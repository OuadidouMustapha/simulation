from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from stock.models import DeliveryDetail, Product
from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
import pandas as pd


class Command(BaseCommand):
    help = "Update ABC & FMR classification of all products using "

    


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
        def _abc_segmentation(perc):
            '''
            Creates the 3 classes A, B, and C based 
            on quantity percentages (A-80%, B-15%, C-5%)
            '''
            if perc > 0 and perc < 0.8:
                return 'A'
            elif perc >= 0.8 and perc < 0.95:
                return 'B'
            elif perc >= 0.95:
                return 'C'

        def _fmr_segmentation(perc):
            '''
            Creates the 3 classes F, M, and R based 
            on quantity percentages (F-80%, M-15%, R-5%)
            '''
            if perc > 0 and perc < 0.8:
                return 'F'
            elif perc >= 0.8 and perc < 0.95:
                return 'M'
            elif perc >= 0.95:
                return 'R'

        # Date range to consider for calculation (last delta years)
        _delta_years = 2
        start_date = datetime.today() - timedelta(days=_delta_years*365)

        # Get the queryset
        qs = DeliveryDetail.objects.filter(
            delivery__delivered_at__gte=start_date
        )
        qs = qs.values('product__id', 'delivered_quantity', 'unit_price')

        # Convert qs to dataframe
        df = read_frame(qs)
        # Format
        df = df.astype({'delivered_quantity': float,
                        'unit_price': float})
        # Add delivery count of each product (sum(1 for each product delivered))
        df['delivery_freq'] = 1
        # Group by product and aggregate
        df = df.groupby(['product__id']).agg({
            'delivered_quantity': 'sum',
            'unit_price': 'mean',
            'delivery_freq': 'sum',
        }).reset_index()

        # Create the column of the additive cost per product
        df['cost_product'] = df['unit_price'] * df['delivered_quantity']
        # Order by cumulative cost and create ABC segmentation
        df = df.sort_values(by=['cost_product'], ascending=False)
        df['cost_product_cum'] = df['cost_product'].cumsum()
        df['cost_product_sum'] = df['cost_product'].sum()
        df['cost_perc'] = df['cost_product_cum']/df['cost_product_sum']
        df['abc_segmentation'] = df['cost_perc'].apply(_abc_segmentation)
        # Order by cumulative cost and create FMR segmentation
        df = df.sort_values(by=['delivery_freq'], ascending=False)
        df['delivery_freq_cum'] = df['delivery_freq'].cumsum()
        df['delivery_freq_sum'] = df['delivery_freq'].sum()
        df['delivery_freq_perc'] = df['delivery_freq_cum']/df['delivery_freq_sum']
        df['fmr_segmentation'] = df['delivery_freq_perc'].apply(_fmr_segmentation)


        self.stdout.write('Updating database...')

        # Bulk update classification in database
        products = [
            Product(
                id=row['product__id'],
                abc_segmentation=row['abc_segmentation'],
                fmr_segmentation=row['fmr_segmentation'],
            )
            for i, row in df.iterrows()
        ]

        Product.objects.bulk_update(products, ['abc_segmentation', 'fmr_segmentation'])

        # Output success message
        self.stdout.write(self.style.SUCCESS('ABC & FMR segmentations have been updated'))
    
    

