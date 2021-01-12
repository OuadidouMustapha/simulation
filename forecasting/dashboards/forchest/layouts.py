import dash_table
from .app import app
from . import ids
from .components import helpers

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from django.utils.translation import gettext as _


# from stock.models import Product, Warehouse, Circuit, Customer, Order
# from ...models import Forecast, Version

# from common.dashboards import dash_constants, helpers
# from common import utils as common_utils
# from django_plotly_dash import DjangoDash
# from django_pandas.io import read_frame
# from django.db.models import OuterRef
# from dash.exceptions import PreventUpdate

# import dash_table
# import pandas as pd
# import numpy as np
# import plotly.graph_objs as go

# import cufflinks as cf
# cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

_classification_filter = dbc.Row([
    dbc.Col([
        dbc.Label(_('ABC classification'), className='mt-2'),
        dcc.Dropdown(
            id=ids.DROPDOWN_ABC,
            options=[
                {'label': _('Extremely important (A)'),
                    'value': 'A'},
                {'label': _('Moderately important (B)'),
                    'value': 'B'},
                {'label': _('Relatively unimportant (C)'),
                    'value': 'C'},
            ],
            value='A',
        ),
    ], sm=12, md=3, lg=3),
    dbc.Col([
        dbc.Label(_('FMR classification'), className='mt-2'),
        dcc.Dropdown(
            id=ids.DROPDOWN_FMR,
            options=[
                {'label': _('Frequently consumed (F)'),
                    'value': 'F'},
                {'label': _('Moderately consumed (M)'),
                    'value': 'M'},
                {'label': _('Rarely consumed (R)'),
                    'value': 'R'},
            ],
            value='F',
        ),
    ], sm=12, md=3, lg=3),
    dbc.Col([
        dbc.Label(_('Forecast accuracy'), className='mt-2'),
        dcc.Dropdown(
            id=ids.DROPDOWN_FORECAST_ACCURACY,
            options=[
                {'label': _('Well estimated'),
                    'value': 1},
                {'label': _('Overestimated'),
                    'value': 2},
                {'label': _('Underestimated'),
                    'value': 3},
            ],
            value=1,
        ),
    ], sm=12, md=3, lg=3),
    dbc.Col([
        dbc.Label(_('Forecast status'), className='mt-2'),
        dcc.Dropdown(
            id=ids.DROPDOWN_FORECAST_STATUS,
            options=[
                {'label': _('Remaining'),
                    'value': 1},
                {'label': _('Achieved not approved'),
                    'value': 2},
                {'label': _('Achieved & approved'),
                    'value': 3},
            ],
            value=1,
        ),
    ], sm=12, md=3, lg=3),
])

_segmentation_filter = dbc.Row([
    dbc.Col([
        dbc.Label(_('Product'), className='mt-2'),
        dcc.Dropdown(
            id=ids.DROPDOWN_PRODUCT,
            options=[
                {'label': _('Prod01'),
                    'value': 1},
            ],
            value=1,
        ),
    ], sm=12, md=6, lg=6),
    dbc.Col([
        dbc.Label(_('Circuit'), className='mt-2'),
        dcc.Dropdown(
            id=ids.DROPDOWN_CIRCUIT,
            options=[
                {'label': _('Circ01'),
                    'value': 1},
            ],
            value=1,
        ),
    ], sm=12, md=6, lg=6),
])

_cards = dbc.Row([
    dbc.Col([
        helpers.get_mini_card(
            ids.CARD_NUM_ACHIEVED_SEGMENTS,
            title=_('Achieved segments'),
        )
    ], sm=12, md=4, lg=4),
    dbc.Col([
        helpers.get_mini_card(
            ids.CARD_NUM_APPROVED_SEGMENTS,
            title=_('Approved segments'),
        )
    ], sm=12, md=4, lg=4),
    dbc.Col([
        helpers.get_mini_card(
            ids.CARD_NUM_REMAINING_SEGMENTS,
            title=_('Remaining segments'),
        )
    ], sm=12, md=4, lg=4),
])

_charts = dbc.Row([
    dbc.Col([
        helpers.get_chart_card(
            ids.CHART_ORDER_FORECAST,
            # Add component graph layout
            footer_div=dcc.Loading(
                dcc.Graph(id=ids.CHART_ORDER_FORECAST_COMPONENTS),
            )
        ),
    ], sm=12, md=12, lg=12),
])


# import pandas as pd
# df = pd.read_csv(
#     'https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
# _datatable = helpers.get_datatable_card(ids.DATABLE_SUMMARY, columns=[{"name": i, "id": i} for i in df.columns],
#                                         data=df.to_dict('records'),)
_datatable = dbc.Row([
    dbc.Col([
        helpers.get_datatable_card(ids.DATABLE_HISTORY)
    ], sm=12, md=6, lg=6),
    dbc.Col([
        helpers.get_datatable_card(ids.DATABLE_FORECAST)
    ], sm=12, md=6, lg=6),
])



filter_container = html.Div([_classification_filter, _segmentation_filter])
body_container = html.Div([_charts, _datatable])


layout = helpers.get_dash_layout(filter_container, body_container)
