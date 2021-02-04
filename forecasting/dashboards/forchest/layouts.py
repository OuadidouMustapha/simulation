import dash_table
from .app import app
from . import ids
from .components import helpers
from django.contrib.auth import models
from django.db.models import F

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from django.utils.translation import gettext as _

#  Get list of users that can approve a version detail
_group_name = 'n1'
group_obj = models.Group.objects.get(name=_group_name)
_group_users = group_obj.user_set.all()
_group_users = list(_group_users.annotate(
    label=F('username'), value=F('id')).values('label', 'value').distinct())

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
                is_open=False,
            ),
        ),
    ], className='mx-3'),

    html.Div([
        dcc.Loading(
            dbc.Alert(
                _('Status updated successfully. The request is approved.'),
                id=ids.MESSAGE_APPROVE,
                color='success',
                dismissable=True,
                is_open=False,
            ),
        ),
    ], className='mx-3'),

    html.Div([
        dcc.Loading(
            dbc.Alert(
                _('Status updated successfully. The request is rejected.'),
                id=ids.MESSAGE_REJECT,
                color='success',
                dismissable=True,
                is_open=False,
            ),
        ),
    ], className='mx-3'),

    # Buttons
    html.Div([
        

        html.Button(
            [html.I(className="fas fa-check mr-2"), _('Approve')],
            id=ids.BUTTON_APPROVE,
            className="btn btn-xs btn-success mb-3 mx-3",
            hidden=True            
        ),
        html.Button(
            [html.I(className="fas fa-times mr-2"), _('Reject')],
            id=ids.BUTTON_REJECT,
            className="btn btn-xs btn-danger mb-3",
            hidden=True            
        ),
        html.Button(
            [html.I(className="fas fa-check-circle mr-2"), _('Confirm')],
            id=ids.BUTTON_SAVE,
            className="btn btn-xs btn-primary mb-3 mx-3",
            hidden=True
        ),
        html.Button(
            [html.I(className="fas fa-share mr-2"), _('Send for review')],
            id=ids.BUTTON_SUBMIT_REVIEW,
            className="btn btn-xs btn-danger mb-3",
            hidden=True            
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(_('Select a user to notify')),
                dbc.ModalBody(
                    html.Div([
                        dcc.Dropdown(
                            id=ids.MODAL_DROPDOWN_USER,
                            options=_group_users,
                            value=_group_users[0]['value'],
                            className='mb-3'
                        ),
                        dcc.Loading(
                            dbc.Alert(
                                _('Data saved successfully'),
                                id=ids.MESSAGE_SUCCESS_SENT_FOR_REVIEW,
                                color='success',
                                dismissable=True,
                                is_open=False,
                            ),
                        ),
                    ]),
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-times mr-2"), _('Close')],
                            id=ids.MODAL_BUTTON_CLOSE,
                            className="btn btn-xs btn-danger mb-3 mx-3",
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-check mr-2"), _('Submit')],
                            id=ids.MODAL_BUTTON_SUBMIT,
                            className="btn btn-xs btn-primary mb-3",
                        ),
                    ]),
                ),
            ],
            id=ids.MODAL_DIV,
        ),
    ])
], className='card shadow mb-4 py-3 mx-3')



# filter_container = html.Div([_classification_filter, _segmentation_filter])
body_container = html.Div([_charts])

layout = helpers.get_dash_layout(None, body_container)
