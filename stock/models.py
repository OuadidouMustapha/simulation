import uuid
import datetime

from django.db import models
from django.db.models import (FloatField, DecimalField, IntegerField, DateTimeField,
                              ExpressionWrapper, F, Q, Count, Sum, Avg, Subquery, OuterRef, Case, When, Window)
from django.db.models.functions import (
    TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDay,
    ExtractDay, ExtractMonth, ExtractWeek, ExtractYear)
from django.utils import timezone
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from . import utils # TODO : Manage classes and functions
from . import managers


###############################################
# MANAGERS
###############################################

class WarehouseQuerySet(models.QuerySet):
    def get_warehouses(self):
        qs = self.annotate(available_products=Count(F('stock__product')))
        # qs = self.annotate(total_product_quantity=Sum(F('stock__product')))
        # qs = self.annotate(
        #     avg_delivered_quantity=ExpressionWrapper(
        #         Subquery(
        #             DeliveryDetail.objects.filter(
        #                 product=OuterRef('product'),
        #                 sale__delivered_at__gte=delivered_at_start,  # _start_date,
        #                 sale__delivered_at__lte=delivered_at_end,  # _send_date
        #             ).values('product__reference'
        #                     ).annotate(
        #                 avg_delivered_quantity=ExpressionWrapper(
        #                     Avg('delivered_quantity'), output_field=FloatField()
        #                 )
        #             ).values('avg_delivered_quantity')
        #         ), output_field=DecimalField(decimal_places=2)
        #     )
        # )
        return qs


class DeliveryDetailQuerySet(models.QuerySet):
    # stock_pareto functions
    def get_avg_delivered_quantity(self, filter_kwargs={}, group_by_field='product'):
        print('group_by_field; ', group_by_field)
        # Copy filter_kwargs to avoid errors after first compile
        # TODO use convert_group_by_field_to_attribute() from Utils to stay DRY
        filter_kwargs_copy = filter_kwargs.copy()
        if group_by_field == 'product':
            filter_kwargs_copy['stock__product'] = OuterRef('stock__product')
            group_by_field = 'stock__product'
        elif group_by_field == 'category':
            filter_kwargs_copy['stock__product__category'] = OuterRef(
                'stock__product__category')
            group_by_field = 'stock__product__category'

        qs = self.filter(**filter_kwargs_copy)
        qs = qs.values(group_by_field)
        qs = qs.annotate(
            avg_delivered_quantity=Avg(
                ExpressionWrapper(
                    F('delivered_quantity'), output_field=FloatField()
                )
            )
        ).values('avg_delivered_quantity')[:1]

        return qs

    def get_delivered_product_total_cost(self, filter_kwargs={}, group_by_field='product'):
        qs = self.filter(**filter_kwargs)
        qs = qs.annotate(
            avg_delivered_quantity=Subquery(
                self.get_avg_delivered_quantity(
                    filter_kwargs=filter_kwargs,
                    group_by_field=group_by_field
                )
            )
        )
        qs = qs.annotate(
            delivered_product_total_cost=ExpressionWrapper(
                F('avg_delivered_quantity')*F('stock__product__cost'), output_field=FloatField()
            )
        )
        qs = qs.values(
            'stock__product__reference',
            'avg_delivered_quantity',
            'stock__product__cost',
            'delivered_product_total_cost'
        ).distinct()
        return qs

    def get_cumul_delivered_product_total_cost(self, filter_kwargs={}, group_by_field='product'):
        qs = self.get_delivered_product_total_cost(
            filter_kwargs, group_by_field)
        qs = qs.order_by('-delivered_product_total_cost')

        qs = qs.annotate(
            cumul_delivered_product_total_cost=Window(
                Sum('delivered_product_total_cost'),
                order_by=F('delivered_product_total_cost').desc(),
                output_field=FloatField()
            )
        )
        qs = qs.annotate(
            cumul_delivered_product_total_cost_corrected=ExpressionWrapper(
                F('cumul_delivered_product_total_cost')/100, output_field=FloatField()
            )
        )
        return qs


