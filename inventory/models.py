from django.db import models

from stock.models import Product,Warehouse
from . import managers


# Create your models here.


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
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Location(CommonMeta):
    reference    = models.CharField(unique=True, max_length=20, null=False)
    name         = models.CharField(max_length=200, blank=True, null=True)
    description  = models.TextField(blank=True)
    product      = models.ManyToManyField(Product)
    objects = managers.LocationQuerySet.as_manager()

    def __str__(self):
        return f'{self.reference}'
class Operation(CommonMeta):


    reference  = models.CharField(unique=False, max_length=20, null=True)
    product    = models.ForeignKey('stock.Product', on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    operation_date = models.DateField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default='1')
    A = 'A'
    Q = 'Q'
    R = 'R'
    CREATED = 'Created'
    STATUS = (
        (A, 'A'),
        (Q, 'Q'),
        (R, 'R'),
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=CREATED,
    )

    def __str__(self):
        return f'{self.reference}'

class StockCheck(CommonMeta):

    reference  = models.CharField(unique=False, max_length=20, null=False)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    check_date = models.DateField(blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True)
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    A = 'A'
    Q = 'Q'
    R = 'R'
    CREATED = 'Created'
    STATUS = (
        (A, 'A'),
        (Q, 'Q'),
        (R, 'R'),
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=CREATED,
    )
    objects = managers.StockCheckQuerySet.as_manager()


    def __str__(self):
        return f'{self.reference}'




