from django_tables2 import tables, TemplateColumn, LinkColumn, CheckBoxColumn
from .models import Version, Forecast
from django_tables2.utils import A  # alias for Accessor
import datetime


class VersionTable(tables.Table):
    action = TemplateColumn(
        template_name='forecasting/tables/version_list_action_column.html',
        orderable=False)
    # delete = LinkColumn(
    #     'forecasting:version_list', 
    #     args=[A('id')], 
    #     attrs={
    #         'a': {'class': 'btn'}
    #     }
    # )

    # def render_month(self, value, column):
    #     now = datetime.datetime.now()

    #     if value == now.month:
    #         column.attrs = {'td': {'class': 'table-info'}}
    #     else:
    #         column.attrs = {'td': {}}
    #     return value

    class Meta:
        model = Version
        # template_name = "django_tables2/bootstrap.html"
        attrs = {'class': 'table table-sm table-hover table-responsive-md'}
        fields = ['reference', 'forecast_type', 'description', 'file_path', 'action']
        order_by = ['year', 'month']

class ForecastTable(tables.Table):
    action = TemplateColumn(
        template_name='forecasting/tables/forecast_list_action_column.html',
        orderable=False)

    class Meta:
        model = Forecast
        attrs = {'class': 'table table-sm table-hover table-responsive-md'}
        fields = ['product', 'circuit', 'version', 'forecast_date', 'forecasted_quantity', 'action']


class ProductToForecastTable(tables.Table):
    action = TemplateColumn(
        template_name='forecasting/tables/product_to_forecast_action_column.html',
        orderable=False)
    selection = CheckBoxColumn(
        accessor='product__id',
        attrs={'th__input': {'onclick': 'selectAllElements(this)'}},
        orderable=False
    )

    class Meta:
        model = Forecast
        attrs = {'class': 'table table-sm table-hover table-responsive-md'}
        fields = ['selection', 'product', 'circuit', 'version', 'product__abc_segmentation', 'product__fmr_segmentation',
                  'version__version_date', 'version__status', 'action']
