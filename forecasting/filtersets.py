import django_filters
from .models import Version, Forecast
from stock.models import Product

class VersionFilter(django_filters.FilterSet):
    reference = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Version
        fields = ['reference', 'year', 'month', 'is_budget', 'forecast_type', 'description']
         
class ForecastFilter(django_filters.FilterSet):
    # product = django_filters.ModelChoiceFilter(
    #     queryset=Product.objects.all())
    # forecast_date = django_filters.DateFilter(
    #     input_formats=['%Y-%m-%d'], lookup_expr='icontains')

    class Meta:
        model = Forecast
        fields = ['category', 'circuit']
         
