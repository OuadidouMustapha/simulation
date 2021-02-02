from stock.models import Product, Warehouse, Circuit, Customer, OrderDetail, Order
from django.utils.translation import gettext as _
import copy
import datetime

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
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
from ..models import Forecast, Version

app = DjangoDash('ForecastAccuracy', add_bootstrap_links=True)


# Prepare html ids
_prefix = 'stock-forecast-accuracy'
# Global filter
dropdown_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_warehouse_list_id')
div_warehouse_list_id =  dash_utils.generate_html_id(_prefix, 'div_warehouse_list_id')
checkbox_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_warehouse_list_id')

dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')
details_product_range_list_id = dash_utils.generate_html_id(_prefix, 'details_product_range_list_id')

dropdown_circuit_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_circuit_list_id')
div_circuit_list_id = dash_utils.generate_html_id(_prefix, 'div_circuit_list_id')
checkbox_circuit_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_circuit_list_id')

dropdown_product_range_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_range_list_id')
div_product_range_list_id = dash_utils.generate_html_id(_prefix, 'div_product_range_list_id')
checkbox_product_range_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_range_list_id')

dropdown_customer_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_customer_list_id')
div_customer_list_id = dash_utils.generate_html_id(_prefix, 'div_customer_list_id')
checkbox_customer_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_customer_list_id')

dropdown_version_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_version_list_id')
input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

# Mini-cards IDs & datatables
# Mini card 1
mini_card_subtitle_bias_percent_id = dash_utils.generate_html_id(_prefix, 'mini_card_subtitle_bias_percent_id')
mini_card_dropdown_bias_percent_id = dash_utils.generate_html_id(_prefix, 'mini_card_dropdown_bias_percent_id')
mini_card_datatable_bias_percent_id = dash_utils.generate_html_id(_prefix, 'mini_card_datatable_bias_percent_id')
chart_bias_id = dash_utils.generate_html_id(_prefix, 'chart_bias_id')
# Mini card 2
mini_card_subtitle_mad_id = dash_utils.generate_html_id(_prefix, 'mini_card_subtitle_mad_id')
mini_card_dropdown_mad_id = dash_utils.generate_html_id(_prefix, 'mini_card_dropdown_mad_id')
mini_card_datatable_mad_id = dash_utils.generate_html_id(_prefix, 'mini_card_datatable_mad_id')
chart_mad_id = dash_utils.generate_html_id(_prefix, 'chart_mad_id')
# Mini card 3
mini_card_subtitle_mape_id = dash_utils.generate_html_id(_prefix, 'mini_card_subtitle_mape_id')
mini_card_dropdown_mape_id = dash_utils.generate_html_id(_prefix, 'mini_card_dropdown_mape_id')
mini_card_datatable_mape_id = dash_utils.generate_html_id(_prefix, 'mini_card_datatable_mape_id')
chart_mape_id = dash_utils.generate_html_id(_prefix, 'chart_mape_id')

# Charts
# Chart right
# Local filter
dropdown_chart_1_forecast_version_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_forecast_version_id')
dropdown_chart_1_group_by_product_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_group_by_product_id')
dropdown_chart_1_group_by_distribution_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_group_by_distribution_id')
dropdown_chart_1_kind_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_kind_id')
dropdown_chart_1_show_by_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_show_by_id')

chart_1_1_id = dash_utils.generate_html_id(_prefix, 'chart_1_1_id')
chart_1_2_id = dash_utils.generate_html_id(_prefix, 'chart_1_2_id')
chart_1_3_id = dash_utils.generate_html_id(_prefix, 'chart_1_3_id')

dropdown_chart_1_2_y_column_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_2_y_column_id')
dropdown_chart_1_3_metric_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_1_3_metric_id')

# Chart left
# Local filter
dropdown_chart_2_forecast_version_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_forecast_version_id')
dropdown_chart_2_group_by_product_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_group_by_product_id')
dropdown_chart_2_group_by_distribution_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_group_by_distribution_id')
dropdown_chart_2_kind_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_kind_id')
dropdown_chart_2_show_by_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_show_by_id')

chart_2_1_id = dash_utils.generate_html_id(_prefix, 'chart_2_1_id')
chart_2_2_id = dash_utils.generate_html_id(_prefix, 'chart_2_2_id')
chart_2_3_id = dash_utils.generate_html_id(_prefix, 'chart_2_3_id')

dropdown_chart_2_2_y_column_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_2_y_column_id')
dropdown_chart_2_3_metric_id = dash_utils.generate_html_id(_prefix, 'dropdown_chart_2_3_metric_id')


# Dataframe ID
table_forecast_dataframe_id = dash_utils.generate_html_id(_prefix, 'table_forecast_dataframe_id')

