# from django_select2 import forms as select2
# from django_select2.forms import Select2Widget
from datetime import datetime
import django_filters
from .models import Version, Forecast
from stock.models import Product, Circuit

class VersionFilter(django_filters.FilterSet):
    reference = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Version
        fields = ['reference', 'forecast_type', 'description']
         
class ForecastFilter(django_filters.FilterSet):
    # product = django_filters.ModelChoiceFilter(
    #     queryset=Product.objects.all())
    # forecast_date = django_filters.DateFilter(
    #     input_formats=['%Y-%m-%d'], lookup_expr='icontains')

    class Meta:
        model = Forecast
        fields = ['category', 'circuit']

class ProductToForecastFilter(django_filters.FilterSet):
    # circuit = django_filters.ModelChoiceFilter(
    #     queryset=Circuit.objects.all(),
    #     widget=Select2Widget
    # )
    # FIXME version__version_date filter does not work (maybe add 'contains' field?)
    version__version_date = django_filters.ModelChoiceFilter(
        label='Version date',
        queryset=Version.objects.values_list('version_date', flat=True).distinct(),
    )

    class Meta:
        model = Forecast
        fields = ['version', 'version__version_date', 'version__status',
                  'product__abc_segmentation', 'product__fmr_segmentation', 'circuit']