class StockControlQuerySet(models.QuerySet):
    def add_trunc_date(self, field_name, kind='day'):
        """Truncate a datetime field based on `kind` argument and annotate it to the queryset
        
        Parameters
        ----------
        models : [type]
            [description]
        field_name : str
            Model's field to be truncated
        kind : str, optional
            Represents a date part. Possible values are `year`, `quarter`, `month`, `week` or `day`, by default `day`
        
        Returns
        -------
        queryset
            Truncated date as a new field named `<field_name>_truncated` to queryset
        """
        # Name the field that will be used as output for annotation
        output_field_name = field_name + '_truncated'
        # Build truncation function name, e.g. TruncYear('inventory_date')
        trunc_function = 'Trunc{kind}("{field_name}")'.format(
            kind=kind.capitalize(), field_name=field_name)

        annotate_kwargs = {output_field_name: eval(trunc_function)}

        qs = self.annotate(**annotate_kwargs)
        return qs

    # stock_dio functions
    def get_stock_value(self, kind='day', group_by_field='product', filter_kwargs={}):
        # Fill the group_by condition
        values_args = []
        if group_by_field == 'product':
            values_args.append('stock__product__reference')
        elif group_by_field == 'category':
            values_args.append('stock__product__category__reference')
        else:
            raise ValueError

        # Filter query
        qs = self.filter(**filter_kwargs)
        # Annotate truncated `inventory_date`
        qs = qs.add_trunc_date('inventory_date', kind=kind)
        # Group result by `group_by_field`
        qs = qs.values('inventory_date_truncated', *values_args)

        qs = qs.annotate(
            avg_cost=Avg(ExpressionWrapper(
                F('product_quantity')*F('stock__product__cost'), output_field=FloatField())),
            avg_quantity=Avg(ExpressionWrapper(
                F('product_quantity'), output_field=FloatField())),
            avg_package=Avg(ExpressionWrapper(
                F('product_quantity')/F('stock__product__package'), output_field=IntegerField())),
            avg_pallet=Avg(ExpressionWrapper(
                F('product_quantity')/F('stock__product__pallet'), output_field=IntegerField())),
            avg_weight=Avg(ExpressionWrapper(
                F('product_quantity')*F('stock__product__weight'), output_field=FloatField())),
            avg_volume=Avg(ExpressionWrapper(
                F('product_quantity')*F('stock__product__volume'), output_field=FloatField())),
        )
        return qs

    def annotate_count_avg_dio(self, dio_low_value, dio_high_value, **kwargs):

        delivered_at_start = datetime.datetime(
            2018, 3, 4, 0, 0, tzinfo=datetime.timezone.utc)
        delivered_at_end = datetime.datetime(
            2020, 3, 7, 0, 0, tzinfo=datetime.timezone.utc)

        # Get main queryset with available kwargs arguments
        query_kwargs = {}
        if 'kind' in kwargs:
            query_kwargs['kind'] = kwargs.get('kind')
        if 'group_by_field' in kwargs:
            query_kwargs['group_by_field'] = kwargs.get('group_by_field')
        if 'filter_kwargs' in kwargs:
            query_kwargs['filter_kwargs'] = kwargs.get('filter_kwargs')

        qs = self.get_stock_value(**query_kwargs)
        qs = qs.annotate(
            avg_delivered_quantity=ExpressionWrapper(
                Subquery(
                    DeliveryDetail.objects.filter(
                        stock__product=OuterRef(utils.convert_group_by_field_to_attribute(
                            'product', 'StockControl')),
                        sale__delivered_at__gte=delivered_at_start,  # _start_date,
                        sale__delivered_at__lte=delivered_at_end,  # _send_date
                    ).values('stock__product__reference'
                             ).annotate(
                        avg_delivered_quantity=ExpressionWrapper(
                            Avg('delivered_quantity'), output_field=FloatField()
                        )
                    ).values('avg_delivered_quantity')
                ), output_field=DecimalField(decimal_places=2)
            ),
            avg_dio=ExpressionWrapper(
                F('product_quantity') / F('avg_delivered_quantity'), output_field=DecimalField(decimal_places=2)
            )
        )

        # Group queryset by truncated inventory date
        qs = qs.values('inventory_date_truncated')
        # Annotate to query the count of average DIO based on its level
        qs = qs.annotate(
            count_avg_dio_lev1=Count(
                F('avg_dio'),
                filter=Q(avg_dio__gte=0) & Q(avg_dio__lt=dio_low_value)
            ),
            count_avg_dio_lev2=Count(
                F('avg_dio'),
                filter=Q(avg_dio__gte=dio_low_value) & Q(
                    avg_dio__lt=dio_high_value)
            ),
            count_avg_dio_lev3=Count(
                F('avg_dio'),
                filter=Q(avg_dio__gte=dio_high_value)
            ),
        )

        return qs

    # stock_pareto functions
    def get_avg_product_quantity(self, filter_kwargs={}, group_by_field='product'):
        # Copy filter_kwargs to avoid errors after first compile
        filter_kwargs_copy = filter_kwargs.copy()
        if group_by_field == 'product':
            filter_kwargs_copy['stock__product'] = OuterRef(
                'stock__product')
            group_by_field = 'stock__product'
        elif group_by_field == 'category':
            filter_kwargs_copy['stock__product__category'] = OuterRef(
                'stock__product__category')
            group_by_field = 'stock__product__category'

        qs = self.filter(**filter_kwargs_copy)
        qs = qs.values(group_by_field)
        qs = qs.annotate(
            avg_product_quantity=Avg(
                ExpressionWrapper(
                    F('product_quantity'), output_field=FloatField()
                )
            )
        ).values('avg_product_quantity')[:1]

        return qs

    def get_product_total_cost(self, filter_kwargs={}, group_by_field='product'):
        qs = self.filter(**filter_kwargs)
        qs = qs.annotate(
            avg_product_quantity=Subquery(
                self.get_avg_product_quantity(
                    filter_kwargs=filter_kwargs,
                    group_by_field=utils.convert_group_by_field_to_attribute(
                        group_by_field, 'StockControl')
                )
            )
        )
        qs = qs.annotate(
            product_total_cost=ExpressionWrapper(
                F('avg_product_quantity')*F('stock__product__cost'), output_field=FloatField()
            )
        )
        qs = qs.values(
            'stock__product__reference',
            'avg_product_quantity',
            'stock__product__cost',
            'product_total_cost'
        ).distinct()
        return qs

    def get_cumul_product_total_cost(self, filter_kwargs={}, group_by_field='product'):
        qs = self.get_product_total_cost(filter_kwargs, group_by_field)
        qs = qs.order_by('-product_total_cost')

        qs = qs.annotate(
            cumul_product_total_cost=Window(
                Sum('product_total_cost'),
                order_by=F('product_total_cost').desc(),
                output_field=FloatField()
            )
        )
        qs = qs.annotate(
            cumul_product_total_cost_corrected=ExpressionWrapper(
                F('cumul_product_total_cost')/100, output_field=FloatField()
            )
        )
        return qs


