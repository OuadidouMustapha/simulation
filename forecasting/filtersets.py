# from django_select2 import forms as select2
# from django_select2.forms import Select2Widget
from datetime import datetime
import django_filters
from .models import Version, VersionDetail, Forecast
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

class VersionDetailFilter(django_filters.FilterSet):
    # circuit = django_filters.ModelChoiceFilter(
    #     queryset=Circuit.objects.all(),
    #     widget=Select2Widget
    # )

    version__version_date = django_filters.ChoiceFilter(
        label='Version date',
        choices=[[obj['version_date'], obj['version_date']]
                 for obj in Version.objects.values('version_date').distinct()],
    )

    class Meta:
        model = VersionDetail
        fields = ['product', 'circuit', 'product__abc_segmentation',
                  'product__fmr_segmentation', 'version__version_date', 'status']
