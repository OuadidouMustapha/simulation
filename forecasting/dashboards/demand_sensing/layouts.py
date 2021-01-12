import dash_table
from .app import app
from . import ids
from .components import helpers

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from django.utils.translation import gettext as _


# _datatable = dbc.Row([
#     dbc.Col([
#         helpers.get_datatable_card(
#             ids.DATABLE_FORECAST, 
#             style_data_conditional=[{
#                 'if': {'column_editable': True},
#                 'backgroundColor': 'WhiteSmoke',
#             }],
#              in_card=False)
#     ], sm=12, md=12, lg=12),
#     # dcc.Dropdown(
#     #     id=ids.DUMMY_DIV_TRIGGER,
#     #     options=[
#     #         {'label': _('Warehouse'),
#     #          'value': 'warehouse'},
#     #         {'label': _('Customer'),
#     #          'value': 'customer'},
#     #         {'label': _('Circuit'),
#     #          'value': 'circuit'},
#     #         {'label': _('Product'),
#     #          'value': 'product'},
#     #         {'label': _('Product Type'),
#     #          'value': 'product__product_type'},
#     #     ],
#     #     value='warehouse',
#     # ),
# ])
_charts = html.Div([
    html.Div([
        # Dummy div
        dbc.Row([
            dbc.Col([
                html.Div(id=ids.DUMMY_DIV_TRIGGER, hidden=True),


            ], sm=12, md=12, lg=12),
        ]),
        # Div chart
        html.Div(id=ids.DIV_CHART),

    ], className='card-body'),
    # Message after saving the data
    html.Div([
        dcc.Loading(
            dbc.Alert(
                _('Data saved successfully'), 
                id=ids.MESSAGE_SUCCESS_SAVE,
                color='success',
                dismissable=True,
                is_open=False
            ),
        ),
    ], className='mx-3'),

    # Buttons
    html.Div([
        html.Button(_('Send for Review'), id=ids.BUTTON_SUBMIT_REVIEW,
                    className='btn btn-xs btn-danger mb-3 mx-3'),
        html.Button(_('Save'), id=ids.BUTTON_SAVE,
                    className='btn btn-xs btn-primary mb-3'),
    ])
], className='card shadow mb-4 py-3 mx-3')



# filter_container = html.Div([_classification_filter, _segmentation_filter])
body_container = html.Div([_charts])

layout = helpers.get_dash_layout(None, body_container)