# Prepare data for dropdown filters
_all_products = list(Product.objects.get_all_products())
_all_products_type = list(Product.objects.get_all_products_by_attribute(attribute='category__reference'))
_all_warehouses = list(Warehouse.objects.get_all_warehouses())
_all_circuits = list(Circuit.objects.get_all_circuits())
_all_customers = list(Customer.objects.get_all_customers())
_select_all_option = {'label': _('All'), 'value': ''}
_all_customers.insert(0, _select_all_option.copy())
_all_versions = list(Version.objects.get_all_versions())

# print(_all_warehouses)
def filter_container():
    filter_container = html.Div([
        dbc.Row([
            html.Details([
                html.Summary(_('Products')),
                dbc.Col([
                    dash_utils.get_filter_dropdown(
                        dropdown_product_list_id, div_product_list_id, checkbox_product_list_id, _all_products, '')

                ], sm=12, md=12, lg=12),
            ], id=details_product_list_id, open=False), 
        ]),
        dbc.Row([
            html.Details([
                html.Summary(_('Products type')),
                dbc.Col([
                    dash_utils.get_filter_dropdown(
                        dropdown_product_range_list_id, div_product_range_list_id, checkbox_product_range_list_id, _all_products_type, '')

                ], sm=12, md=12, lg=12),
            ], id=details_product_range_list_id, open=False),
        ]),
        dbc.Row([

            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id, _all_warehouses, _('Warehouses'))

            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_circuit_list_id, div_circuit_list_id, checkbox_circuit_list_id, _all_circuits, _('Circuits'))

            ], sm=12, md=6, lg=2),
            # dbc.Col([
            #     dash_utils.get_filter_dropdown(
            #         dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id, _all_customers, _('Customers'))

            # ], sm=12, md=6, lg=3),
            dbc.Col([
                dbc.Label(_('Customers')),
                dcc.Dropdown(
                    id=dropdown_customer_list_id,
                    options=_all_customers, 
                    value='',
                ),
            ], sm=12, md=6, lg=2),
            dbc.Col([
                dbc.Label(_('Forecast version')),
                dcc.Dropdown(
                    id=dropdown_version_list_id,
                    placeholder=_('Forecast version'),
                    options=_all_versions,
                    value=_all_versions[-1]['value'] if _all_versions else None,
                ),
            ], sm=12, md=6, lg=2),
            dbc.Col([
                dash_utils.get_date_range(
                    input_date_range_id,
                    label=_('Time horizon'),
                    year_range=1
                ),
            ], sm=12, md=6, lg=3),
        ]),
    ])
    return filter_container