###############################################
# MODELS
###############################################

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


class ProductCategory(MPTTModel):
    CREATED = 'Created'
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'
    STATUS = (
        (CREATED, 'Created'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
    )
    reference = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    # Parent attribute uses MPTT model
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children', db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    min_dio = models.IntegerField(
        'Min DIO', null=True, blank=True)
    max_dio = models.IntegerField(
        'Max DIO', null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=CREATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tree = TreeManager()


    objects = managers.ProductCategoryQuerySet.as_manager()


    class MPTTMeta:
        order_insertion_by = ['reference']

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        # return self.name
        return f'{self.reference}'

    def was_created_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    def get_categories():
        '''
        return list of unique/distinct categories
        '''
        return ProductCategory.objects.annotate(label=F('reference'), value=F('id')).values('label', 'value').distinct()

    def get_total_categories(status=None):
        '''
        Return total number of categories
        '''
        filter_kwargs = {}
        if status:
            filter_kwargs = {'status': status}

        return ProductCategory.objects.filter(**filter_kwargs).count()


class Product(CommonMeta):
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, blank=True, null=True)  # Try this parameter related_name='products'
    reference = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    cost = models.DecimalField(
        max_digits=11, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=11, decimal_places=2, blank=True, null=True)
    weight_unit = models.TextField(blank=True)
    volume = models.DecimalField(
        max_digits=11, decimal_places=2, blank=True, null=True)
    volume_unit = models.TextField(blank=True)
    package_size = models.IntegerField(blank=True, null=True)
    pallet_size = models.IntegerField(blank=True, null=True)
    product_type = models.CharField(max_length=20, blank=True, null=True)
    product_ray = models.CharField(max_length=20, blank=True, null=True)
    product_universe = models.CharField(max_length=20, blank=True, null=True)

    objects = managers.ProductQuerySet.as_manager()

    
    class Meta:  # new
        indexes = [models.Index(fields=['reference'])]
        ordering = ['reference']

    def __str__(self):
        return f'{self.reference}'


    # def get_absolute_url(self):
    #     return reverse('forecasting:input_interface')
    
    def get_products(category_ids=None):
        '''
        return list of unique/distinct products
        '''
        filter_kwargs = {}
        if category_ids is not None:
            filter_kwargs = {'category__in': category_ids}

        queryset = Product.objects.filter(
            **filter_kwargs
        ).annotate(
            label=F('reference'),
            value=F('id')
        ).values('label', 'value').distinct()
        
        return queryset

    def get_total_products(status=None):
        filter_kwargs = {}
        if status:
            filter_kwargs = {'status': status}

        return Product.objects.filter(**filter_kwargs).count()


