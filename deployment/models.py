from django.db import models
from django.db.models import DecimalField, IntegerField, DateTimeField


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
        null=True, blank=True
    )
    # added_by = models.ForeignKey(settings.AUTH_USER_MODEL, )
    # modified_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

class TruckCategory(CommonMeta):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    TRUCK_TYPE = (
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    )
    reference = models.CharField(unique=True, max_length=200)    
    capacity = models.IntegerField(blank=True, null=True)
    cost = models.DecimalField(
        max_digits=11, decimal_places=2, blank=True, null=True)
    truck_type = models.CharField(
        max_length=32,
        choices=TRUCK_TYPE,
        default=SMALL,
    )

    def __str__(self):
        return f'{self.reference}'


class TruckAvailability(CommonMeta):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    TRUCK_TYPE = (
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    )
    category = models.ForeignKey(
        TruckCategory, on_delete=models.CASCADE, blank=True, null=True)
    warehouse = models.ForeignKey(
        'stock.Warehouse', on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(unique=True, max_length=200)
    available_truck = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.reference}'
