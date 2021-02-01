import dash_table
from .app import app
from . import ids
from .components import helpers
from django.contrib.auth import models
from django.db.models import F
from deployment.models import TruckAvailability
from stock.models import Warehouse
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from django.utils.translation import gettext as _
from django_pandas.io import read_frame

import datetime

_all_warehouses = list(Warehouse.objects.get_all_warehouses())
# Used parameters
_min_deployment_days  = 1
_deployment_days = 6*30

# Truck availability query
truckavailability_qs = TruckAvailability.objects.filter(warehouse__warehouse_type='RDC')
truckavailability_qs = truckavailability_qs.values(
    'warehouse', 'category__reference', 'warehouse__reception_capacity', 'available_truck', 'category__capacity', 'category__cost')
truckavailability_qs = truckavailability_qs.order_by('warehouse')
truckavailability_df = read_frame(truckavailability_qs)
_editable_columns = ['warehouse__reception_capacity', 'available_truck',
                     'category__capacity', 'category__cost']

_input = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Col([
                dbc.Label(_('Maximize')),
                dcc.Dropdown(
                    id=ids.DROPDOWN_SHOW_BY,
                    options=[
                        {'label': _('Turnover'), 'value': 'Chiffre d\'affaire'},
                        {'label': 'Gain', 'value': 'gain'},
                    ],
                    value='turnover',
                ),
            ], sm=12, md=12, lg=12),
            dbc.Col([
                html.Div([
                    dbc.Label(_('Over the period')),
                    html.Div([
                        dcc.DatePickerRange(
                            id=ids.INPUT_DATE_RANGE,
                            className='mb-3',
                            start_date_placeholder_text='Select a date range',
                            min_date_allowed=datetime.datetime.now().date() + datetime.timedelta(days=_min_deployment_days),
                            start_date=datetime.datetime.now().date() + datetime.timedelta(days=_min_deployment_days),
                            end_date=datetime.datetime.now().date() + datetime.timedelta(days=_min_deployment_days) +
                            datetime.timedelta(days=_deployment_days)
                        ),
                    ])
                ], className='my-3')
            ], sm=12, md=12, lg=12),
            html.Div([
                html.Button(
                    [html.I(className='fas fa-play mr-2'), _('Run')],
                    id=ids.BUTTON_RUN,
                    className='btn btn-xs btn-primary mb-3 mx-3',
                ),
                html.Button(
                    [html.I(className='fas fa-save mr-2'), _('Save')],
                    id=ids.BUTTON_SAVE,
                    className='btn btn-xs btn-primary mb-3',
                    hidden=True
                ),
            ]),
        ], sm=12, md=4, lg=3),
        dbc.Col([
            dbc.Col([
                html.Div([
                    dbc.Label(
                        _('Availability of vehicles and their capacities')),
                    dcc.Loading(
                        dash_table.DataTable(
                            id=ids.DATATABLE_TRUCKAVAILABILITY,
                            data=truckavailability_df.to_dict('records'),
                            columns=[{'name': i, 'id': i, 'editable': True if i in _editable_columns else False}
                                        for i in truckavailability_df.columns],
                            page_action='native',
                            filter_action='native',
                            sort_action='native',
                            sort_mode='multi',
                            page_size=15,
                            # style_data_conditional=[{
                            #     'if': {'column_editable': True},
                            #     'backgroundColor': 'WhiteSmoke',
                            # }],
                        )
                    )
                ])
            ]),
        ], sm=12, md=8, lg=9),
    ]),
])

_output = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Alert(
                _('Data saved successfully'),
                id=ids.MESSAGE_SUCCESS,
                color='success',
                dismissable=True,
                is_open=False,
            ),
        ], sm=12, md=12, lg=12),
    ]),

    dbc.Row([
        dbc.Col([
            html.Div(
                [
                    html.Div(
                        className='control-tabs',
                        children=[
                            dcc.Tabs(
                                value='Product-at',
                                children=[
                                    dcc.Tab(
                                        label=_('Warhouses Pie Graph'),
                                        value='Product-at',
                                        children=html.Div(
                                            className='control-tab',
                                            children=[
                                                dbc.Col([
                                                    dbc.Label(
                                                        _('Warehouses')),
                                                    dcc.Dropdown(
                                                        id=ids.DROPDOWN_W_PIE_BY,
                                                        multi=True,
                                                        options=_all_warehouses,
                                                        value=[_all_warehouses[i]['value'] for i in range(len(_all_warehouses))],
                                                    ),
                                                ], sm=12, md=12, lg=12),
                                                html.Div(
                                                    className='app-controls-block',
                                                    children=dcc.Loading(
                                                        html.Div(
                                                            [dcc.Graph(id=ids.FIGURE_PIE_ID)],
                                                            className="",
                                                        )
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                    dcc.Tab(
                                        label=_('Warehouses'),
                                        value='what-is',
                                        children=dcc.Loading(
                                            html.Div(
                                                [dcc.Graph(id=ids.FIGURE_WAREHOUSES_ID)],
                                                className="",
                                            )
                                        ),
                                    ),
                                ])
                        ],
                    ),
                ],
                id=ids.DIV_W_PIE_BY,
                hidden=True,
                className="shadow-lg p-12 mb-5 bg-white rounded",
            ),
        ], sm=12, md=6, lg=6),
        dbc.Col([
            html.Div(
                [
                    html.Div(
                        className='control-tabs',
                        children=[
                            dcc.Tabs(
                                value='what-is',
                                children=[
                                    dcc.Tab(
                                        label=_('Product'),
                                        value='what-is',
                                        children=html.Div(
                                            className='control-tab',
                                            children=[
                                                dbc.Col([
                                                    dbc.Label(_('Warehouses')),
                                                    dcc.Dropdown(
                                                        id=ids.DROPDOWN_W_T_BY,
                                                        multi=True,
                                                        options=_all_warehouses,
                                                        value=[_all_warehouses[i]['value'] for i in range(len(_all_warehouses))],),
                                                ], sm=12, md=12, lg=12),
                                                html.Div(
                                                    className='app-controls-block',
                                                    children=dcc.Loading(
                                                        html.Div(
                                                            [dcc.Graph(id=ids.FIGURE_TOP_ID)],
                                                            className="",
                                                        )
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ])
                        ],
                    ),
                ],
                id=ids.DIV_W_T_BY,
                hidden=True,
                className="shadow-lg p-12 mb-5 bg-white rounded",
            ),
        ], sm=12, md=6, lg=6),
    ]),
    html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Label(
                        _('Deployed quantities by truck')),
                    dcc.Loading(
                        dash_table.DataTable(
                            id=ids.DATATABLE_DEPLOYMENT,
                            # data=truckavailability_df.to_dict('records'),
                            # columns=[{'name': i, 'id': i, 'editable': True if i in _editable_columns else False}
                            #         for i in truckavailability_df.columns],
                            page_action='native',
                            filter_action='native',
                            sort_action='native',
                            sort_mode='multi',
                            page_size=20,
                        )
                    ),
                ], sm=12, md=12, lg=12),
                html.Div([
                    dash_table.DataTable(
                        id=ids.DATATABLE_TRUCK,
                    )
                ], hidden=True),
            ])
        ], className='card-body')
    ], className='card shadow mb-4 py-3'),
])

layout = helpers.get_dash_layout(_input, _output)