def body_container():
    body_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_mini_card(
                    mini_card_subtitle_bias_percent_id,
                    title=_('Forecast bias %'),
                    dropdown_div=html.Div([
                        dbc.Label(_('Lowest rates grouped by:')),
                        dcc.Dropdown(
                            id=mini_card_dropdown_bias_percent_id,
                            options=[
                                {'label': _('Warehouse'),
                                'value': 'warehouse'},
                                {'label': _('Customer'),
                                'value': 'customer'},
                                {'label': _('Circuit'),
                                'value': 'circuit'},
                                {'label': _('Product'),
                                'value': 'product'},
                                {'label': _('Product Type'),
                                'value': 'product__product_type'},
                            ],
                        value='warehouse',
                        ),
                    ]),
                    datatable_div=html.Div([
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_bias_id)
                            ]),
                        ),
                        dcc.Loading(
                            dash_table.DataTable(
                                id=mini_card_datatable_bias_percent_id,
                            ),
                        ),
                    ]),
                )
            ], sm=12, md=4, lg=4), 
            dbc.Col([
                dash_utils.get_mini_card(
                    mini_card_subtitle_mad_id,
                    title=_('Mean absolute deviation (MAD)'),
                    dropdown_div=html.Div([
                        dbc.Label(_('Highest values grouped by:')),
                        dcc.Dropdown(
                            id=mini_card_dropdown_mad_id,
                            options=[
                                {'label': _('Warehouse'),
                                'value': 'warehouse'},
                                {'label': _('Customer'),
                                'value': 'customer'},
                                {'label': _('Circuit'),
                                'value': 'circuit'},
                                {'label': _('Product'),
                                'value': 'product'},
                                {'label': _('Product Type'),
                                'value': 'product__product_type'},
                            ],
                        value='warehouse',
                        ),
                    ]),
                    datatable_div=html.Div([
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_mad_id)
                            ]),
                        ),
                        dcc.Loading(
                            dash_table.DataTable(
                                id=mini_card_datatable_mad_id,
                            ),
                        ),
                    ]),
                )
            ], sm=12, md=4, lg=4), 
            dbc.Col([
                dash_utils.get_mini_card(
                    mini_card_subtitle_mape_id,
                    title=_('Mean absolute percentage error % (MAPE)'),
                    dropdown_div=html.Div([
                        dbc.Label(_('Highest rates grouped by:')),
                        dcc.Dropdown(
                            id=mini_card_dropdown_mape_id,
                            options=[
                                {'label': _('Warehouse'),
                                'value': 'warehouse'},
                                {'label': _('Customer'),
                                'value': 'customer'},
                                {'label': _('Circuit'),
                                'value': 'circuit'},
                                {'label': _('Product'),
                                'value': 'product'},
                                {'label': _('Product Type'),
                                'value': 'product__product_type'},
                            ],
                        value='warehouse',
                        ),
                    ]),
                    datatable_div=html.Div([
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_mape_id)
                            ]),
                        ),
                        dcc.Loading(
                            dash_table.DataTable(
                                id=mini_card_datatable_mape_id,
                            ),
                        ),
                    ]),
                )
            ], sm=12, md=4, lg=4), 

        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(
                    chart_1_1_id,
                    filter_div=html.Details([         
                        html.Summary(_('Dynamic filter')),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Label(_('Distribution field')),
                                    dcc.Dropdown(
                                        id=dropdown_chart_1_group_by_distribution_id,
                                        options=[
                                            {'label': _('-None-'), 'value': ''},
                                            {'label': _('Warehouse'), 'value': 'warehouse'},
                                            {'label': _('Customer'), 'value': 'customer'},
                                            {'label': _('Circuit'), 'value': 'circuit'},
                                            # {'label': 'Sub-Circuit', 'value': 'sub_circuit'},
                                        ],
                                        value='warehouse',
                                    ),
                                ])
                            ], sm=12, md=6, lg=6),
                            dbc.Col([
                                html.Div([
                                    dbc.Label(_('Product field')),
                                    dcc.Dropdown(
                                        id=dropdown_chart_1_group_by_product_id,
                                        options=[
                                            {'label': _('-None-'), 'value': ''},
                                            {'label': _('Product'), 'value': 'product'},
                                            # {'label': 'Product Rayon',
                                            #     'value': 'product__product_ray'},
                                            # {'label': 'Product Universe',
                                            #     'value': 'product_universe'},
                                            {'label': _('Product Type'),
                                                'value': 'product__product_type'},
                                            # {'label': 'Category',
                                            #  'value': 'product__product_category'},
                                            # {'label': 'Sub-Category',
                                            #  'value': 'product_category'},
                                        ],
                                        value='product',
                                    ),
                                ])
                            ], sm=12, md=6, lg=6),
                            dbc.Col([
                                dbc.Label(_('Show by')),
                                dcc.Dropdown(
                                    id=dropdown_chart_1_show_by_id,
                                    options=[
                                        {'label': _('Quantity (Unit)'), 'value': 'quantity'},
                                        # {'label': 'Quantity (Package)', 'value': 'package'},
                                        # {'label': 'Quantity (Pallet)', 'value': 'pallet'},
                                        {'label': _('Cost (DH)'), 'value': 'cost', 'disabled': True},
                                        # {'label': 'Weight (Kg)', 'value': 'weight'},
                                        # {'label': 'Volume (m3)', 'value': 'volume'},
                                    ],
                                    value='quantity',
                                ),

                            ], sm=12, md=6, lg=6),

                            dbc.Col([
                                html.Div([
                                    dbc.FormGroup([
                                        dbc.Label(_('Grouping period')),
                                        dcc.Dropdown(
                                            id=dropdown_chart_1_kind_id,
                                            options=[
                                                {'label': _('Year'), 'value': '%Y'},
                                                # {'label': 'Quarter', 'value': 'quarter'},
                                                {'label': _('Month'), 'value': '%Y-%b'},
                                                {'label': _('Week'), 'value': '%Y-Week%W'},
                                                {'label': _('Day'), 'value': '%Y-%b-%d'}
                                            ],
                                            value='%Y-%b-%d',
                                        )
                                    ]),
                                ])
                            ], sm=12, md=6, lg=6),
                        ]),
                    ], open=False), 
                    footer_div=html.Div([
                        html.Br(),
                        dbc.Label(_('Select values to show')),
                        dcc.Dropdown(
                            id=dropdown_chart_1_2_y_column_id,
                            options=[
                                {'label': _('Forcast Bias'), 'value': 'bias_quantity'},
                                {'label': _('Forcasts'), 'value': 'forecasted_quantity'},
                                {'label': _('Orders'), 'value': 'ordered_quantity'},
                            ],
                            value='bias_quantity',
                        ),
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_1_2_id)
                            ]),
                        ),
                        
                        html.Br(),
                        dbc.Label(_('Select values to show')),
                        dcc.Dropdown(
                            id=dropdown_chart_1_3_metric_id,
                            options=[
                                {'label': _('Forecast Bias %'), 'value': 'forecast_bias_percent'},
                                {'label': _('MAD'), 'value': 'forecast_mad_single'},
                                {'label': _('MAPE'), 'value': 'forecast_mape_single'},
                            ],
                            value='forecast_bias_percent',
                        ),
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_1_3_id)
                            ]),
                        ),
                    ])
                )
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(
                    chart_2_1_id,
                    filter_div=html.Details([         
                        html.Summary(_('Dynamic filter')),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.Label(_('Distribution field')),
                                    dcc.Dropdown(
                                        id=dropdown_chart_2_group_by_distribution_id,
                                        options=[
                                            {'label': _('-None-'), 'value': ''},
                                            {'label': _('Warehouse'), 'value': 'warehouse'},
                                            {'label': _('Customer'), 'value': 'customer'},
                                            {'label': _('Circuit'), 'value': 'circuit'},
                                            # {'label': 'Sub-Circuit', 'value': 'sub_circuit'},
                                        ],
                                        value='',
                                    ),
                                ])
                            ], sm=12, md=6, lg=6),
                            dbc.Col([
                                html.Div([
                                    dbc.Label(_('Product field')),
                                    dcc.Dropdown(
                                        id=dropdown_chart_2_group_by_product_id,
                                        options=[
                                            {'label': _('-None-'), 'value': ''},
                                            {'label': _('Product'), 'value': 'product'},
                                            # {'label': 'Product Rayon',
                                            #     'value': 'product__product_ray'},
                                            # {'label': 'Product Universe',
                                            #     'value': 'product_universe'},
                                            {'label': _('Product Type'),
                                                'value': 'product__product_type'},
                                            # {'label': 'Category',
                                            #  'value': 'product__product_category'},
                                            # {'label': 'Sub-Category',
                                            #  'value': 'product_category'},
                                        ],
                                        value='',
                                    ),
                                ])
                            ], sm=12, md=6, lg=6),
                            dbc.Col([
                                dbc.Label(_('Show by')),
                                dcc.Dropdown(
                                    id=dropdown_chart_2_show_by_id,
                                    options=[
                                        {'label': _('Quantity (Unit)'), 'value': 'quantity'},
                                        # {'label': 'Quantity (Package)', 'value': 'package'},
                                        # {'label': 'Quantity (Pallet)', 'value': 'pallet'},
                                        {'label': _('Cost (DH)'), 'value': 'cost', 'disabled': True},
                                        # {'label': 'Weight (Kg)', 'value': 'weight'},
                                        # {'label': 'Volume (m3)', 'value': 'volume'},
                                    ],
                                    value='quantity',
                                ),

                            ], sm=12, md=6, lg=6),

                            dbc.Col([
                                html.Div([
                                    dbc.FormGroup([
                                        dbc.Label(_('Grouping period')),
                                        dcc.Dropdown(
                                            id=dropdown_chart_2_kind_id,
                                            options=[
                                                {'label': _('Year'), 'value': '%Y'},
                                                # {'label': 'Quarter', 'value': 'quarter'},
                                                {'label': _('Month'), 'value': '%Y-%b'},
                                                {'label': _('Week'), 'value': '%Y-Week%W'},
                                                {'label': _('Day'), 'value': '%Y-%b-%d'}
                                            ],
                                            value='%Y-%b-%d',
                                        )
                                    ]),
                                ])
                            ], sm=12, md=6, lg=6),
                        ]),
                    ], open=False), 
                    footer_div=html.Div([
                        html.Br(),
                        dbc.Label(_('Select values to show')),
                        dcc.Dropdown(
                            id=dropdown_chart_2_2_y_column_id,
                            options=[
                                {'label': _('Forcast Bias'), 'value': 'bias_quantity'},
                                {'label': _('Forcasts'), 'value': 'forecasted_quantity'},
                                {'label': _('Orders'), 'value': 'ordered_quantity'},
                            ],
                            value='bias_quantity',
                        ),
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_2_2_id)
                            ]),
                        ),
                        
                        html.Br(),
                        dbc.Label(_('Select values to show')),
                        dcc.Dropdown(
                            id=dropdown_chart_2_3_metric_id,
                            options=[
                                {'label': _('Forecast Bias %'), 'value': 'forecast_bias_percent'},
                                {'label': _('MAD'), 'value': 'forecast_mad_single'},
                                {'label': _('MAPE'), 'value': 'forecast_mape_single'},
                            ],
                            value='forecast_bias_percent',
                        ),
                        dcc.Loading(
                            html.Div([
                                dcc.Graph(id=chart_2_3_id)
                            ]),
                        ),
                    ])
                )
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
        Output(mini_card_subtitle_bias_percent_id, 'children'),
        Output(mini_card_datatable_bias_percent_id, 'data'),
        Output(mini_card_datatable_bias_percent_id, 'columns'),
        Output(chart_bias_id, 'figure'),
    ],
    [
        Input(table_forecast_dataframe_id, 'data'),
        Input(mini_card_dropdown_bias_percent_id, 'value'),
    ]
)
def fill_cards(
        input_data,
        group_by,
    ):
    # Get dataframe
    df = pd.DataFrame.from_dict(input_data)
    # Group by selected field
    df = df.groupby(
        by=group_by, 
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
        'ordered_quantity': 'sum',
    }).reset_index()
    
    # Add metrics columns
    df['forecast_bias_percent'] = round(100 * df['forecasted_quantity'] / df['ordered_quantity'],2)

    # Compute metrics
    card_value = round(
        100 * df['forecasted_quantity'].sum() / df['ordered_quantity'].sum(), 2)

    # Prepare & sort & trunck data to be returned
    df = df[
        [group_by, 'forecast_bias_percent']
    ].replace(
        [np.inf, -np.inf], np.nan
    ).sort_values(
        'forecast_bias_percent',
        # ascending=False,
        na_position='first',
    ).head(10)

    figure = df.iplot(
        asFigure=True,
        kind='barh',
        x=group_by,
        y=['forecast_bias_percent'],
        theme='white',
        title=_('Forecast bias percent {}').format(group_by),
        xTitle=_(group_by),
        yTitle='Forecast bias percent',
    )



    # Output datatable
    column = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    return (
        card_value,
        data,
        column,
        figure
    )

