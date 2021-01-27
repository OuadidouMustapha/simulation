import random
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from forecasting.models import PlannedOrder
from stock.models import Product, Customer
from datetime import date, datetime


class Command(BaseCommand):
    # TODO The command should be running each year 1st December
    help = "Generate targe table for all {products, circuits} of selected year"

    def add_arguments(self, parser):
        parser.add_argument(
            '-y', '--year',
            type=int,
            help='Manually select the year of the target to be generated.',
        )

    def handle(self, *args, **kwargs):
        _all_products = list(Product.objects.values_list('id', flat=True))
        _all_customer = list(Customer.objects.values_list('id', flat=True))
        
        year = kwargs['year'] if kwargs['year'] else date.today().year

        planned_orders = []

        for p in _all_products:
            for c in random.sample(_all_customer, 1000):
                for month in range(1,13, 2):
                    planned_orders.append(
                        PlannedOrder(
                            product_id=p,
                            customer_id=c,
                            planned_at=datetime(year, month, 1),
                            planned_quantity=random.randint(10000,100000),
                        )
                    )
                    self.stdout.write(
                        'Append instance with p,c = %s, %s' % (p, c))

        PlannedOrder.objects.bulk_create(planned_orders)
        self.stdout.write(self.style.SUCCESS(
            'Planned orders for year %s are created successfully!' % (year)))
