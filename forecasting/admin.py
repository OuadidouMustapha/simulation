from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import StockForecast
from .resources import StockForecastResource


@admin.register(StockForecast)
class StockForecastAdmin(ImportExportModelAdmin):
    resource_class = StockForecastResource