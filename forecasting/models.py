
from django.db import models
# from django.db.models import (FloatField, DecimalField, IntegerField, DateTimeField,
#                               ExpressionWrapper, F, Q, Count, Sum, Avg, Subquery, OuterRef, Case, When, Window)
from . import managers
from account.models import CustomUser 
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext as _

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

class Target(CommonMeta):
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
        TargetVersion, on_delete=models.CASCADE, blank=True, null=True)

    targeted_date = models.DateField(
        blank=True, null=True)
    targeted_quantity = models.IntegerField(blank=True, null=True)

class Version(CommonMeta):
    # TODO add verbose_name with translation
    AUTO = 'Automatic'
    MANU = 'Manual'
    FORECAST_TYPE = (
        (AUTO, 'Automatic'),
        (MANU, 'Manual'),
    )
    CREATED = 'Created'
    PENDING = 'Pending'
    APPROVED = 'Approved'
    STATUS = (
        (CREATED, 'Created'),
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
    )
    reference = models.CharField(unique=True, max_length=200)
    # year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2900)])
    # month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    forecast_type = models.CharField(
        max_length=32,
        choices=FORECAST_TYPE,
        default=AUTO,
    )
    version_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    # upload_to='forecast_files/%Y/%m/%d/'
    file_path = models.FileField(upload_to='forecast_versions/', blank=True)
    # is_budget = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        CustomUser, related_name='created_versions', on_delete=models.CASCADE, blank=True, null=True)
    approved_by = models.ForeignKey(
        CustomUser, related_name='approved_versions', on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=CREATED,
    )

    objects = managers.VersionQuerySet.as_manager()

    def __str__(self):
        return str(self.reference)

    class Meta:
        permissions = (
            ('request_review', 'Send review request'),
            ('validate_version', 'Validate a version'),
        )



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
    edited_forecasted_quantity = models.IntegerField(blank=True, null=True)

    objects = managers.ForecastQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'category', 'warehouse', 'forecast_date', 'circuit', 'version'], name='unique_forecast')
        ]

    def __str__(self):
        return f'product: {self.product}, warehouse: {self.warehouse}, forecast_date: {self.forecast_date}, circuit: {self.circuit}'


class Event(CommonMeta):
    PROMO = 'Promo'
    ACTION_MARKETING = 'Action Marketing'
    HOLIDAY = 'Holiday'
    CATEGORY = (
        (PROMO, 'Promo'),
        (ACTION_MARKETING, 'Action Marketing'),
        (HOLIDAY, 'Holiday'),
    )

    reference = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=32,
        choices=CATEGORY,
        default=PROMO,
    )

    def __str__(self):
        return self.reference


class EventDetail(CommonMeta):
    product = models.ForeignKey(
        'stock.Product', on_delete=models.CASCADE, blank=True, null=True)
    circuit = models.ForeignKey(
        'stock.Circuit', on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    lower_window = models.IntegerField(default=0, blank=True)
    upper_window = models.IntegerField(default=1, blank=True)

    objects = managers.EventDetailQuerySet.as_manager()

    def __str__(self):
        return f'event: {self.event}, date: {self.date}'
