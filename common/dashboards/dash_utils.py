import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from ..dashboards import dash_constants
from stock.models import Product, ProductCategory
import datetime
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table

# Common parameters
###################
# Plotly chart config parameter
# def get_config_parameter(id):
#     config = dict(
#         id=id,
#         # displayModeBar=False,
#         displaylogo=False,
#         responsive=True,
#         modeBarButtonsToRemove=['pan2d', 'zoomIn2d', 'zoomOut2d',
#                                 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
#     )
#     return config



# Common elements
#################
def get_category_dropdown(dropdown_id, div_checklist_id, checklist_select_all_id):
    div = html.Div([
        dbc.Label('Select categories'),
        dcc.Dropdown(
            id=dropdown_id,
            placeholder='Select categories',
            options=list(ProductCategory.get_categories()),
            value=list(ProductCategory.get_categories(
            ).values_list('value', flat=True)),
            multi=True
        ),
        html.Div(
            id=div_checklist_id,
            children=dcc.Checklist(
                id=checklist_select_all_id,
                options=[
                    {"label": "Select All", "value": "All"}],
                value=["All"],
            ),
        ),

    ])
    return div


def get_product_dropdown(dropdown_id, div_checklist_id, checklist_select_all_id):
    div = html.Div([
        dbc.Label('Select products'),
        dcc.Dropdown(
            id=dropdown_id,
            placeholder="Select products",
            options=list(Product.get_products()),
            # value=list(Product.get_products().values_list('value', flat=True)),
            multi=True
        ),
        html.Div(
            id=div_checklist_id,
            children=dcc.Checklist(
                id=checklist_select_all_id,
                options=[
                    {"label": "Select All", "value": "All"}],
                value=["All"],
            ),
        ),

    ])
    return div


def get_filter_dropdown(dropdown_id, div_checklist_id, checkbox_select_all_id, options, placeholder):
    div = html.Div([
        dbc.Label(placeholder),
        dcc.Dropdown(
            id=dropdown_id,
            placeholder=placeholder,
            options=options,
            # value=list(Product.get_products().values_list('value', flat=True)),
            multi=True
        ),
        html.Div(
            id=div_checklist_id,
            children=dcc.Checklist(
                id=checkbox_select_all_id,
                options=[
                    {"label": "Select All", "value": "All"}],
                value=[],
                # value=["All"], # NOTE FIXME for madec_forecasting and testing purpose we made the chekcbox uncheckek by default to avoid wrong initialization in Dash dropdown filter
            ),
        ),

    ])
    return div


def get_checklist_select_all(div_id, value=["All"]):
    div = dcc.Checklist(
        id=div_id,
        options=[{"label": "Select All", "value": "All"}],
        value=value,
    )
    return div


# dcc.Checklist(
#     id=checklist_select_all_products_id,
#     options=[{"label": "Select All", "value": "All"}],
#     value=["All"],
# )

def get_group_by_dropdown(div_id):
    div = html.Div([
        dbc.Label('Group by'),
        dcc.Dropdown(
            id=div_id,
            options=[
                {'label': 'Product', 'value': 'product'},
                {'label': 'Category', 'value': 'category'},
            ],
            value='product',
        ),
    ])
    return div

def get_group_by_product_dropdown(div_id, value='product'):
    div = html.Div([
        dbc.Label('Product field'),
        dcc.Dropdown(
            id=div_id,
            options=[
                {'label': 'Product', 'value': 'product'},
                {'label': 'Product Rayon', 'value': 'product_ray'},
                {'label': 'Product Universe', 'value': 'product_universe'},
                {'label': 'Category',
                    'value': 'product_category_parent_level_0'},
                {'label': 'Sub-Category - Level 1',
                    'value': 'product_category_parent_level_1'},
                {'label': 'Sub-Category - Level 2',
                    'value': 'product_category_parent_level_2'},
            ],
            value=value,
        ),
    ])
    return div


def get_group_by_distribution_dropdown(div_id, value=''):
    div = html.Div([
        dbc.Label('Distribution field'),
        dcc.Dropdown(
            id=div_id,
            options=[
                {'label': '-None-', 'value': ''},
                {'label': 'Warehouse', 'value': 'warehouse'},
                {'label': 'Customer', 'value': 'customer'},
                {'label': 'Circuit', 'value': 'circuit'},
                {'label': 'Sub-Circuit', 'value': 'sub_circuit'},

            ],
            value=value,
        ),
    ])
    return div


def get_kind_dropdown(div_id, label='Select period', value='year'):
    div = html.Div([
        dbc.FormGroup([
            dbc.Label(label),
            dcc.Dropdown(
                id=div_id,
                options=[
                    {'label': 'Year', 'value': 'year'},
                    # {'label': 'Quarter', 'value': 'quarter'},
                    {'label': 'Month', 'value': 'month'},
                    {'label': 'Week', 'value': 'week'},
                    {'label': 'Day', 'value': 'day'}
                ],
                value=value,
            )
        ]),
    ])
    return div


