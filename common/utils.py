import itertools
from operator import itemgetter
import plotly.graph_objs as go
from django.db.models.functions import (
        TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDay)
        
def add_trunc_date(queryset, field_name, kind, prefix=''):
    """Truncate a datetime field based on `kind` argument and annotate it to the queryset

    Parameters
    ----------
    models : [type]
        [description]
    field_name : str
        Model's field to be truncated
    kind : str
        Represents a date part. Possible values are `year`, `quarter`, `month`, `week` or `day`

    Returns
    -------
    queryset
        Truncated date as a new field named `<field_name>_truncated` to queryset
    """
    # Name the field that will be used as output for annotation
    output_field_name = field_name + '_truncated'
    # Build truncation function name, e.g. TruncYear('inventory_date')
    trunc_function = 'Trunc{kind}("{prefix}{field_name}")'.format(
        kind=kind.capitalize(), prefix=prefix, field_name=field_name)

    annotate_kwargs = {output_field_name: eval(trunc_function)}

    qs = queryset.annotate(**annotate_kwargs)
    return qs


def group_data_by_category(queryset, category_key, x_key, y_key):
    '''
    input = queryset([
        {'category_key': 'Cat001', 'x_key': 1, 'y_key': 0},
        {'category_key': 'Cat001', 'x_key': 2, 'y_key': 1},
        {'category_key': 'Cat002', 'x_key': 1, 'y_key': 0},
    ])
    output = dict({
        'Cat001': [
            {'x': [1, 2]},
            {'y': [0, 1]}
        ],
        'Cat002': [
            {'x': [1]},
            {'y': [0]}
        ]
    })
    '''
    X = 'x'
    Y = 'y'
    # Sort queryset data by category key
    dataset = sorted(list(queryset), key=itemgetter(category_key))
    # Return data grouped by category
    dataset_grouped_by_category = {}
    for key, value in itertools.groupby(dataset, key=itemgetter(category_key)):
        dataset_grouped_by_category[key] = {}
        dataset_grouped_by_category[key][X] = []
        dataset_grouped_by_category[key][Y] = []
        for v in value:
            dataset_grouped_by_category[key][X].append(v.get(x_key))
            dataset_grouped_by_category[key][Y].append(v.get(y_key))
    # print(dataset_grouped_by_category) # NOTE : print alerte
    return dataset_grouped_by_category



def build_chart_series(grouped_data, chart_type='Bar', x_key='x', y_key='y'):
    '''
    Build data to plot in chart
    input = grouped data returned by function `group_data_by_category`
    output = data ready for the chart
    '''
    chartdata = []
    for key, value in grouped_data.items():
        chartdata.append(
            eval('go.' + chart_type)(
                x=value[x_key],
                y=value[y_key],
                name=key,
                # mode='markers',
            )
        )
    return chartdata
