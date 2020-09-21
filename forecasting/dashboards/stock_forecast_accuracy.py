import copy
import datetime

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from django.db.models import OuterRef
from django_pandas.io import read_frame
from django_plotly_dash import DjangoDash

from common import utils as common_utils
from common.dashboards import dash_constants, dash_utils
from ..models import StockForecast

app = DjangoDash('StockForecastAccuracy', add_bootstrap_links=True)

### Used IDs ###
prefix = 'stock-forecast-accuracy'
# Filter IDs
dropdown_group_by_product_field_id = prefix + '-dropdown-group-by-product-field'
dropdown_group_by_distribution_field_id = prefix + '-dropdown-group-by-distribution-field'
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

### Global variable ###
# forecast_version_list = list(StockForecast.objects.get_forecast_versions())
forecast_version_list = []

def filter_container():
    filter_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_group_by_distribution_dropdown(
                    dropdown_group_by_distribution_field_id),
            ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_group_by_product_dropdown(
                    dropdown_group_by_product_field_id),
            ], sm=12, md=4, lg=4),

            dbc.Col([
                dash_utils.get_kind_dropdown(
                    dropdown_kind_id, 
                    label='Grouping period', 
                    value='day'
                ),
            ], sm=12, md=4, lg=4),
            dbc.Col([
                dbc.Label('Show by'),
                dcc.Dropdown(
                    id=dropdown_show_by_id,
                    options=[
                        {'label': 'Quantity (Unit)', 'value': 'quantity'},
                        {'label': 'Quantity (Package)', 'value': 'package'},
                        {'label': 'Quantity (Pallet)', 'value': 'pallet'},
                        {'label': 'Cost (DH)', 'value': 'cost'},
                        {'label': 'Weight (Kg)', 'value': 'weight'},
                        {'label': 'Volume (m3)', 'value': 'volume'},
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
                        {'label': dt, 'value': dt} for dt in forecast_version_list
                    ],
                    value=[forecast_version_list[0]
                           if forecast_version_list else None],
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


def chart_1(df, kind, group_by_query_column, group_by_label, dropdown_y_axis):
    df_chart = df.groupby([group_by_query_column, 'forecast_date_truncated'])[
        'total_forecasted_value', 'total_ordered_value', 'forecast_bias'].sum().reset_index()
    df_chart = df_chart.to_dict('records')

    df_chart_grouped = common_utils.group_data_by_category(
        df_chart,
        category_key=group_by_query_column,
        x_key='forecast_date_truncated',
        y_key=dropdown_y_axis
    )

    chartdata = common_utils.build_chart_series(df_chart_grouped, chart_type='Scatter')

    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Forecast Bias by Date by {}'.format(
        group_by_label.capitalize())
    chart_layout['xaxis'] = dict(
        title='Date in {}s'.format(kind.capitalize()))
    chart_layout['yaxis'] = dict(title='Forecast Bias')

    figure = {'data': chartdata, 'layout': chart_layout}
    return figure

def chart_2(df, show_by, group_by_query_column, group_by_label):
    df_chart = df.groupby([group_by_query_column])[
        'total_forecasted_value', 'total_ordered_value', 'forecast_bias'].sum().reset_index()

    chartdata = [
        go.Scatter(
            x=df_chart[group_by_query_column],
            y=df_chart['total_forecasted_value'],
            name='Forecasted value ({})'.format(show_by),
        ),
        go.Scatter(
            x=df_chart[group_by_query_column],
            y=df_chart['total_ordered_value'],
            name='Ordered value ({})'.format(show_by),
        ),
        go.Bar(
            x=df_chart[group_by_query_column],
            y=df_chart['forecast_bias'],
            name='Forecast bias',
        ),
    ]
    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Forecast VS. Order Values by {}'.format(
        group_by_label.capitalize())
    chart_layout['xaxis'] = dict(
        title='{}s'.format(group_by_label.capitalize()))
    chart_layout['yaxis'] = dict(title='Values')

    figure = {'data': chartdata, 'layout': chart_layout}
    return figure

@app.callback(
    [
        # Dataframe
        Output(table_forecast_dataframe_id, 'data'),
        Output(table_forecast_dataframe_id, 'columns'),
        # Mini-cards
        Output(mini_card_subtitle_bias_percent_id, 'children'),
        Output(mini_card_subtitle_mad_id, 'children'),
        Output(mini_card_subtitle_mape_id, 'children'),
        # Charts
        Output(chart_by_date_by_group_id, 'figure'),
        Output(chart_by_group_id, 'figure'),
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
    forecast_start_date,
    forecast_end_date,
    kind,
    show_by,
    forecast_version,
    dropdown_y_axis):
    # Get queryset
    qs = StockForecast.objects.get_forecast_accuracy_main_queryset(
        group_by_product, group_by_distribution, show_by, kind, 
        forecast_start_date, forecast_end_date, forecast_version)
    # Convert queryset to dataframe
    df = read_frame(qs)

    ### Dataframe ###
    # Prepare data & columns to be returned
    data = df.round(2).to_dict('records')
    columns = [{"name": i, "id": i} for i in df.columns]

    ### Charts ###
    # Get group_by column
    group_by_query_column = qs.get_group_by_column(
        group_by_distribution, group_by_product)
    # Get the label of group_by
    group_by_label = group_by_distribution if group_by_distribution else group_by_product
    # Chart 1
    figure_1 = chart_1(
        df, kind, group_by_query_column[0], group_by_label, dropdown_y_axis)
    # Chart 2
    figure_2 = chart_2(df, show_by, group_by_query_column[0], group_by_label)
    


    ### Mini-cards ###
    # Compute forecast bias
    forecast_bias_avg = round(
        100 * df['total_forecasted_value'].sum() / df['total_ordered_value'].sum(), 2)
    # Compute forecast MAD
    forecast_mad_avg = df['forecast_mad_single'].mean().round(2)
    # Compute forecast MAPE
    forecast_mape_avg = df['forecast_mape_single'].mean().round(2)

    return (data, columns, forecast_bias_avg, forecast_mad_avg,
            forecast_mape_avg, figure_1, figure_2)

###############################################################
# NOTES SECTION
###############################################################
'''Old way to convert queryset to Pandas'''
# from django.db import connection
# # Get raw sql to use it with Pandas
# sql, params = qs.query.sql_with_params()
# # Create dataframe
# df = pd.read_sql_query(sql, connection, params=params)
'''Old way to plot graph based on queryset instead of dataframe'''
# # Chart 2
# chart_qs_2  = qs.get_forecast_accuracy_chart_queryset(
#     group_by_product, group_by_distribution, show_by, kind, group_by_date=False)
# chart_qs_2 = chart_qs_2 .order_by('total_forecast_bias')

# chartdata_2 = [
#     go.Scatter(
#         x=list(chart_qs_2.values_list(
#             qs_value[0], flat=True)),
#         y=list(chart_qs_2.values_list(
#             'total_forecasted_value', flat=True)),
#         name='Forecasted value ({})'.format(show_by),
#     ),
#     go.Scatter(
#         x=list(chart_qs_2.values_list(
#             qs_value[0], flat=True)),
#         y=list(chart_qs_2.values_list(
#             'total_ordered_value', flat=True)),
#         name='Ordered value ({})'.format(show_by),
#     ),
#     go.Bar(
#         x=list(chart_qs_2.values_list(
#             qs_value[0], flat=True)),
#         y=list(chart_qs_2.values_list(
#             'total_forecast_bias', flat=True)),
#         name='Forecast bias',
#     ),
# ]
''' Old way to compute mini-cards values'''
# ### Mini-cards ###
# # Compute forecast bias
# total_forecast_bias = qs.get_total_forecast_bias_percent()
# # Compute forecast MAD
# total_forecast_mad = qs.get_total_forecast_mad()
# # Compute forecast MAPE
# total_forecast_mape = qs.get_total_forecast_mape()

