import random
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from forecasting.models import Target
from stock.models import Product, Circuit
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
        _all_circuits = list(Circuit.objects.values_list('id', flat=True))
        
        year = kwargs['year'] if kwargs['year'] else date.today().year

        targets = []

        for p in _all_products:
            for c in _all_circuits:
                for month in range(1,13):
                    targets.append(
                        Target(
                            product_id=p,
                            circuit_id=c,
                            targeted_date=datetime(year, month, 1),
                            targeted_quantity=random.randint(10000,100000),
                        )
                    )
                    self.stdout.write(
                        'Append instance with p,c = %s, %s' % (p, c))

        Target.objects.bulk_create(targets)
        self.stdout.write(self.style.SUCCESS(
            'Targets for year %s are created successfully!' % (year)))