@app.callback(
    [
        Output(mini_card_subtitle_mad_id, 'children'),
        Output(mini_card_datatable_mad_id, 'data'),
        Output(mini_card_datatable_mad_id, 'columns'),
        Output(chart_mad_id, 'figure'),
    ],
    [
        Input(table_forecast_dataframe_id, 'data'),
        Input(mini_card_dropdown_mad_id, 'value'),
    ]
)
def fill_cards(
        input_data,
        group_by,
    ):
    # Get dataframe
    df = pd.DataFrame.from_dict(input_data)
    # Group by selected field
    df = df.groupby(
        by=group_by, 
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
        'ordered_quantity': 'sum',
    }).reset_index()
    
    # Add metrics columns
    df['forecast_mad_single'] = round(abs(
        df['forecasted_quantity'] - df['ordered_quantity']), 2)

    # Compute metrics
    card_value = df['forecast_mad_single'].mean().round(2)
    # forecast_mape_avg = df['forecast_mape_single'].mean().round(2)

    # Prepare & sort & trunck data to be returned
    df = df[
        [group_by, 'forecast_mad_single']
    ].replace(
        [np.inf, -np.inf], np.nan
    ).sort_values(
        'forecast_mad_single',
        ascending=False,
        na_position='first',
    ).head(10)

    figure = df.iplot(
        asFigure=True,
        kind='barh',
        x=group_by,
        y=['forecast_mad_single'],
        theme='white',
        title=_('Forecast MAD single {}').format(group_by),
        xTitle=_(group_by),
        yTitle='Forecast MAD single',
    )

    # Output datatable
    column = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    return (
        card_value,
        data,
        column,
        figure
    )

