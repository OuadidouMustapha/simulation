import factory
from faker import Faker

from .models import TruckCategory, TruckAvailability
from stock.models import Warehouse
from forecasting.factories import ForecastFactory
import random
import pytz

class TruckCategoryFactory(factory.django.DjangoModelFactory):
    reference = factory.Sequence(lambda n: 'tr-cat-00%d' % n)
    capacity = factory.Faker('random_number', digits=2, fix_len=False)
    cost = factory.Faker(
        'pydecimal',
        left_digits=None,
        right_digits=None,
        positive=True,
        min_value=10,
        max_value=500
    )
    truck_type = factory.LazyFunction(lambda: random.choice([1, 2, 3]))

    class Meta:
        model = TruckCategory

    @factory.post_generation
    def create_truck_availability(self, create, how_many, **kwargs):
        at_least = 1
        if not create:
            return
        for n in range(how_many or at_least):
            _all_warehouses_objects = Warehouse.objects.all()
            for w_obj in _all_warehouses_objects:
                TruckAvailabilityFactory(category=self, warehouse=w_obj)



class TruckAvailabilityFactory(factory.django.DjangoModelFactory):

    category = factory.SubFactory(TruckCategoryFactory)
    warehouse = factory.SubFactory(TruckCategoryFactory)
    reference = factory.Sequence(lambda n: 'trTypW-num%d' % n)
    available_truck = factory.LazyFunction(lambda: random.randint(1, 30))

    class Meta:
        model = TruckAvailability
