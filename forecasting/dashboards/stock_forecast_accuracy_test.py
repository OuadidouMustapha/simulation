from stock.models import Order
from django.utils.translation import gettext as _
import copy
import datetime

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go

import cufflinks as cf
cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True


from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from django.db.models import OuterRef
from django_pandas.io import read_frame
from django_plotly_dash import DjangoDash

from common import utils as common_utils
from common.dashboards import dash_constants, dash_utils
from ..models import StockForecast

app = DjangoDash('StockForecastAccuracyTest', add_bootstrap_links=True)

### Used IDs ###
prefix = 'stock-forecast-accuracy-test'
# Filter IDs
dropdown_group_by_product_field_id = prefix + '-dropdown-group-by-product-field'
dropdown_group_by_distribution_field_id = prefix + \
    '-dropdown-group-by-distribution-field'
dropdown_kind_id = prefix + '-dropdown-kind'
dropdown_show_by_id = prefix + '-dropdown-show-by'
input_date_range_id = prefix + '-input-date-range'
dropdown_forecast_version_id = prefix + '-dropdown-forecast-version'
# Mini-cards IDs
mini_card_subtitle_bias_percent_id = prefix + 'mini-card-subtitle-bias-percent'
mini_card_subtitle_mad_id = prefix + 'mini-card-subtitle-mad'
mini_card_subtitle_mape_id = prefix + 'mini-card-subtitle-mape'
# Charts IDs
chart_by_date_by_group_id = prefix + 'chart-by-date-by-group'
chart_dropdown_y_axis_id = prefix + 'chart-filter-y-axis'
chart_by_group_id = prefix + 'chart-by-group'
# Dataframe ID
table_forecast_dataframe_id = prefix + '-table-forecast-dataframe'



def filter_container():
    filter_container = html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Label('Distribution field'),
                    dcc.Dropdown(
                        id=dropdown_group_by_distribution_field_id,
                        options=[
                            {'label': '-None-', 'value': ''},
                            {'label': 'Warehouse', 'value': 'warehouse'},
                            {'label': 'Customer', 'value': 'customer'},
                            {'label': 'Circuit', 'value': 'circuit'},
                            # {'label': 'Sub-Circuit', 'value': 'sub_circuit'},
                        ],
                        value='warehouse',
                    ),
                ])
            ], sm=12, md=4, lg=4),
            dbc.Col([
                html.Div([
                    dbc.Label('Product field'),
                    dcc.Dropdown(
                        id=dropdown_group_by_product_field_id,
                        options=[
                            {'label': '-None-', 'value': ''},
                            {'label': 'Product', 'value': 'product'},
                            # {'label': 'Product Rayon',
                            #     'value': 'product__product_ray'},
                            # {'label': 'Product Universe',
                            #     'value': 'product_universe'},
                            {'label': 'Product Type',
                                'value': 'product__product_type'},
                            # {'label': 'Category',
                            #  'value': 'product__product_category'},
                            # {'label': 'Sub-Category',
                            #  'value': 'product_category'},
                        ],
                        value='product',
                    ),
                ])
            ], sm=12, md=4, lg=4),

            dbc.Col([
                html.Div([
                    dbc.FormGroup([
                        dbc.Label(_('Grouping period')),
                        dcc.Dropdown(
                            id=dropdown_kind_id,
                            options=[
                                {'label': 'Year', 'value': '%Y'},
                                # {'label': 'Quarter', 'value': 'quarter'},
                                {'label': 'Month', 'value': '%Y-%b'},
                                {'label': 'Week', 'value': '%Y-Week%W'},
                                {'label': 'Day', 'value': '%Y-%b-%d'}
                            ],
                            value='%Y-%b-%d',
                        )
                    ]),
                ])
            ], sm=12, md=4, lg=4),
            dbc.Col([
                dbc.Label('Show by'),
                dcc.Dropdown(
                    id=dropdown_show_by_id,
                    options=[
                        {'label': 'Quantity (Unit)', 'value': 'quantity'},
                        # {'label': 'Quantity (Package)', 'value': 'package'},
                        # {'label': 'Quantity (Pallet)', 'value': 'pallet'},
                        {'label': 'Cost (DH)', 'value': 'cost'},
                        # {'label': 'Weight (Kg)', 'value': 'weight'},
                        # {'label': 'Volume (m3)', 'value': 'volume'},
                    ],
                    value='quantity',
                ),

            ], sm=12, md=4, lg=4),
            dbc.Col([
                dbc.Label('Forecast version'),
                dcc.Dropdown(
                    id=dropdown_forecast_version_id,
                    placeholder='Forecasting version',
                    options=[
                        # {'label': dt, 'value': dt} for dt in forecast_version_list
                    ],
                    value=[],
                    # value=[forecast_version_list[0]
                    #        if forecast_version_list else None],
                ),
            ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_date_range(
                    input_date_range_id,
                    label='Time horizon',
                    year_range=5
                ),
            ], sm=12, md=4, lg=4),
        ])
    ])
    return filter_container