@app.callback(
    [
        Output(mini_card_subtitle_mape_id, 'children'),
        Output(mini_card_datatable_mape_id, 'data'),
        Output(mini_card_datatable_mape_id, 'columns'),
        Output(chart_mape_id, 'figure'),
    ],
    [
        Input(table_forecast_dataframe_id, 'data'),
        Input(mini_card_dropdown_mape_id, 'value'),
    ]
)
def fill_cards(
        input_data,
        group_by,
    ):
    # Get dataframe
    df = pd.DataFrame.from_dict(input_data)
    # Group by selected field
    df = df.groupby(
        by=group_by, 
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
        'ordered_quantity': 'sum',
    }).reset_index()
    
    # Add metrics columns
    df['forecast_mape_single'] = round(100 * abs(
        df['forecasted_quantity'] - df['ordered_quantity']) / df['ordered_quantity'], 2)

    # Compute metrics
    card_value = df['forecast_mape_single'].mean().round(2)

    # Prepare & sort & trunck data to be returned
    df = df[
        [group_by, 'forecast_mape_single']
    ].replace(
        [np.inf, -np.inf], np.nan
    ).sort_values(
        'forecast_mape_single',
        ascending=False,
        na_position='first',
    ).head(10)

    figure = df.iplot(
        asFigure=True,
        kind='barh',
        x=group_by,
        y=['forecast_mape_single'],
        theme='white',
        title=_('Forecast MAPE single {}').format(group_by),
        xTitle=_(group_by),
        yTitle='Forecast MAPE single',
    )

    # Output datatable
    column = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    return (
        card_value,
        data,
        column,
        figure
    )



