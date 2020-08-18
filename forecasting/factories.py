import factory
from faker import Faker

from .models import StockForecast
import pytz


class StockForecastFactory(factory.django.DjangoModelFactory):
    stock = factory.SubFactory('stock.StockFactory')
    customer = factory.SubFactory('stock.CustomerFactory')
    circuit = factory.SubFactory('stock.CircuitFactory')
    forecast_date = factory.Faker(
        'date_time_between',
        start_date='-2y',
        end_date='+60d',
        tzinfo=pytz.utc
    )
    forecasted_quantity = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )

    class Meta:
        model = StockForecast
        django_get_or_create = ('stock', 'forecast_date', 'circuit')