class Warehouse(CommonMeta):

    reference = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    available_trucks = models.IntegerField(blank=True, null=True)
    reception_capacity = models.IntegerField(blank=True, null=True)
    lat = DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    objects = managers.WarehouseQuerySet.as_manager()
    
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['name', 'lat', 'lon'], name='stock_warehouse_uniq')
    #     ]

    def __str__(self):
        return f'{self.name}'


class Stock(CommonMeta):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'product:{self.product}, warehouse: {self.warehouse}'


class StockPolicy(CommonMeta):
    stock = models.OneToOneField(
        Stock, 
        on_delete=models.CASCADE, 
        # primary_key=True,
    )
    safety_stock = models.IntegerField(blank=True, null=True)
    delivery_time = models.IntegerField(blank=True, null=True)
    order_point = models.IntegerField(blank=True, null=True)
    target_stock = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'stock: {self.stock}'


class StockControl(CommonMeta):

    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, blank=True, null=True)
    inventory_date = models.DateField(
        blank=True, null=True)  # change to control_date
    product_quantity = models.IntegerField(blank=True, null=True)
    objects = StockControlQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['stock', 'inventory_date'], name='stockcontrol_stock_sp_id_uniq')
        ]

    def __str__(self):
        return f'stock: {self.stock}, inventory_date: {self.inventory_date}'


    def get_stock_value(category_ids, product_ids, start_date, end_date, period='year', group_by='product'):
        '''
        TODO : add default parameters
        Return list of sales of one product between a range of date
        [{'inventory_date': * , 'product_quantity': *, 'total_cost': *}]
        '''
        # Initial parameters
        annotate_kwargs = {}
        values_args = []

        # Add attributes depending on selected period
        if period == 'year':
            annotate_kwargs = {
                'inventory_date_truncated': TruncYear('inventory_date')}
            values_args.append('inventory_date_truncated')

        elif period == 'quarter':
            annotate_kwargs = {
                'inventory_date_truncated': TruncQuarter('inventory_date')}
            values_args.append('inventory_date_truncated')

        elif period == 'month':
            annotate_kwargs = {
                'inventory_date_truncated': TruncMonth('inventory_date')}
            values_args.append('inventory_date_truncated')

        elif period == 'week':
            annotate_kwargs = {
                'inventory_date_truncated': TruncWeek('inventory_date')}
            values_args.append('inventory_date_truncated')

        elif period == 'day':
            annotate_kwargs = {
                'inventory_date_truncated': TruncDay('inventory_date')}
            values_args.append('inventory_date_truncated')
        else:
            # Value by default is `year`
            annotate_kwargs = {
                'inventory_date_truncated': TruncYear('inventory_date')}
            values_args.append('inventory_date_truncated')
            pass

        # Group data by category or products
        if group_by == 'product':
            values_args.append('stock__product__reference')
        elif group_by == 'category':
            values_args.append('stock__product__category__reference')
        else:  # Default value
            values_args.append('stock__product__reference')

        # def avg_quantity_by_product_in_date_range(delivered_at_start_date, delivered_at_end_date, outref_product='product'):
        #     '''
        #     '''
        #     queryset = DeliveryDetail.objects.filter(
        #         product=OuterRef('product'),
        #         sale__delivered_at__gte=delivered_at_start_date,
        #         sale__delivered_at__lte=delivered_at_end_date
        #     ).values(
        #         'product__reference'
        #     ).annotate(
        #         avg_quantity=Avg('delivered_quantity')
        #     ).values('avg_quantity')

        #     return queryset

        queryset = StockControl.objects.filter(
            Q(inventory_date__gte=start_date)
            & Q(inventory_date__lte=end_date),
            stock__product__category__in=category_ids,
            stock__product__in=product_ids,
        ).annotate(**annotate_kwargs
        ).values(*values_args
        ).annotate(
            avg_cost=Avg(ExpressionWrapper(
                F('product_quantity')*F('stock__product__cost'), output_field=FloatField())),
            avg_quantity=Avg(ExpressionWrapper(
                F('product_quantity'), output_field=FloatField())),
            avg_package=Avg(ExpressionWrapper(
                F('product_quantity')/F('stock__product__package'), output_field=IntegerField())),
            avg_pallet=Avg(ExpressionWrapper(
                F('product_quantity')/F('stock__product__pallet'), output_field=IntegerField())),
            avg_weight=Avg(ExpressionWrapper(
                F('product_quantity')*F('stock__product__weight'), output_field=FloatField())),
            avg_volume=Avg(ExpressionWrapper(
                F('product_quantity')*F('stock__product__volume'), output_field=FloatField())),
            avg_dio=Avg(ExpressionWrapper(
                F('product_quantity') / Subquery(
                    DeliveryDetail.objects.filter(
                        stock__product=OuterRef('stock__product'),
                        sale__delivered_at__gte=start_date,  # _start_date,
                        sale__delivered_at__lte=end_date,  # _send_date
                    ).values('stock__product__reference'
                    ).annotate(
                        avg_quantity=Avg('delivered_quantity')
                    ).values('avg_quantity')
                ), output_field=DecimalField(decimal_places=2)
            ))
        )

        return queryset

    def annotate_count_avg_dio(queryset, dio_low_value, dio_high_value):
        queryset = queryset.annotate(
            count_avg_dio_lev1=Count(
                F('avg_dio'),
                filter=Q(avg_dio__gte=0) & Q(avg_dio__lt=dio_low_value)
            ),
            # count_avg_dio_lev2=Count(
            #     F('avg_dio'),
            #     # filter=Q(avg_dio__gte=dio_low_value) & Q(
            #     #     avg_dio__lt=dio_high_value)
            # ),
            # count_avg_dio_lev3=Count(
            #     F('avg_dio'),
            #     # filter=Q(avg_dio__gte=dio_high_value)
            # ),
        )

        return queryset

    def avg_delivered_quantity_by_product_in_date_range(delivered_at_start_date, delivered_at_end_date, category_ids=None, product_ids=None):
        '''
        '''
        # Check if `product_ids` argument is an array like [1, 2, 10]
        # else it should be an `Outref()` function
        # notice `stock__product__in` vs `product` in each case
        filter_kwargs = {}
        if category_ids is None:
            filter_kwargs = {}
        elif isinstance(category_ids, list):
            filter_kwargs['stock__product__category__in'] = category_ids
        else:
            filter_kwargs = {'stock__product__category': category_ids}

        if product_ids is None:
            filter_kwargs = {}
        elif isinstance(product_ids, list):
            filter_kwargs['stock__product__in'] = product_ids
        else:
            filter_kwargs = {'stock__product': product_ids}

        queryset = DeliveryDetail.objects.filter(
            **filter_kwargs,
            sale__delivered_at__gte=delivered_at_start_date,
            sale__delivered_at__lte=delivered_at_end_date,
        ).values(
            utils.convert_group_by_field_to_attribute(
                'product', 'DeliveryDetail')
        ).annotate(
            avg_quantity=Avg('delivered_quantity')
        )

        return queryset

    def stock_query_filter(**kwargs):
        """

        Parameters
        ----------
        avg_quantity_period : str, optional
            [description], by default 'year'
        group_by : str, optional
            [description], by default 'product'

        Other Parameters
        ----------------
        inventory_date_start : datetime, optional
            Query filter argument. Keeping results with an `inventory_date` greater or equal to input date, by default None.
        inventory_date_end : datetime, optional
            Query filter argument. Keeping results with an `inventory_date` less or equal to input date, by default None.
        category_ids : array, optional
            Query filter argument. Keeping resuls with category id is in input array. Assuming the existance of `stock_policy__product__category` attribute, by default None.
        product_ids : array, optional
            Query filter argument. Keeping resuls with product id is in input array. Assuming the existance of `product` attribute, by default None.
        include_weekend : bool, optional
            Query exclude argument. If False, exclude results where `inventory_date` is Saturday or Sunday. Assuming the existance of `inventory_date` attribute, by default True.

        Returns
        -------
        queryset
            Filtered queryset based on input keyword arguments. Returns all objects if no argument specified.
        """
        # -- initial parameters --
        filter_kwargs = {}
        exclude_kwargs = {}

        # -- `filter_kwargs` --
        # Filter by `inventory_date` date range
        if 'inventory_date_start' in kwargs:
            filter_kwargs['inventory_date__gte'] = kwargs.get(
                'inventory_date_start')
        if 'inventory_date_end' in kwargs:
            filter_kwargs['inventory_date__lte'] = kwargs.get(
                'inventory_date_end')

        # Filter by categories
        if 'category_ids' in kwargs:
            filter_kwargs['stock__product__category__in'] = kwargs.get(
                'category_ids')

        # Filter by products
        if 'product_ids' in kwargs:
            filter_kwargs['stock__product__in'] = kwargs.get(
                'product_ids')

        # -- `exclude_kwargs` --
        # Check if weekends in `inventory_date` should be excluded
        if 'include_weekend' in kwargs:
            if not kwargs.get('include_weekend'):
                # Exclude Saturday and Sunday
                exclude_kwargs['inventory_date__week_day__in'] = [1, 7]

        # -- queryset --
        qs = StockControl.objects.filter(**filter_kwargs)
        qs = qs.exclude(**exclude_kwargs)

        return qs

    def get_stock_dio(
            delivered_at_start_date,
            delivered_at_end_date,
            avg_quantity_period='year',
            avg_sale_period='year',
            group_by='product',
            **kwargs):
        """TODO : add default parameters
        Return list of sales of one product between a range of date
        [{'inventory_date': * , 'product_quantity': *, 'total_cost': *}]
        
        Parameters
        ----------
        start_date : [type]
            [description]
        end_date : [type]
            [description]
        delivered_at_start_date : [type]
            [description]
        delivered_at_end_date : [type]
            [description]
        avg_quantity_period : str, optional
            [description], by default 'year'
        avg_sale_period : str, optional
            [description], by default 'year'
        group_by : str, optional
            [description], by default 'product'
        
        Other Parameters
        ----------------
        **kwargs : xxx, optional
            All kwargs of `stock_query_filter` could be used, by default xxx.

        Returns
        -------
        [type]
            [description]
        """
        def annotate_avg_dio_to_stock(stock_queryset, group_by='product', avg_sale_period='year'):
            """[summary]
            
            Parameters
            ----------
            stock_queryset : queryset
                Stock query to which the annotation should be added
            group_by : str, optional
                [description], by default 'product'
            avg_sale_period : str, optional
                [description], by default 'year'
            
            Returns
            -------
            queryset
                Values `stock__product__reference` and `avg_dio`
            """
            # Check if `product_ids` argument is an array like [1, 2, 10]
            # else it should be an `Outref()` function
            # notice `stock__product__in` vs `product` in each case
            filter_kwargs = {}
            values_args = []

            # -- `group_by` --
            stockcontrol_group_by_attribute = utils.convert_group_by_field_to_attribute(group_by, 'StockControl')
            saledetail_group_by_attribute = utils.convert_group_by_field_to_attribute(group_by, 'DeliveryDetail')

            filter_kwargs[saledetail_group_by_attribute] = OuterRef(
                stockcontrol_group_by_attribute)
            values_args.append(f'{saledetail_group_by_attribute}__reference')

            # if group_by == 'category':
            #     filter_kwargs['stock__product__category'] = OuterRef(
            #         'stock__product__category')
            #     values_args.append(
            #         'stock__product__category__reference')
            # elif group_by == 'product':
            #     filter_kwargs['product'] = OuterRef('product')
            #     values_args.append('stock__product__reference')

            # -- `avg_sale_period` --
            if avg_sale_period == 'year':
                filter_kwargs['sale__delivered_at__year'] = ExtractYear(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
            elif avg_sale_period == 'month':
                filter_kwargs['sale__delivered_at__year'] = ExtractYear(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
                filter_kwargs['sale__delivered_at__month'] = ExtractMonth(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
            elif avg_sale_period == 'week':
                filter_kwargs['sale__delivered_at__year'] = ExtractYear(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
                filter_kwargs['sale__delivered_at__month'] = ExtractMonth(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
                filter_kwargs['sale__delivered_at__week'] = ExtractWeek(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
            elif avg_sale_period == 'day':
                filter_kwargs['sale__delivered_at__year'] = ExtractYear(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
                filter_kwargs['sale__delivered_at__month'] = ExtractMonth(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
                filter_kwargs['sale__delivered_at__week'] = ExtractWeek(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
                filter_kwargs['sale__delivered_at__day'] = ExtractDay(
                    ExpressionWrapper(
                        OuterRef('inventory_date'),
                        output_field=models.DateTimeField()
                    )
                )
            # Create a subquery for `DeliveryDetail`
            sub_qs = DeliveryDetail.objects.filter(**filter_kwargs)
            sub_qs = sub_qs.values(*values_args)
            sub_qs = sub_qs.annotate(
                avg_delivered_quantity=Avg('delivered_quantity'))
            sub_qs = sub_qs.values('avg_delivered_quantity')
            # Create annotation for the query
            qs = stock_queryset.annotate(
                avg_dio=Avg(
                    ExpressionWrapper(
                        F('product_quantity') /
                        Subquery(
                            sub_qs
                        ), output_field=DecimalField(decimal_places=2)
                    )
                )
            )
            qs = qs.values('stock__product__category__reference' if group_by ==
                           'category' else 'stock__product__reference', 'avg_dio')

            return qs

        values_args = []

        # Group data by category or products then by truncated date
        if group_by == 'product':
            values_args.append('stock__product__reference')
        elif group_by == 'category':
            values_args.append('stock__product__category__reference')
        else:  # Default value
            values_args.append('stock__product__reference')

        values_args.append('inventory_date_truncated')

        # -- queryset --
        # Filter queryset based on keyword arguments
        qs = StockControl.stock_query_filter(**kwargs)
        # Add truncated attribute for `inventory_date` depending on selected `avg_quantity_period`
        qs = utils.trunc_date_attribute(
            qs, 'inventory_date', trunc_period=avg_quantity_period)
        # Customize queryset
        qs = qs.values(*values_args)

        qs = annotate_avg_dio_to_stock(
            qs, group_by=group_by, avg_sale_period=avg_sale_period)

        return qs


class Circuit(CommonMeta):
    reference = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True)

    objects = managers.CircuitQuerySet.as_manager()
    

    def __str__(self):
        return f'{self.reference}'

class Customer(CommonMeta):
    # TODO : Separate Customer as a company from the provider as a person
    reference = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    circuit = models.ForeignKey(
        Circuit, on_delete=models.CASCADE, blank=True, null=True)

    
    objects = managers.CustomerQuerySet.as_manager()


    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['reference', 'circuit'], name='customer_reference_circuit_uniq')
    #     ]

    def __str__(self):
        return f'{self.reference}'

class Order(CommonMeta):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    circuit = models.ForeignKey(
        Circuit, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(max_length=200, blank=True, null=True)
    # total_amount = models.IntegerField(blank=True, null=True)
    ordered_quantity = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    unit_price = models.IntegerField(blank=True, null=True)
    ordered_at = models.DateField(blank=True, null=True)

    objects = managers.OrderQuerySet.as_manager()


    def __str__(self):
        return f'reference:{self.reference}, product: {self.product}'

    def get_product_orders(product_id, start_date, end_date):
        '''
        TODO : add default parameters
        Return list of order of one product between a range of date
        '''
        product_order = OrderDetail.objects.filter(
            product=product_id)
        product_order_query = Order.objects.filter(Q(orderdetail__in=product_order) & Q(ordered_at__gte=start_date) & Q(ordered_at__lte=end_date)).values(
            'reference', 'ordered_at', 'orderdetail__product', 'orderdetail__ordered_quantity')

        return product_order_query


# class OrderDetail(CommonMeta):

#     stock = models.ForeignKey(
#         Stock, on_delete=models.CASCADE)
#     order = models.ForeignKey(
#         Order, on_delete=models.CASCADE, blank=True, null=True)
#     unit_price = models.IntegerField(blank=True, null=True)
#     ordered_quantity = models.IntegerField(blank=True, null=True)

#     objects = managers.OrderDetailQuerySet.as_manager()

#     def __str__(self):
#         return f'Order:{self.order}, Stock: {self.stock}'


class Delivery(CommonMeta):  # TODO rename to Delivery

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    circuit = models.ForeignKey(
        Circuit, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(max_length=200, blank=True, null=True)
    delivered_at = models.DateField(blank=True, null=True)
    delivered_quantity = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    total_amount = models.IntegerField(blank=True, null=True)
    
    objects = managers.DeliveryQuerySet.as_manager()


    def __str__(self):
        return f'order:{self.order}, reference: {self.reference}'

    def get_product_sales(product_id, start_date, end_date):
        '''
        TODO : add default parameters
        Return list of sales of one product between a range of date
        '''
        product_sales = DeliveryDetail.objects.filter(
            product=product_id)
        product_sales_query = Delivery.objects.filter(Q(saledetail__in=product_sales) & Q(delivered_at__gte=start_date) & Q(delivered_at__lte=end_date)).values(
            'reference', 'delivered_at', 'saledetail__product', 'saledetail__delivered_quantity')

        return product_sales_query


class DeliveryDetail(CommonMeta):
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE)
    sale = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, blank=True, null=True)
    unit_price = models.IntegerField(blank=True, null=True)
    delivered_quantity = models.IntegerField(blank=True, null=True)

    objects = DeliveryDetailQuerySet.as_manager()

    def __str__(self):
        return f'sale:{self.sale}, Stock: {self.stock}'

    def get_products():
        # TODO : delete this methode if not used Or update it (We already have a similar functtion in `product` class)
        '''
        Get list of products with order(s)
        [{'label': 'P03600', 'value': 1}, {'label': 'P03601', 'value': 2}]
        This format is compatible with Plotly data input
        '''
        return list(DeliveryDetail.objects.annotate(label=F('product__reference'), value=F('product')).values('label', 'value').distinct())

    def get_avg_quantity_in_date_range(delivered_at_start, delivered_at_end):
        '''
        delivered_at_start : start date sold at 
        delivered_at_end : end date sold at 
        '''
        queryset = DeliveryDetail.objects.filter(
            sale__delivered_at__gte=delivered_at_start,
            sale__delivered_at__lte=delivered_at_end
        ).values(
            'product__reference'
        ).annotate(
            avg_quantity=Avg('delivered_quantity')
        )
        return queryset


class Invoice(CommonMeta):

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, blank=True, null=True)
    sale = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(unique=True, max_length=200)
    invoicing_date = models.DateField(blank=True, null=True)
    # may add other fields like billing method, coupon, credit..
    total_amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'reference:{self.reference}'


class Supplier(CommonMeta):
    # TODO : Separate provider as a company from the provider as a person
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)

    def __str__(self):
        return f'{self.reference}'


class Supply(CommonMeta):

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(unique=True, max_length=200)
    supplied_at = models.DateField(blank=True, null=True)
    total_amount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.reference}'


class SupplyDetail(CommonMeta):

    supply = models.ForeignKey(
        Supply, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    # supply_type = local, import
    unit_price = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'Supply: {self.supply}, product: {self.product}'


# Deleted table (table `ProductQuantity` added instead)
# class StockOperation(models.Model):
#     CREATED = 'Created'
#     ACTIVE = 'Active'
#     ARCHIVED = 'Archived'
#     STATUS = (
#         (CREATED, 'Created - default'),
#         (ACTIVE, 'Active - available'),
#         (ARCHIVED, 'Archived - not available anymore'),
#     )
#     # OPERATION_TYPE = (
#     #     (INPUT, 'Input +'),
#     #     (OUTPUT, 'Output -'),
#     # )

#     stock = models.ForeignKey(
#         Stock, on_delete=models.CASCADE, blank=True, null=True)
#     product = models.ForeignKey(
#         Product, on_delete=models.CASCADE, blank=True, null=True)
#     quantity = models.IntegerField(blank=True, null=True)
#     operation_type = models.CharField(max_length=200)
#     operation_date = models.DateTimeField(blank=True, null=True)
#     status = models.CharField(
#         max_length=32,
#         choices=STATUS,
#         default=CREATED,
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.warehouse + '|' + self.product

################ 200504 ##################

# class ProductQuantity(CommonMeta):
#     product = models.ForeignKey(
#         Product, on_delete=models.CASCADE, blank=True, null=True)
#     quantity = models.IntegerField(blank=True, null=True)
#     inventory_date = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return f'{self.reference}'

#     def get_absolute_url(self):
#         return reverse('stock:product_detail', kwargs={'pk': self.id})