@app.callback(
    [
        # Dataframe
        Output(table_forecast_dataframe_id, 'data'),
        Output(table_forecast_dataframe_id, 'columns'),
    ],
    [
        Input(dropdown_product_list_id, 'value'),
        Input(dropdown_warehouse_list_id, 'value'),
        Input(dropdown_circuit_list_id, 'value'),
        Input(dropdown_customer_list_id, 'value'),
        Input(dropdown_version_list_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def dataframe_date_filter(
        selected_products,
        selected_warehouses,
        selected_circuits,
        selected_customers,
        selected_version,
        start_date,
        end_date,
        # kind,
        # show_by,
        # forecast_version,
        # dropdown_y_axis
        ):

    # # Define group_by
    # group_by = []
    # if group_by_product:
    #     group_by.append(group_by_product)
    # if group_by_distribution:
    #     group_by.append(group_by_distribution)

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
    print('selected_version:', selected_version)
    forecast_qs = Forecast.objects.get_forecasting(
        product_filter=selected_products, 
        warehouse_filter=selected_warehouses, 
        circuit_filter=selected_circuits, 
        customer_filter=selected_customers, 
        version_filter=selected_version, 
        start_date=start_date, 
        end_date=end_date
    )
    print('forecast_qs:', forecast_qs)

    order_qs = OrderDetail.objects.get_forecasting(
        product_filter=selected_products,
        warehouse_filter=selected_warehouses,
        circuit_filter=selected_circuits,
        customer_filter=selected_customers,
        start_date=start_date,
        end_date=end_date
    )

    # Convert queryset to dataframe and assign the right column type
    forecast_df = read_frame(forecast_qs)
    forecast_df['forecast_date'] = forecast_df['forecast_date'].astype('datetime64[ns]')

    order_df = read_frame(order_qs)
    order_df['order__ordered_at'] = order_df['order__ordered_at'].astype('datetime64[ns]')
    

    # TODO I'm HERE. Check tmp issue and maybe think to fill empty data by a default value "undefined". Do that to all columns (check graph to understand)
    # Fill empty values to avoid issues when filtering
    # forecast_df = forecast_df.fillna(forecast_df.dtypes.replace({'O': 'Undifined'})) # 'float64': 0.0, 
    # order_df = order_df.fillna(order_df.dtypes.replace({'O': 'Undifined'}))
    # forecast_df = forecast_df.replace('', np.nan)
    # order_df = order_df.replace('', np.nan)
    forecast_df['customer'] = forecast_df['customer'].fillna('undefined')
    order_df['customer'] = order_df['customer'].fillna('undefined')
    # default grouping
    _group_by_default = ['product', 'warehouse', 'circuit', 'customer']

    print(forecast_df)
    # Group by order_date and aggregate
    # forecast_df['forecast_date'] = forecast_df['forecast_date'].dt.strftime(kind)
    forecast_df = forecast_df.groupby([*_group_by_default, 'forecast_date'], as_index=False).agg(
        {'forecasted_quantity': 'sum', 'product__product_type': 'first'})

    # order_df['order__ordered_at'] = order_df['order__ordered_at'].dt.strftime(kind)
    order_df = order_df.groupby([*_group_by_default, 'order__ordered_at'], as_index=False).agg(
        {'ordered_quantity': 'sum'})
    print(order_df)
    merged_df = pd.merge(forecast_df, order_df, how='left', left_on=[
        *_group_by_default, 'forecast_date'], right_on=[
        *_group_by_default, 'order__ordered_at'])  # .dropna()
    print(merged_df)

    # Prepare data & columns to be returned
    data = merged_df.to_dict('records')
    columns = [{"name": i, "id": i} for i in merged_df.columns]


    return data, columns


@app.callback(
    [
        Output(chart_1_1_id, 'figure'),
        Output(chart_1_2_id, 'figure'),
        Output(chart_1_3_id, 'figure'),
    ],

    [
        # Input(datatable_data_upload_id, 'column'),
        Input(table_forecast_dataframe_id, 'data'),
        Input(dropdown_chart_1_forecast_version_id, 'value'),
        Input(dropdown_chart_1_group_by_product_id, 'value'),
        Input(dropdown_chart_1_group_by_distribution_id, 'value'),
        Input(dropdown_chart_1_kind_id, 'value'),
        Input(dropdown_chart_1_show_by_id, 'value'),
        Input(dropdown_chart_1_2_y_column_id, 'value'),
        Input(dropdown_chart_1_3_metric_id, 'value'),
    ]
)
def update_graph(
        data,
        version_id,
        group_by_product,
        group_by_distribution,
        kind,
        show_by,
        selected_y_column,
        selected_metric):
    # Define group_by
    group_by = []
    if group_by_distribution:
        group_by.append(group_by_distribution)
    if group_by_product:
        group_by.append(group_by_product)

    # Get dataframe
    df = pd.DataFrame.from_dict(data)

    # Clear figure if empty data or no groupby field is provided
    if df.empty or group_by == []:
        return {}

    # Convert datetime column to the correct kind (day, week, year..)
    df['forecast_date'] = df['forecast_date'].astype(
        'datetime64[ns]')
    df['forecast_date'] = df['forecast_date'].dt.strftime(kind)
    df['bias_quantity'] = df['forecasted_quantity'] - df['ordered_quantity']

    # Figure settings
    # Figure_1
    df_1 = df.copy()

    figure_1 = df_1.groupby(
        by=[*group_by],
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
        'ordered_quantity': 'sum',
        'bias_quantity': 'sum'
    }).reset_index(
    ).sort_values(
        by=['bias_quantity'],
        ascending=False,
        na_position='first',
    ).iplot(
        asFigure=True,
        kind='bar',
        # barmode='stack',
        x=group_by,
        y=['forecasted_quantity', 'ordered_quantity', 'bias_quantity'],
        theme='white',
        title=_('Forecast accuracy by {}: Forecasts, orders, bias').format(
            [item.split('__')[-1] for item in group_by]
        ),
        xTitle=_('{}').format([item.split('__')[-1] for item in group_by]),
        yTitle=show_by.capitalize(),
    )

    # Figure 2
    df_2 = df.copy()

    figure_2 = df_2.groupby(
        by=['forecast_date', group_by[0]],
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
        'ordered_quantity': 'sum',
        'bias_quantity': 'sum'
    }).reset_index(
    ).sort_values(
        by=['forecast_date', group_by[0]],
        ascending=True
    ).iplot(
        asFigure=True,
        kind='scatter',
        mode='lines + markers',
        size=5,
        x='forecast_date',
        y=selected_y_column,  # ['forecasted_quantity', 'ordered_quantity'],
        # group_by[1] if len(group_by) > 1 else group_by[0], # Assuming the array is not empty (checked previousely)
        categories=group_by[0],
        theme='white',
        title=_('{} by {}').format(
            selected_y_column.capitalize(),
            group_by[0],
        ),
        xTitle=_('date'),
        yTitle=_('Quantity'),
    )

    # Figure 3
    df_3 = df.copy().groupby(
        by=[*group_by],
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
        'ordered_quantity': 'sum',
        'bias_quantity': 'sum'
    }).reset_index()
    # Add metrics to dataframe
    df_3['forecast_bias_percent'] = round(
        100 * df_3['forecasted_quantity'] / df_3['ordered_quantity'], 2)
    df_3['forecast_mad_single'] = round(abs(
        df_3['forecasted_quantity'] - df_3['ordered_quantity']), 2)
    df_3['forecast_mape_single'] = round(100 * abs(
        df_3['forecasted_quantity'] - df_3['ordered_quantity']) / df_3['ordered_quantity'], 2)

    # Filter out rows with nan and inf
    df_3 = df_3[~df_3[[selected_metric]].isin(
        [np.nan, np.inf, -np.inf]).any(1)]
    figure_3 = df_3.sort_values(
        by=selected_metric,
        ascending=False,
        # na_position='last'
    ).iplot(
        asFigure=True,
        kind='bar',
        x=group_by,
        y=selected_metric,
        # categories=group_by[1] if len(group_by) > 1 else group_by[0],
        theme='white',
        title=_('Metric distribution by {}').format(
            [item.split('__')[-1] for item in group_by]
        ),
        xTitle=_('{}').format([item.split('__')[-1] for item in group_by]),
        yTitle=_('Metric'),
    )

    return figure_1, figure_2, figure_3


