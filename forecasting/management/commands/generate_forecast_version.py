from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from forecasting.models import Version
from datetime import date, datetime

class Command(BaseCommand):
    # TODO The command should be running each year 1st December
    help = "Generate forecast version table of upcomming year with attributes (reference, year, month, type)."

    def add_arguments(self, parser):
        parser.add_argument(
            '-y', '--year',
            type=int,
            help='Manually select the year of the version to be generated.',
            # action='store_true', # True if year is provided
            # default=False,
        )
        parser.add_argument(
            '-m', '--month',
            type=int,
            help='Manually select the month of the version to be generated.',
        )

    def handle(self, *args, **kwargs):
        # Get forecast_type choices from model 
        forecast_types = Version._meta.get_field('forecast_type').choices

        # Get year/month if provided else get the current year and the upcomming month
        if kwargs['year']:
            year = kwargs['year']
        else:
            year = date.today().year

        if kwargs['month']:
            month = kwargs['month']
        else:
            month = date.today().month + 1
        


        versions = []
        # Range of 12 months
        for forecast_type in forecast_types:
            # for month in range(1, 13):
            reference = '{}{}_{}'.format(year, month, forecast_type[0])
            
            versions.append(
                Version(
                    reference=reference,
                    year=year,
                    month=month,
                    version_date=datetime(year, month, 1),
                    forecast_type=forecast_type[0],
                )
            )

            self.stdout.write('Append instance with reference: %s' % (reference))


        Version.objects.bulk_create(versions)
        self.stdout.write(self.style.SUCCESS(
            'The version for %s-%s is created successfully!' % (month, year)))


        # try:
        #     with transaction.atomic():

        # except Exception as e:
        #     raise CommandError(
        #         f"{e}\n\nTransaction was not committed due to the above exception.")

    # def _load_fixtures(self):

    #     # cat = ProductCategory.objects.create(reference='cat_parent', name='category_parent')
    #     # ProductCategoryFactory.create_batch(
    #     #     size=3, create_products=3, parent=cat)  

        





