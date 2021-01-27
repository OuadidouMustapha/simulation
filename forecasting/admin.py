from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Forecast, Event, EventDetail
from .resources import ForecastResource


admin.site.register(Event)
admin.site.register(EventDetail)

@admin.register(Forecast)
class ForecastAdmin(ImportExportModelAdmin):
    resource_class = ForecastResource