# @app.callback(
#     [
#         Output(chart_2_1_id, 'figure'),
#         Output(chart_2_2_id, 'figure'),
#         Output(chart_2_3_id, 'figure'),
#     ],

#     [
#         # Input(datatable_data_upload_id, 'column'),
#         Input(table_forecast_dataframe_id, 'data'),
#         Input(dropdown_chart_2_group_by_product_id, 'value'),
#         Input(dropdown_chart_2_group_by_distribution_id, 'value'),
#         Input(dropdown_chart_2_kind_id, 'value'),
#         Input(dropdown_chart_2_show_by_id, 'value'),
#         Input(dropdown_chart_2_2_y_column_id, 'value'),
#         Input(dropdown_chart_2_3_metric_id, 'value'),
#     ]
# )
# def update_graph(
#         data,
#         group_by_product,
#         group_by_distribution,
#         kind,
#         show_by,
#         selected_y_column,
#         selected_metric):
#     # Define group_by
#     group_by = []
#     if group_by_distribution:
#         group_by.append(group_by_distribution)
#     if group_by_product:
#         group_by.append(group_by_product)

#     # Get dataframe
#     df = pd.DataFrame.from_dict(data)

#     # Clear figure if empty data or no groupby field is provided
#     if df.empty or group_by == []:
#         return {}

