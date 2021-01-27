from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from deployment.factories import TruckCategoryFactory, TruckAvailabilityFactory
from deployment.models import TruckCategory, TruckAvailability
from stock.models import Warehouse
from forecasting.models import Forecast


class Command(BaseCommand):
    help = "Generate truck categories and availability for existing warehouses."


    def _load_fixtures(self):
        TruckCategoryFactory.create_batch(
            size=3, create_truck_availability=1)

    def _clean_db(self):
        for model in [
                TruckCategory, TruckAvailability
            ]:
            model.objects.all().delete()

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options['clean']:
                    self._clean_db()
                self._load_fixtures()
                self.stdout.write(self.style.SUCCESS(
                    'Trucks created successfully!'))

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