def body_container():
    body_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_mini_card(mini_card_subtitle_bias_percent_id, title='Forecast bias %',
                                         subtitle='', icon='')
            ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_mini_card(mini_card_subtitle_mad_id, title='Mean absolute deviation (MAD)',
                                         subtitle='', icon='')
            ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_mini_card(mini_card_subtitle_mape_id, title='Mean absolute percentage error % (MAPE)',
                                         subtitle='', icon='')
            ], sm=12, md=4, lg=4),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(
                    chart_by_date_by_group_id,
                    filter_div=dbc.Col([
                        dcc.Dropdown(
                            id=chart_dropdown_y_axis_id,
                            options=[
                                {'label': 'Forecast Bias',
                                    'value': 'forecast_bias'},
                                {'label': 'Forecasted Value',
                                 'value': 'total_forecasted_value'},
                                {'label': 'Ordered Value',
                                    'value': 'total_ordered_value'},
                            ],
                            value='forecast_bias',
                        ),

                    ])
                )
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_by_group_id)
            ], sm=12, md=6, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_datatable_card(table_forecast_dataframe_id)
            ], sm=12, md=12, lg=12),
        ]),
    ])
    return body_container


app.layout = dash_utils.get_dash_layout(filter_container(), body_container())

@app.callback(
    [
        # Dataframe
        Output(table_forecast_dataframe_id, 'data'),
        Output(table_forecast_dataframe_id, 'columns'),
    ],
    [
        Input(dropdown_group_by_product_field_id, 'value'),
        Input(dropdown_group_by_distribution_field_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(dropdown_kind_id, 'value'),
        Input(dropdown_show_by_id, 'value'),
        Input(dropdown_forecast_version_id, 'value'),
        Input(chart_dropdown_y_axis_id, 'value'),
    ]
)
def dataframe_date_filter(
        group_by_product,
        group_by_distribution,
        start_date,
        end_date,
        kind,
        show_by,
        forecast_version,
        dropdown_y_axis):

    # Define group_by
    group_by = []
    if group_by_product:
        group_by.append(group_by_product)
    if group_by_distribution:
        group_by.append(group_by_distribution)

    # # Define kind
    # if kind = 'year':
    #     kind_format = '%Y'
    # elif kind = 'month':
    #     kind_format = '%Y'

    # group_by = {
    #     0: ['product'],
    #     1: ['warehouse'],
    #     2: ['circuit'],
    #     3: ['customer'],
    #     4: ['product__type'],
    #     5: ['product__type', 'warehouse'],
    #     6: ['product__type', 'circuit'],
    #     7: ['product__type', 'customer'],
    # }

    # Get queryset
    forecast_qs = StockForecast.objects.get_forecasting(
        warehouse_filter=None, product_filter=None, circuit_filter=None, start_date=start_date, end_date=end_date)

    order_qs = Order.objects.get_forecasting(
        warehouse_filter=None, product_filter=None, circuit_filter=None, start_date=start_date, end_date=end_date)

    # Convert queryset to dataframe and assign the right column type
    forecast_df = read_frame(forecast_qs)
    forecast_df['forecast_date'] = forecast_df['forecast_date'].astype('datetime64[ns]')

    order_df = read_frame(order_qs)
    order_df['ordered_at'] = order_df['ordered_at'].astype('datetime64[ns]')

    # Group by order_date and aggregate
    forecast_df['forecast_date'] = forecast_df['forecast_date'].dt.strftime(kind)
    forecast_df = forecast_df.groupby([*group_by, 'forecast_date'], as_index=False).agg(
        {'forecasted_quantity': 'sum'})

    order_df['ordered_at'] = order_df['ordered_at'].dt.strftime(kind)
    order_df = order_df.groupby([*group_by, 'ordered_at'], as_index=False).agg(
        {'ordered_quantity': 'sum'})

    merged_df = pd.merge(forecast_df, order_df, how='left', left_on=[
        *group_by, 'forecast_date'], right_on=[*group_by, 'ordered_at'])  # .dropna()

    # Prepare data & columns to be returned
    data = merged_df.to_dict('records')
    columns = [{"name": i, "id": i} for i in merged_df.columns]

    # df = pd.DataFrame.from_dict(data)
    # df = df[(df['warehouse'].isin(warehouse_list)) & (df['circuit'].isin(
    #     circuit_list)) & (df['product_range'].isin(product_range_list))]
    # group_by_list = ['warehouse', 'circuit', 'product', 'product_range']

    # show_by_axis = {
    #     'quantity': ['forecasted_by_quantity', 'sold_by_quantity', 'bias_quantity'],
    #     'cost': ['forecasted_by_cost', 'sold_by_cost', 'bias_cost'],
    #     'volume': ['forecasted_by_volume', 'sold_by_volume', 'bias_volume'],
    # }
    # df_copy = df.groupby([group_by], as_index=False).agg({show_by_axis[show_by][0]: 'sum', show_by_axis[show_by][1]: 'sum', show_by_axis[show_by][2]: 'sum'})
    # fig1 = df_copy.sort_values(by=[show_by_axis[show_by][2]], ascending=False).iplot(asFigure=True, kind='bar', x=group_by, y=[show_by_axis[show_by][0], show_by_axis[show_by][1], show_by_axis[show_by][2]], theme='white', title='Title {}'.format(group_by.capitalize()),
    #                                                                                  xTitle='xTitle', yTitle='xTitle')




    return data, columns