#     # Convert datetime column to the correct kind (day, week, year..)
#     df['forecast_date'] = df['forecast_date'].astype(
#         'datetime64[ns]')
#     df['forecast_date'] = df['forecast_date'].dt.strftime(kind)
#     df['bias_quantity'] = df['forecasted_quantity'] - df['ordered_quantity']

#     # Figure settings
#     # Figure_1
#     df_1 = df.copy()

#     figure_1 = df_1.groupby(
#         by=[*group_by],
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#         'bias_quantity': 'sum'
#     }).reset_index(
#     ).sort_values(
#         by=['bias_quantity'],
#         ascending=False,
#         na_position='first',
#     ).iplot(
#         asFigure=True,
#         kind='bar',
#         # barmode='stack',
#         x=group_by,
#         y=['forecasted_quantity', 'ordered_quantity', 'bias_quantity'],
#         theme='white',
#         title=_('Forecast accuracy by {}: Forecasts, orders, bias').format(
#             [item.split('__')[-1] for item in group_by]
#         ),
#         xTitle=_('{}').format([item.split('__')[-1] for item in group_by]),
#         yTitle=show_by.capitalize(),
#     )

#     # Figure 2
#     df_2 = df.copy()

#     figure_2 = df_2.groupby(
#         by=['forecast_date', group_by[0]],
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#         'bias_quantity': 'sum'
#     }).reset_index(
#     ).sort_values(
#         by=['forecast_date', group_by[0]],
#         ascending=True
#     ).iplot(
#         asFigure=True,
#         kind='scatter',
#         mode='lines + markers',
#         size=5,
#         x='forecast_date',
#         y=selected_y_column,  # ['forecasted_quantity', 'ordered_quantity'],
#         # group_by[1] if len(group_by) > 1 else group_by[0], # Assuming the array is not empty (checked previousely)
#         categories=group_by[0],
#         theme='white',
#         title=_('{} by {}').format(
#             selected_y_column.capitalize(),
#             group_by[0],
#         ),
#         xTitle=_('date'),
#         yTitle=_('Quantity'),
#     )

#     # Figure 3
#     df_3 = df.copy().groupby(
#         by=[*group_by],
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#         'bias_quantity': 'sum'
#     }).reset_index()
#     # Add metrics to dataframe
#     df_3['forecast_bias_percent'] = round(
#         100 * df_3['forecasted_quantity'] / df_3['ordered_quantity'], 2)
#     df_3['forecast_mad_single'] = round(abs(
#         df_3['forecasted_quantity'] - df_3['ordered_quantity']), 2)
#     df_3['forecast_mape_single'] = round(100 * abs(
#         df_3['forecasted_quantity'] - df_3['ordered_quantity']) / df_3['ordered_quantity'], 2)

#     # Filter out rows with nan and inf
#     df_3 = df_3[~df_3[[selected_metric]].isin(
#         [np.nan, np.inf, -np.inf]).any(1)]
#     figure_3 = df_3.sort_values(
#         by=selected_metric,
#         ascending=False,
#         # na_position='last'
#     ).iplot(
#         asFigure=True,
#         kind='bar',
#         x=group_by,
#         y=selected_metric,
#         # categories=group_by[1] if len(group_by) > 1 else group_by[0],
#         theme='white',
#         title=_('Metric distribution by {}').format(
#             [item.split('__')[-1] for item in group_by]
#         ),
#         xTitle=_('{}').format([item.split('__')[-1] for item in group_by]),
#         yTitle=_('Metric'),
#     )

#     return figure_1, figure_2, figure_3


# Select all checklist callbacks
dash_utils.select_all_callbacks(
    app, dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_circuit_list_id, div_circuit_list_id, checkbox_circuit_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_product_range_list_id, div_product_range_list_id, checkbox_product_range_list_id)
