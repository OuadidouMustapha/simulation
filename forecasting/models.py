# import datetime

from django.db import models
# from django.db.models import (FloatField, DecimalField, IntegerField, DateTimeField,
#                               ExpressionWrapper, F, Q, Count, Sum, Avg, Subquery, OuterRef, Case, When, Window)
from . import managers

class CommonMeta(models.Model):
    CREATED = 'Created'
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'
    STATUS = (
        (CREATED, 'Created'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=CREATED,
    )
    # added_by = models.ForeignKey(settings.AUTH_USER_MODEL, )
    # modified_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class StockForecast(CommonMeta):

    stock = models.ForeignKey(
        'stock.Stock', on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(
        'stock.Customer', on_delete=models.CASCADE, blank=True, null=True)
    circuit = models.ForeignKey(
        'stock.Circuit', on_delete=models.CASCADE, blank=True, null=True)
    forecast_date = models.DateField(
        blank=True, null=True)
    forecast_version = models.DateField(auto_now_add=True)
    forecasted_quantity = models.IntegerField(blank=True, null=True)

    objects = managers.StockForecastQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stock', 'forecast_date', 'circuit', 'forecast_version'], name='stockforecast_stock_sp_fd_uniq')
        ]

    def __str__(self):
        return f'stock: {self.stock}, forecast_date: {self.forecast_date}, circuit: {self.circuit}'

