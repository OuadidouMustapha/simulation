from django.apps import apps
from django.db import models
from django.db.models import (Case, CharField, DecimalField, ExpressionWrapper,
                              F, FloatField, IntegerField, OuterRef, Q,
                              Subquery, Sum, Avg, Value, When, Window)
from django.db.models.functions import Abs

from common import utils as common_utils  
from . import utils  # TODO : Manage classes and functions


class StockForecastQuerySet(models.QuerySet):
    def get_forecast_versions(self):
        '''Get a list of available forecast versions'''
        qs = self.values_list('forecast_version', flat=True)
        qs = qs.order_by('-forecast_version').distinct()
        return qs

    #################################

    def _filter_by_forecast_date(self, start_date, end_date):
        filter_kwargs = {}
        if start_date is not None:
            filter_kwargs['forecast_date__gte'] = start_date
        if end_date is not None:
            filter_kwargs['forecast_date__lte'] = end_date

        qs = self.filter(**filter_kwargs)
        return qs

    def _filter_by_forecast_version(self, forecast_version):
        qs = self.filter(forecast_version=forecast_version)
        return qs

    def _get_forecast_date_truncated(self, kind):
        # qs = self.filter()
        qs = common_utils.add_trunc_date(self, 'forecast_date', kind)
        return qs

    #################################
    def _get_group_by_distribution_value(self, group_by_distribution):
        value = []
        if group_by_distribution == 'warehouse':
            value = ['stock__warehouse__name']

        elif group_by_distribution == 'customer':
            value = ['customer__reference']

        elif group_by_distribution == 'circuit':
            if self.filter(circuit__isnull=False).exists():
                value = ['circuit__name']
            elif self.filter(customer__isnull=False).exists():
                value = ['customer__circuit__name']

        elif group_by_distribution == 'sub_circuit':
            if self.filter(circuit__isnull=False).exists():
                value = ['circuit__name']
            elif self.filter(customer__isnull=False).exists():
                value = ['customer__circuit__name']
        return value

    def _get_group_by_product_value(self, group_by_product):
        value = []
        if group_by_product == 'product':
            value = ['stock__product__reference']

        elif group_by_product == 'product_ray':
            value = ['stock__product__product_ray']

        elif group_by_product == 'product_universe':
            value = ['stock__product__product_universe']

        elif group_by_product in ['product_category_parent_level_0', 'product_category_parent_level_1',
                                  'product_category_parent_level_2']:
            value = ['product_category_parent']

        return value

    def get_group_by_column(self, group_by_distribution, group_by_product):
        ''' Return database column name based on group_by variables. Used to plot charts '''
        if group_by_distribution:
            qs_value = self._get_group_by_distribution_value(
                group_by_distribution)
        else:
            qs_value = self._get_group_by_product_value(group_by_product)
        return qs_value


    #################################

    def _group_by(self, group_by_product, group_by_distribution):
        group_by_distribution_value = self._get_group_by_distribution_value(group_by_distribution)
        group_by_product_value = self._get_group_by_product_value(group_by_product)
        qs = self
        
        if group_by_product in ['product_category_parent_level_0',
                                'product_category_parent_level_1',
                                'product_category_parent_level_2']:
            level = int(group_by_product[-1])
            ProductCategory = apps.get_model('stock', 'ProductCategory')
            sub_qs = ProductCategory.objects.get_productcategory_parent_sub_queryset(
                level=level)

            qs = qs.annotate(
                product_category_parent=ExpressionWrapper(
                    Subquery(sub_qs), output_field=CharField()
                )
            )

        qs = qs.values(
            *group_by_distribution_value,
            *group_by_product_value, 
            'forecast_date_truncated'
        )

        return qs

    #################################
    def _get_forecasted_value(self, show_by):
        show_by_attribute = utils.get_show_by_attribute(show_by)

        if show_by == 'quantity':
            forecasted_value = ExpressionWrapper(
                F('forecasted_quantity'), output_field=FloatField()
            )
        elif show_by == 'package':
            forecasted_value = ExpressionWrapper(
                F('forecasted_quantity') / F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'pallet':
            forecasted_value = ExpressionWrapper(
                F('forecasted_quantity') / F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'cost':
            forecasted_value = ExpressionWrapper(
                F('forecasted_quantity') * F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'weight':
            forecasted_value = ExpressionWrapper(
                F('forecasted_quantity') * F(show_by_attribute), output_field=FloatField()
            )
        elif show_by == 'volume':
            forecasted_value = ExpressionWrapper(
                F('forecasted_quantity') * F(show_by_attribute), output_field=FloatField()
            )

        qs = self.annotate(
            forecasted_value=forecasted_value
        )
        return qs

    def _get_total_forecasted_value(self):
        # Prepare main queryset to get stock_forecast table
        qs = self.annotate(
            total_forecasted_value=Sum(
                'forecasted_value', output_field=FloatField())
        )
        return qs

    def _get_total_ordered_value(self, orderdetail_sub_query):
        qs = self.annotate(
            total_ordered_value=ExpressionWrapper(
                Subquery(orderdetail_sub_query), output_field=IntegerField()
            )
        )
        return qs

    def _get_forecast_bias(self):
        qs = self.annotate(
            forecast_bias=ExpressionWrapper(
                F('total_forecasted_value') - F('total_ordered_value'), output_field=FloatField()
            )
        )
        return qs

    def _get_forecast_bias_percent(self):
        qs = self.annotate(
            forecast_bias_percent=ExpressionWrapper(
                100.0 * F('total_forecasted_value') / F('total_ordered_value'), output_field=FloatField()
            )

        )
        return qs

    def _get_forecast_mad_single(self):
        '''Mean absolute deviation (MAD) of a single item abs(Forecast - Order)'''
        qs = self.annotate(
            forecast_mad_single=Abs(
                F('total_forecasted_value') - F('total_ordered_value'), output_field=FloatField()
            )
        )
        return qs

    def _get_forecast_mape_single(self):
        '''Mean absolute percentage error (MAPE) of a single item (abs(Forecast - Order) / Order)'''
        qs = self.annotate(
            forecast_mape_single=ExpressionWrapper(
                100.0 * F('forecast_mad_single') / F('total_ordered_value'), output_field=FloatField()
            )
        )
        return qs

    
    #################################


    def _get_values(self, group_by_product, group_by_distribution):
        default_values = ['forecast_date_truncated', 'total_forecasted_value',
                          'total_ordered_value', 'forecast_bias',
                          'forecast_bias_percent', 'forecast_mad_single', 'forecast_mape_single']


        group_by_distribution_values = self._get_group_by_distribution_value(group_by_distribution)
        group_by_product_values = self._get_group_by_product_value(group_by_product)

        qs = self.values(*group_by_distribution_values,
                         *group_by_product_values, *default_values)
        return qs

    #################################
    def get_forecast_accuracy_main_queryset(self, group_by_product, group_by_distribution, show_by, kind, start_date, end_date, forecast_version):
        # Get subquery to fetch `Orders`
        OrderDetail = apps.get_model('stock', 'OrderDetail')
        orderdetail_sub_query = OrderDetail.objects.get_orderdetail_sub_queryset(
            group_by_product, group_by_distribution, show_by, kind)

        # Filter the query by forecast date
        qs = self._filter_by_forecast_date(start_date, end_date)
        # Filter the query by forecast version
        qs = qs._filter_by_forecast_version(forecast_version)
        # Add truncated date to be able to filter by date, month, year
        qs = qs._get_forecast_date_truncated(kind)

        qs = qs._group_by(group_by_product, group_by_distribution)
        qs = qs._get_forecasted_value(show_by)
        qs = qs._get_total_forecasted_value()
        qs = qs._get_total_ordered_value(orderdetail_sub_query)
        # Calculate metrics
        qs = qs._get_forecast_bias()
        qs = qs._get_forecast_bias_percent()
        qs = qs._get_forecast_mad_single()
        qs = qs._get_forecast_mape_single()
        # Chose values to be shown
        qs = qs._get_values(group_by_product, group_by_distribution)
        return qs
####################################################
# NOTES
####################################################
''' Old way to get parent of category'''

# def _group_by_product_category_parent(self, productcategory_sub_query, level):
#     productcategory_sub_query = ProductCategory.objects.filter(level=level)
#     qs_list = []
#     for parent_category in productcategory_sub_query:
#         child_categories = parent_category.get_descendants(include_self=True)
#         qs = StockForecast.objects.filter(
#             stock__product__category__in=list(child_categories)
#         )
#         qs = qs.annotate(parent_category=Value(parent_category.reference, CharField()))
#         # qs = qs.values('parent_category')
#         qs_list.extend(list(qs))
#     return qs_list
#################################
''' These methods are replaced by '''
# def _get_values_product(self):
#     return ['stock__product__reference']

# def _get_values_product_ray(self):
#     return ['stock__product__product_ray']

# def _get_values_product_universe(self):
#     return ['stock__product__product_universe']

# def _get_values_product_category_parent(self):
#     return ['product_category_parent']

'''Deprecated functions. Pandas dataframe used instead'''
# def get_forecast_accuracy_chart_queryset(self, group_by_product, group_by_distribution, show_by, kind, group_by_date=True):
#     # * This is not working as expected. Subquery issue + double agreagation
#     # * an alternative to this method is to use directly 'forecasted_value' in the main query without subquery
#     # Get column attribute based on distribution & product (e.g. 'stock_warehouse_name')
#     qs_value = self.get_group_by_column(group_by_distribution, group_by_product)
#     if group_by_date:
#         group_by = [*qs_value, 'forecast_date_truncated']
#     else:
#         group_by = [*qs_value]

#     # Forecast subquery
#     filter_kwargs = {}
#     filter_kwargs[qs_value[0]] = OuterRef(qs_value[0])

#     if group_by_date:
#         filter_kwargs['forecast_date_truncated'] = OuterRef('forecast_date_truncated')

#     # Filter query and keep objects with the same 'group_by' and 'date' values as the main query
#     forecast_sqs = self.filter(**filter_kwargs)
#     # Group query by 'group_by' and 'date'
#     forecast_sqs = forecast_sqs.values(*group_by)
#     forecast_sqs = forecast_sqs.annotate(
#         total_forecasted_value=Sum(
#             F('forecasted_value'), output_field=FloatField())
#     )
#     forecast_sqs = forecast_sqs.values('total_forecasted_value')[:1]

#     # Orders subquery
#     OrderDetail = apps.get_model('stock', 'OrderDetail')
#     order_sqs = OrderDetail.objects.get_total_ordered_value(
#         group_by_product, group_by_distribution, show_by, kind)

#     qs = self.values(*group_by)
#     qs = qs.annotate(
#         total_forecasted_value=ExpressionWrapper(
#             Subquery(forecast_sqs), output_field=FloatField()
#         ),
#         total_ordered_value=ExpressionWrapper(
#             Subquery(order_sqs), output_field=FloatField()
#         )
#     )
#     qs = qs.annotate(
#         total_forecast_bias=ExpressionWrapper(
#             F('total_forecasted_value') - F('total_ordered_value'), output_field=FloatField()
#         )
#     )
#     qs = qs.distinct()

#     return qs

# #################################
# def get_total_forecast_bias_percent(self):
#     _sum = self.aggregate(
#         sum_total_forecast_bias_percent=ExpressionWrapper(
#             100.0 * Sum('total_forecasted_value') / Sum('total_ordered_value'), output_field=FloatField()
#         )
#     )
#     return round(_sum['sum_total_forecast_bias_percent'],2)

# def get_total_forecast_mad(self):
#     _avg = self.aggregate(
#         avg_total_forecast_mad=ExpressionWrapper(
#             Avg('forecast_mad_single'), output_field=FloatField()
#         )
#     )
#     return round(_avg['avg_total_forecast_mad'], 2)

# def get_total_forecast_mape(self):
#     _avg = self.aggregate(
#         avg_total_forecast_mape=ExpressionWrapper(
#             Avg('forecast_mape_single'), output_field=FloatField()
#         )
#     )
#     return round(_avg['avg_total_forecast_mape'], 2)
''' Old functions controling 'group_by' variable. New function more consize'''
# def _group_by_product(self, group_by_distribution):
#     value = self._get_group_by_distribution_value(group_by_distribution)
#     qs = self.values(*value,
#                      'stock__product', 'forecast_date_truncated')
#     return qs

# def _group_by_product_ray(self, group_by_distribution):
#     value = self._get_group_by_distribution_value(group_by_distribution)
#     qs = self.values(*value, 'stock__product__product_ray',
#                      'forecast_date_truncated')
#     return qs

# def _group_by_product_universe(self, group_by_distribution):
#     value = self._get_group_by_distribution_value(group_by_distribution)
#     qs = self.values(
#         *value, 'stock__product__product_universe', 'forecast_date_truncated')
#     return qs

# def _group_by_product_category_parent(self, group_by_distribution, productcategory_queryset):
#     value = self._get_group_by_distribution_value(group_by_distribution)
#     qs = self.annotate(
#         product_category_parent=ExpressionWrapper(
#             Subquery(productcategory_queryset), output_field=CharField()
#         )
#     )
#     qs = qs.values(*value, 'product_category_parent',
#                    'forecast_date_truncated')
#     return qs

# def _group_by(self, group_by_product, group_by_distribution):
#     if group_by_product == 'product':
#         qs = self._group_by_product(group_by_distribution)
#     elif group_by_product == 'product_ray':
#         qs = self._group_by_product_ray(group_by_distribution)
#     elif group_by_product == 'product_universe':
#         qs = self._group_by_product_universe(group_by_distribution)
#     elif group_by_product == 'product_category_parent_level_0':
#         ProductCategory = apps.get_model('stock', 'ProductCategory')
#         sub_qs = ProductCategory.objects.get_productcategory_parent_sub_queryset(
#             level=0)
#         qs = self._group_by_product_category_parent(
#             group_by_distribution, sub_qs)
#     elif group_by_product == 'product_category_parent_level_1':
#         ProductCategory = apps.get_model('stock', 'ProductCategory')
#         sub_qs = ProductCategory.objects.get_productcategory_parent_sub_queryset(
#             level=1)
#         qs = self._group_by_product_category_parent(
#             group_by_distribution, sub_qs)
#     elif group_by_product == 'product_category_parent_level_2':
#         ProductCategory = apps.get_model('stock', 'ProductCategory')
#         sub_qs = ProductCategory.objects.get_productcategory_parent_sub_queryset(
#             level=2)
#         qs = self._group_by_product_category_parent(
#             group_by_distribution, sub_qs)
#     return qs
