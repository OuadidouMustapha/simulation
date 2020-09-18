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
from stock.models import Warehouse

# Initialization
min_deployment_days = 2
# Get warehouse queryset
warehouse_qs = Warehouse.objects.values('name', 'available_trucks', 'reception_capacity')
# Convert queryset to dataframe
warehouse_df = read_frame(warehouse_qs)

app = DjangoDash('DeploymentDashboard', add_bootstrap_links=True)

### Used IDs ### 
prefix = 'deployment-dashboard'
# Filter IDs

dropdown_show_by_id = prefix + '-dropdown-show-by'
input_date_range_id = prefix + '-input-date-range'
# Mini-cards IDs
mini_card_subtitle_bias_percent_id = prefix + 'mini-card-subtitle-bias-percent'
mini_card_subtitle_mad_id = prefix + 'mini-card-subtitle-mad'
mini_card_subtitle_mape_id = prefix + 'mini-card-subtitle-mape'
# Charts IDs
chart_by_date_by_group_id = prefix + 'chart-by-date-by-group'
chart_dropdown_y_axis_id = prefix + 'chart-filter-y-axis'
chart_by_group_id = prefix + 'chart-by-group'
# Dataframe ID
table_truck_settings_id = prefix + '-table-truck-settings'
table_output_id = prefix + '-table-output'

### Global variable ###
def filter_container():
    filter_container = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Col([
                    dbc.Label('Maximizé'),
                    dcc.Dropdown(
                        id=dropdown_show_by_id,
                        options=[
                            {'label': 'Chiffre d\'affaire', 'value': 'turnover'},
                            {'label': 'Gain', 'value': 'gain'},
                        ],
                        value='turnover',
                    ),
                ], sm=12, md=12, lg=12),
                dbc.Col([
                    html.Div([
                        dbc.Label('Sur la période'),
                        html.Div([
                            dcc.DatePickerRange(
                                id=input_date_range_id,
                                start_date_placeholder_text='Select a date range',
                                min_date_allowed=datetime.datetime.now().date(
                                )+datetime.timedelta(days=min_deployment_days),
                                start_date=datetime.datetime.now().date(
                                )+datetime.timedelta(days=min_deployment_days),
                                end_date=datetime.datetime.now().date(
                                )+datetime.timedelta(days=min_deployment_days)
                            ),
                        ])
                    ])
                ], sm=12, md=12, lg=12),
            ], sm=12, md=4, lg=3),
            dbc.Col([
                dbc.Col([
                    html.Div([
                        dbc.Label('Disponibilité des vehicules et leurs capacités'),
                        dcc.Loading(
                            dash_table.DataTable(
                                id=table_truck_settings_id,
                                data=warehouse_df.round(
                                    2).to_dict('records'),
                                columns=[{'name': i, 'id': i, 'editable': False}
                                            for i in warehouse_df.columns[0:1]] + [{'name': i, 'id': i, 'editable': True}
                                                                                for i in warehouse_df.columns[1:]],
                                page_size=20,
                            )
                        )
                    ])
                ]),
            ], sm=12, md=8, lg=9),
        ]),
    ])
    return filter_container

def body_container():
    body_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_datatable_card(
                    table_output_id,
                    data=warehouse_df.round(
                        2).to_dict('records'),
                    columns=[{'name': i, 'id': i}
                             for i in ['Truck', 'Warehouse', 'Product', 'Quantity', 'Gain','Turnover']],
                )
            ], sm=12, md=12, lg=12),
        ]),
    ])
    return body_container

app.layout = dash_utils.get_dash_layout(filter_container(), body_container())