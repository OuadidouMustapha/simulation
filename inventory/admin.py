from django.contrib import admin
from inventory.models import Location,StockCheck,Operation

from .resources import LocationResource

from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin

# Register your models here.

@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource


admin.site.register(Operation)
admin.site.register(StockCheck)