def get_date_range(div_id, label='Select date range', year_range=5):
    div = html.Div([
        dbc.Label(label),
        html.Div([
            dcc.DatePickerRange(
                id=div_id,
                start_date_placeholder_text='Select a date range',
                end_date=datetime.datetime.now().date(),
                start_date=datetime.datetime.now().date(
                )-datetime.timedelta(days=365.25*year_range)
            ),
        ])
    ])
    return div

# Templates builder
###################
def get_chart_card(div_id, filter_div=None):
    """
    Build div representing the chart card
    """
    div = html.Div([
        html.Div([
            filter_div,
            dcc.Loading(
                dcc.Graph(id=div_id),
            )
        ], className='card-body')
    ], className='card shadow mb-4 py-3')
    return div

def get_mini_card(subtitle_id, title='', subtitle='', icon=''):
    """
    Build div representing mini card
    """
    div = html.Div([
        dbc.Row([
            html.Div([
                html.Div([
                    title,
                ], className='h5 font-weight-bold text-primary mb-1'),
                dcc.Loading(
                    html.Div([
                            subtitle
                        ], 
                        id=subtitle_id,
                        className='font-weight-bold text-gray-800 mb-0'
                    )
                )
            ], className='col mr-2'),
            html.Div([
                html.Div([
                ], className='fas {icon} fa-3x text-gray-300')
            ], className='col-auto')
        ]),
    ], className='card border-left-primary shadow card-body mb-4')
    return div


def get_datatable_card(div_id, style_data_conditional=None):
    """
    Build div representing the datatable card
    """
    div = html.Div([
        html.Div([
            dcc.Loading(
                dash_table.DataTable(
                    id=div_id,
                    page_action='native',
                    filter_action='native',
                    sort_action='native',
                    sort_mode='multi',
                    page_size=20,
                    style_data_conditional=style_data_conditional
                    # style_data_conditional=[
                    # {
                    #     'if': {
                    #         'column_id': 'Region',
                    #     },
                    #     'backgroundColor': 'dodgerblue',
                    #     'color': 'white'
                    # },
                    # {
                    #     'if': {
                    #         'column_id': 'Pressure',

                    #         # since using .format, escape { with {{
                    #         'filter_query': '{{Pressure}} = {}'.format(df['Pressure'].max())
                    #     },
                    #     'backgroundColor': '#85144b',
                    #     'color': 'white'
                    # },
                    # {
                    #     'if': {
                    #         # comparing columns to each other
                    #         'filter_query': '{total_forecasted_quantity} < {total_ordered_quantity}',
                    #         'column_id': 'total_forecasted_quantity'
                    #     },
                    #     'backgroundColor': '#3D9970'
                    # },
                    # ]
                )
            )
        ], className='card-body')
    ], className='card shadow mb-4 py-3')

    return div


def get_div_card(div_id):
    """
    Build div representing the datatable card
    """
    div = html.Div([
        html.Div([
            dcc.Loading(
                html.Div(id=div_id)
            )
        ], className='card-body')
    ], className='card shadow mb-4 py-3')

    return div

def get_dash_layout(filter_div, body_div):
    div = html.Div(
        [
            html.Div(
                [
                    html.Div([
                        filter_div,
                    ], className='card-body')
                ], className='card bg-light shadow mb-4 py-3'
            ),

            html.Div([
                body_div
            ]),
        ], style={'background-color': '#f8f9fc'}
    )
    return div

def build_modal_info_overlay(id, side, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div([  # modal div
        html.Div([  # content div
            html.Div([
                html.H4([
                    "Info",
                    html.Img(
                        id=f'close-{id}-modal',
                        src="assets/times-circle-solid.svg",
                        n_clicks=0,
                        className='info-icon',
                        style={'margin': 0},
                    ),
                ], className="container_title", style={'color': 'white'}),

                dcc.Markdown(
                    content
                ),
            ])
        ],
            className=f'modal-content {side}',
        ),
        html.Div(className='modal')
    ],
        id=f"{id}-modal",
        style={"display": "none"},
    )

    return div


def select_all_callbacks(app, dropdown_id, div_checklist_id, checklist_select_all):

    @app.callback(
        Output(dropdown_id, "value"),
        [Input(checklist_select_all, "value")],
        [State(dropdown_id, "options")],
    )
    def update_region_select(select_all, options):
        if select_all == ["All"]:
            return [i["value"] for i in options]
        raise PreventUpdate()

    @app.callback(
        Output(div_checklist_id, "children"),
        [Input(dropdown_id, "value")],
        [State(dropdown_id, "options"), State(checklist_select_all, "value")],
    )
    def update_checklist(selected, select_options, checked):
        if len(selected) < len(select_options) and len(checked) == 0:
            raise PreventUpdate()

        elif len(selected) < len(select_options) and len(checked) == 1:
            return get_checklist_select_all(checklist_select_all, value=[])

        elif len(selected) == len(select_options) and len(checked) == 1:
            raise PreventUpdate()

        return get_checklist_select_all(checklist_select_all)
