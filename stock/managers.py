from django.db import models
from django.db.models import (CharField, FloatField, DecimalField, IntegerField, DateTimeField, Value,
                              ExpressionWrapper, F, Q, Count, Sum, Avg, Subquery, OuterRef, Case, When, Window)
from common import utils as common_utils  # TODO : Manage classes and functions
from . import utils  # TODO : Manage classes and functions
# from . import models
import datetime
from django.apps import apps

class ProductCategoryQuerySet(models.QuerySet):
    def get_productcategory_parent_sub_queryset(self, level):
        qs = self.filter(
            # Filter to get parent of category based on selected level
            lft__lte=OuterRef('stock__product__category__lft'),
            rght__gte=OuterRef('stock__product__category__rght'),
            tree_id=OuterRef('stock__product__category__tree_id'),
            level=level
        )
        qs = qs.values('reference')
        return qs

class OrderQuerySet(models.QuerySet):
    def get_forecasting(self, warehouse_filter, product_filter, circuit_filter, start_date=None, end_date=None):
        '''get forecast and order query'''
        filter_kwargs = {}
        # filter_kwargs['warehouse__in'] = warehouse_filter
        # filter_kwargs['product__in'] = product_filter
        # filter_kwargs['circuit__in'] = circuit_filter
        if start_date is not None:
            filter_kwargs['ordered_at__gte'] = start_date
        if end_date is not None:
            filter_kwargs['ordered_at__lte'] = end_date

        qs = self.filter(**filter_kwargs)
        qs = qs.select_related('product', 'warehouse', 'circuit', 'customer')
        # qs = qs.
        qs = qs.values('product', 'warehouse', 'circuit', 'customer',
                       'ordered_at', 'ordered_quantity', 'product__product_ray', 'product__product_type')
        return qs


    def _get_group_by_product_filter(self, group_by_product):
        # Prepare filter to be used based on group_by_product option
        filter_kwargs = {}

        if group_by_product == 'product':
            filter_kwargs['stock__product'] = OuterRef('stock__product')

        # elif group_by_product == 'stock':
        #     filter_kwargs['stock'] = OuterRef('stock')
        # elif group_by_product == 'warehouse':
        #     filter_kwargs['stock__warehouse'] = OuterRef('stock__warehouse')
        elif group_by_product == 'product_ray':
            filter_kwargs['stock__product__product_ray'] = OuterRef(
                'stock__product__product_ray')

        elif group_by_product == 'product_universe':
            filter_kwargs['stock__product__product_universe'] = OuterRef(
                'stock__product__product_universe')

        elif group_by_product in ['product_category_parent_level_0', 'product_category_parent_level_1', 'product_category_parent_level_2']:
            # TODO this needs more reflexion: case of multi trees with nested levels
            # Get the level filter which is the last character of the `group_by_product` string
            level = int(group_by_product[-1])
            ProductCategory = apps.get_model('stock', 'ProductCategory')
            category_parent_sub_qs = ProductCategory.objects.filter(
                lft__lte=ExpressionWrapper(
                    OuterRef('stock__product__category__lft'), output_field=IntegerField()),
                rght__gte=ExpressionWrapper(
                    OuterRef('stock__product__category__rght'), output_field=IntegerField()),
                tree_id=ExpressionWrapper(
                    OuterRef('stock__product__category__tree_id'), output_field=IntegerField()),
                level=level,
            )

            filter_kwargs['stock__product__category__lft__gte'] = ExpressionWrapper(
                Subquery(
                    category_parent_sub_qs.values('lft')
                ), output_field=IntegerField())
            filter_kwargs['stock__product__category__rght__lte'] = ExpressionWrapper(
                Subquery(
                    category_parent_sub_qs.values('rght')
                ), output_field=IntegerField())
            filter_kwargs['stock__product__category__tree_id'] = ExpressionWrapper(
                Subquery(
                    category_parent_sub_qs.values('tree_id')
                ), output_field=IntegerField())
            filter_kwargs['stock__product__category__level__gte'] = level
        return filter_kwargs

    def _get_group_by_distribution_filter(self, group_by_distribution):
        filter_kwargs = {}

        if group_by_distribution == 'warehouse':
            filter_kwargs['stock__warehouse'] = OuterRef(
                'stock__warehouse')

        elif group_by_distribution == 'customer':
            filter_kwargs['order__customer'] = OuterRef('customer')

        elif group_by_distribution == 'circuit':
            # FIXME if OuterRef('circuit') is null, the filter will not work as expected
                filter_kwargs['order__customer__circuit'] = OuterRef('circuit')

        elif group_by_distribution == 'sub_circuit':
            # FIXME if OuterRef('circuit') is null, the filter will not work as expected
            filter_kwargs['order__customer__circuit'] = OuterRef('circuit') 
        
        return filter_kwargs

    def _filter_by_group_by(self, group_by_product, group_by_distribution):
        filter_kwargs = {}
        filter_kwargs['ordered_at_truncated'] = OuterRef(
            'forecast_date_truncated')
        filter_kwargs_product = self._get_group_by_product_filter(
            group_by_product)
        filter_kwargs_distribution = self._get_group_by_distribution_filter(
            group_by_distribution)
        qs = self.filter(**filter_kwargs_product, **
                         filter_kwargs_distribution, **filter_kwargs)

        return qs

    def get_orderdetail_sub_queryset(self, group_by_product, group_by_distribution, show_by, kind):
                
        show_by_attribute = utils.get_show_by_attribute(show_by)

        if show_by == 'quantity':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity'), output_field=FloatField()
            )
        elif show_by == 'package':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') / F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'pallet':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') / F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'cost':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') * F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'weight':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') * F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'volume':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') * F(show_by_attribute), output_field=FloatField()
            )

        # Prepare subquery to get real ordered_quantity next to forecasted_quantity
        qs = common_utils.add_trunc_date(
            self, 'ordered_at', kind=kind, prefix='order__')
        qs = qs._filter_by_group_by(group_by_product, group_by_distribution)
        # group by date `ordered_at_truncated`
        qs = qs.values('ordered_at_truncated')

        qs = qs.annotate(
            total_ordered_value=Sum(ordered_value, output_field=FloatField())
        )
        qs = qs.values('total_ordered_value')
        return qs

    def get_total_ordered_value(self, group_by_product, group_by_distribution, show_by, kind):
        ''' Used as input for chart data'''
                
        show_by_attribute = utils.get_show_by_attribute(show_by)

        if show_by == 'quantity':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity'), output_field=FloatField()
            )
        elif show_by == 'package':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') / F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'pallet':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') / F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'cost':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') * F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'weight':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') * F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'volume':
            ordered_value = ExpressionWrapper(
                F('ordered_quantity') * F(show_by_attribute), output_field=FloatField()
            )

        # Prepare subquery to get real ordered_quantity next to forecasted_quantity
        qs = common_utils.add_trunc_date(
            self, 'ordered_at', kind=kind, prefix='order__')

        if group_by_distribution:
            filter_kwargs = self._get_group_by_distribution_filter(
                group_by_distribution)
            filter_kwargs['ordered_at_truncated'] = OuterRef(
                'forecast_date_truncated')
        else:
            filter_kwargs = self._get_group_by_product_filter(
                group_by_product)
            filter_kwargs['ordered_at_truncated'] = OuterRef(
                'forecast_date_truncated')
        qs = qs.filter(**filter_kwargs)

        # group by date `ordered_at_truncated`
        qs = qs.values('ordered_at_truncated')

        qs = qs.annotate(
            total_ordered_value=Sum(ordered_value, output_field=FloatField())
        )
        qs = qs.values('total_ordered_value')
        return qs
    
