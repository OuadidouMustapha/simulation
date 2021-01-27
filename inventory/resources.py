from inventory.models import Location,StockCheck,Operation

from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, IntegerWidget, DateWidget, DecimalWidget
import datetime


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('reference',)
        exclude = ('product')
