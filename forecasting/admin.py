from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Forecast
from .resources import ForecastResource


@admin.register(Forecast)
class ForecastAdmin(ImportExportModelAdmin):
    resource_class = ForecastResource