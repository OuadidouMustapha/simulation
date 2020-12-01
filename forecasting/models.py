# import datetime

from django.db import models
# from django.db.models import (FloatField, DecimalField, IntegerField, DateTimeField,
#                               ExpressionWrapper, F, Q, Count, Sum, Avg, Subquery, OuterRef, Case, When, Window)
from . import managers
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

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



class Version(CommonMeta):
    COMMERCIAL = 'Commercial'
    LOGISTIC = 'Logistic'
    FORECAST_TYPE = (
        (COMMERCIAL, 'Commercial'),
        (LOGISTIC, 'Logistic'),
    )
    reference = models.CharField(unique=True, max_length=200)
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2900)])
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    forecast_type = models.CharField(
        max_length=32,
        choices=FORECAST_TYPE,
        default=COMMERCIAL,
    )
    version_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    # upload_to='forecast_files/%Y/%m/%d/'
    file_path = models.FileField(upload_to='forecast_versions/', blank=True)
    is_budget = models.BooleanField(default=False)
    objects = managers.VersionQuerySet.as_manager()

    def __str__(self):
        return str(self.reference)

    # def get_absolute_url(self):
    #     return reverse('forecasting:version_list')
        # return reverse('forecasting:version_list', pk=self.pk)



class Forecast(CommonMeta):

    product = models.ForeignKey(
        'stock.Product', on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(
        'stock.ProductCategory', on_delete=models.CASCADE, blank=True, null=True)
    warehouse = models.ForeignKey(
        'stock.Warehouse', on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(
        'stock.Customer', on_delete=models.CASCADE, blank=True, null=True)
    circuit = models.ForeignKey(
        'stock.Circuit', on_delete=models.CASCADE, blank=True, null=True)
    version = models.ForeignKey(
        Version, on_delete=models.CASCADE, blank=True, null=True)
    forecast_date = models.DateField(
        blank=True, null=True)
    forecasted_quantity = models.IntegerField(blank=True, null=True)

    objects = managers.ForecastQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'category', 'warehouse', 'forecast_date', 'circuit', 'version'], name='unique_forecast')
        ]

    def __str__(self):
        return f'product: {self.product}, warehouse: {self.warehouse}, forecast_date: {self.forecast_date}, circuit: {self.circuit}'
