import itertools
from operator import itemgetter
import plotly.graph_objs as go
from django.db.models.functions import (
    TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDay)

# TODO : use classes instead of methods (queryset class, plotly_data class...)

def trunc_date_attribute(queryset, attribute_name, trunc_period='day'):
    """Add truncated attribute to queryset

    Parameters
    ----------
    queryset : queryset
        Query object with datetime attribute.
    attribute_name : str
        Name of datetime attribute in the query.
    trunc_period : str
        Possible options are: 'year', 'quarter', 'month', 'week', 'day', by default 'day'

    Returns
    -------
    queryset
        Annotate a new value to queryset having the name `<attribute_name>_truncated` with the truncated date.
    """
    truncated_attribute_name = attribute_name + '_truncated'
    annotate_kwargs = {}

    if trunc_period == 'year':
        annotate_kwargs[truncated_attribute_name] = TruncYear(
            attribute_name)
        pass
    elif trunc_period == 'quarter':
        annotate_kwargs[truncated_attribute_name] = TruncQuarter(
            attribute_name)

    elif trunc_period == 'month':
        annotate_kwargs[truncated_attribute_name] = TruncMonth(
            attribute_name)

    elif trunc_period == 'week':
        annotate_kwargs[truncated_attribute_name] = TruncWeek(
            attribute_name)

    elif trunc_period == 'day':
        annotate_kwargs[truncated_attribute_name] = TruncDay(
            attribute_name)
    else:
        # Value by default is `day`
        annotate_kwargs[truncated_attribute_name] = TruncDay(
            attribute_name)

    qs = queryset.annotate(**annotate_kwargs)

    return qs


def convert_group_by_field_to_attribute(group_by_field, model):
    if model == 'StockControl':
        if group_by_field == 'product':
            return 'stock__product'
        elif group_by_field == 'category':
            return 'stock__product__category'
    elif model == 'SaleDetail':
        if group_by_field == 'product':
            return 'stock__product'
        elif group_by_field == 'category':
            return 'stock__product__category'
    else:
        if group_by_field == 'product':
            return 'product'
        elif group_by_field == 'category':
            return 'product__category'



def build_scatter_chart(grouped_data, x_key='x', y_key='y'):
    '''
    This is used for building chart scatter
    '''
    from django.contrib.admin.utils import flatten

    chartdata = []
    x = []
    y = []

    # # Plot data grouped by category or product
    # for key, value in grouped_data.items():
    #     chartdata.append(
    #         go.Scatter(
    #             x=value[x_key],
    #             y=value[y_key],
    #             name=key,
    #             mode='markers',
    #         ),
    #     )

    for _, value in grouped_data.items():
        x.append(value[x_key])
        y.append(value[y_key])

    chartdata.append(
        go.Scatter(
            x=flatten(x),
            y=flatten(y),
            # name=key,
            mode='markers',
        ),
    )
    return chartdata


def count_dio_average_by_level_range(queryset, dio_level_low, dio_level_high, category_key, x_key):
    '''
    If we suppose:
    dio_level_low = 2 
    dio_level_high = 4
    category_key = 'product__reference'
    x_key = 'avg_dio'

    dio_occurence_lev1 = count(avg_dio) where (0 <= avg_dio < dio_level_low)
    dio_occurence_lev2 = count(avg_dio) where (dio_level_low <= avg_dio < dio_level_high)
    dio_occurence_lev3 = count(avg_dio) where (dio_level_high <= avg_dio)

    input = queryset([
        {'product__reference': 'Sku001', 'avg_dio': 1},
        {'product__reference': 'Sku001', 'avg_dio': 4},
        {'product__reference': 'Sku001', 'avg_dio': 3},
        {'product__reference': 'Sku002', 'avg_dio': 0.5},
        {'product__reference': 'Sku002', 'avg_dio': 8},
    ])

    output = dict({
        'Sku001': [
            {'dio_occurence_lev1': 1},
            {'dio_occurence_lev2': 1},
            {'dio_occurence_lev3': 1},
        ],
        'Sku002': [
            {'dio_occurence_lev1': 1},
            {'dio_occurence_lev2': 0},
            {'dio_occurence_lev3': 1},
        ]
    })
    '''
    lev1 = 'dio_occurence_lev1'
    lev2 = 'dio_occurence_lev2'
    lev3 = 'dio_occurence_lev3'
    none = 'dio_occurence_none'
    # Sort queryset data by category key
    dataset = sorted(list(queryset), key=itemgetter(category_key))
    # print(queryset) # NOTE : print alerte
    # Return data grouped by category
    dataset_grouped_by_category = {}
    for key, value in itertools.groupby(dataset, key=itemgetter(category_key)):
        dataset_grouped_by_category[key] = {}
        dataset_grouped_by_category[key][lev1] = 0
        dataset_grouped_by_category[key][lev2] = 0
        dataset_grouped_by_category[key][lev3] = 0
        dataset_grouped_by_category[key][none] = 0
        for v in value:
            if (float(v.get(x_key)) >= 0) and (float(v.get(x_key)) < float(dio_level_low)):
                dataset_grouped_by_category[key][lev1] += 1
            elif (float(v.get(x_key)) >= float(dio_level_low)) and (float(v.get(x_key)) < float(dio_level_high)):
                dataset_grouped_by_category[key][lev2] += 1
            elif (float(v.get(x_key)) >= float(dio_level_high)):
                dataset_grouped_by_category[key][lev3] += 1
            else:
                dataset_grouped_by_category[key][none] += 1
    # print(dataset_grouped_by_category) # NOTE  print() alert
    return dataset_grouped_by_category


def build_dio_chart_series(grouped_data, dio_level_low, dio_level_high):
    '''
    Build data to plot in chart
    input = grouped data returned by function `group_data_by_category`
    output = data ready for the chart
    '''
    chartdata = []
    X_cat = []
    Y_lev1 = []
    Y_lev2 = []
    Y_lev3 = []
    for key, value in grouped_data.items():
        X_cat.append(key)
        Y_lev1.append(value['dio_occurence_lev1'])
        Y_lev2.append(value['dio_occurence_lev2'])
        Y_lev3.append(value['dio_occurence_lev3'])
        

    chartdata = [
        go.Bar(
            x=X_cat,
            y=Y_lev1,
            name='DIO less than {} (days)'.format(dio_level_low),
        ),
        go.Bar(
            x=X_cat,
            y=Y_lev2,
            name='DIO between [{}, {}[ (days)'.format(
                dio_level_low, dio_level_high),
        ),
        go.Bar(
            x=X_cat,
            y=Y_lev3,
            name='DIO more than {} (days)'.format(dio_level_high),
        ),
    ]
    return chartdata


##############################################
# Updated version
##############################################


def get_show_by_attribute(show_by):
    if show_by == 'quantity':
        return
    elif show_by == 'package':
        return 'stock__product__package'
    elif show_by == 'pallet':
        return 'stock__product__pallet'
    elif show_by == 'cost':
        return 'stock__product__cost'
    elif show_by == 'weight':
        return 'stock__product__weight'
    elif show_by == 'volume':
        return 'stock__product__volume'
