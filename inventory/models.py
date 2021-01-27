from django.db import models
from stock.models import Product, Warehouse
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
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Location(CommonMeta):
    product = models.ManyToManyField(Product)
    reference = models.CharField(unique=True, max_length=20, null=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)

    objects = managers.LocationQuerySet.as_manager()

    def __str__(self):
        return f'{self.reference}'

class Operation(CommonMeta):
    A = 'A'
    Q = 'Q'
    R = 'R'
    STATUS = (
        (A, 'A'),
        (Q, 'Q'),
        (R, 'R'),
    )
    product = models.ForeignKey('stock.Product', on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(unique=False, max_length=20, null=True)
    operation_date = models.DateField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default='1')
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=A,
    )

    def __str__(self):
        return f'{self.reference}'

class StockCheck(CommonMeta):
    A = 'A'
    Q = 'Q'
    R = 'R'
    STATUS = (
        (A, 'A'),
        (Q, 'Q'),
        (R, 'R'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(unique=False, max_length=20, null=False) # FIXME shouldn't this be unique?
    check_date = models.DateField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=A,
    )

    objects = managers.StockCheckQuerySet.as_manager()

    def __str__(self):
        return f'{self.reference}'