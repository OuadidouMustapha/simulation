import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
import datetime
from common import utils as common_utils
from .. import utils
from ..models import DeliveryDetail, Delivery, Order, StockControl, Product, ProductCategory
import copy
from common.dashboards import dash_utils, dash_constants
from dash.exceptions import PreventUpdate


# app = DjangoDash('StockValue', external_stylesheets=[dbc.themes.BOOTSTRAP])
app = DjangoDash('StockValue', add_bootstrap_links=True)

prefix = 'stock-value'
dropdown_categories_id = prefix + '-dropdown-categories'
checklist_select_all_categories_id = prefix + '-checklist-select-all-categories'
div_checklist_category_id = prefix + '-div-checklist_category'
dropdown_products_id = prefix + '-dropdown-products'
checklist_select_all_products_id = prefix + '-checklist-select-all-products'
div_checklist_id = prefix + '-div-checklist'
dropdown_y_axis_id = prefix + '-dropdown-y-axis'
input_period_date_range_id = prefix + '-input-date-range'
dropdown_period_id = prefix + '-dropdown-period'
radioitems_chart_type_id = prefix + '-radioitems-chart-type'
chart_stock_value_by_product_id = prefix + '-chart-stock-value-by-product'
dropdown_group_by_field_id = prefix + '-dropdown-group-by-field'
chart_stock_cost_id = prefix + '-chart-stock-cost'
chart_stock_quantity_unit_id = prefix + '-chart-stock-quantity-unit'
chart_stock_quantity_package_id = prefix + '-chart-stock-quantity-package'
chart_stock_quantity_pallet_id = prefix + '-chart-stock-quantity-pallet'
chart_stock_weight_id = prefix + '-chart-stock-weight'
chart_stock_volume_id = prefix + '-chart-stock-volume'


def filter_container():
    filter_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_category_dropdown(
                    dropdown_categories_id,
                    div_checklist_category_id,
                    checklist_select_all_categories_id
                ),

            ], sm=12, md=6, lg=3),

            dbc.Col([
                dash_utils.get_product_dropdown(
                    dropdown_products_id,
                    div_checklist_id,
                    checklist_select_all_products_id
                ),

                # html.Div([

                #     dcc.Checklist(
                #         id=checklist_select_all_products_id,
                #         options=[{'label': 'Select All', 'value': 1}],
                #         value=[]
                #     )
                # ], id=),
            ], sm=12, md=6, lg=3),

            dbc.Col([
                dash_utils.get_group_by_dropdown(dropdown_group_by_field_id),
                dash_utils.get_kind_dropdown(dropdown_period_id),
            ], sm=12, md=6, lg=3),

            dbc.Col([
                dash_utils.get_date_range(input_period_date_range_id, year_range=5),

                dbc.FormGroup([
                    dbc.Label('Chart type'),
                    dbc.RadioItems(
                        id=radioitems_chart_type_id,
                        options=[
                            {'label': 'Stack', 'value': 'stack'},
                            {'label': 'Group', 'value': 'group'}
                        ],
                        value='stack',
                        inline=True,
                    )
                ]),
            ], sm=12, md=6, lg=3),

            # dbc.Col([
            #     dbc.Label('Show by'),
            #     dcc.Dropdown(
            #         id=dropdown_y_axis_id,
            #         options=[
            #             {'label': 'Value (DH)', 'value': 'avg_cost'},
            #             {'label': 'Quantity (Unit)', 'value': 'avg_quantity'},
            #             {'label': 'Quantity (Package)', 'value': 'avg_package'},
            #             {'label': 'Quantity (Pallet)', 'value': 'avg_pallet'},
            #             {'label': 'Weight (Kg)', 'value': 'avg_weight'},
            #             {'label': 'Volume (cm3)', 'value': 'avg_volume'},
            #             # {'label': 'Coverage (days)', 'value': 'avg_coverage'},
            #         ],
            #         value='avg_cost',
            #     ),
            # ]),
        ]),
    ])
    return filter_container

def chart_container():
    chart_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_cost_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_quantity_unit_id)
            ], sm=12, md=12, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_quantity_package_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_quantity_pallet_id)
            ], sm=12, md=12, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_weight_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_volume_id)
            ], sm=12, md=12, lg=6),
        ]),
    ])
    return chart_container


app.layout = dash_utils.get_dash_layout(filter_container(), chart_container())

@app.callback(
    [
        Output(chart_stock_cost_id, 'figure'),
        Output(chart_stock_quantity_unit_id, 'figure'),
        Output(chart_stock_quantity_package_id, 'figure'),
        Output(chart_stock_quantity_pallet_id, 'figure'),
        Output(chart_stock_weight_id, 'figure'),
        Output(chart_stock_volume_id, 'figure'),
    ],
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(dropdown_period_id, 'value'),
        Input(input_period_date_range_id, 'start_date'),
        Input(input_period_date_range_id, 'end_date'),
        Input(radioitems_chart_type_id, 'value'),
        # Input(dropdown_y_axis_id, 'value'),
     #  Input('dropdown-x-axis', 'value'),
        Input(dropdown_group_by_field_id, 'value'),

     ]
)
def update_charts(category_ids, product_ids, kind, inventory_date_start, inventory_date_end, chart_type, group_by_field):
    chart_y_axis = [
        {'label': 'Value (DH)', 'key': 'avg_cost', },
        {'label': 'Quantity (Unit)', 'key': 'avg_quantity', },
        {'label': 'Quantity (Package)', 'key': 'avg_package', },
        {'label': 'Quantity (Pallet)', 'key': 'avg_pallet', },
        {'label': 'Weight (Kg)', 'key': 'avg_weight', },
        {'label': 'Volume (cm3)', 'key': 'avg_volume', },
    ]


    filter_kwargs = {}
    filter_kwargs['stock__product__category__in'] = ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True)
    filter_kwargs['stock__product__in'] = product_ids
    filter_kwargs['inventory_date__gte'] = inventory_date_start
    filter_kwargs['inventory_date__lte'] = inventory_date_end

    qs = StockControl.objects.get_stock_value(
        kind=kind,
        group_by_field=group_by_field,
        filter_kwargs=filter_kwargs
    )
    
    # Group data by category as a preparation for plotting
    if group_by_field == 'product':
        category_key = 'stock__product__reference'
    elif group_by_field == 'category':
        category_key = 'stock__product__category__reference'

    figures = []
    for y in chart_y_axis:
        dataset_grouped_category = common_utils.group_data_by_category(qs, category_key=category_key,
                                                                x_key='inventory_date_truncated', y_key=y['key'])

        # Build chart data
        chart_data = []
        for key, value in dataset_grouped_category.items():
            chart_data.append(
            go.Bar(
                    x=value['x'],
                    y=value['y'],
                    name=key,
                )
            )

        chart_layout = copy.deepcopy(dash_constants.layout)
        chart_layout['title'] = 'Stock {} Distribution by {}'.format(
            y['label'], group_by_field.capitalize())
        chart_layout['xaxis'] = dict(
            title='Date in {}s'.format(kind.capitalize()))
        chart_layout['yaxis'] = dict(title=y['label'])
        chart_layout['barmode'] = chart_type

        figures.append({'data': chart_data, 'layout': chart_layout})
    figures = tuple(figures)
    return figures


@app.callback(
    Output(dropdown_products_id, 'options'),
    [
        Input(dropdown_categories_id, 'value')
    ]
)
def set_products_of_categories(category_ids):
    # Filter existing product_ids by keeping items where the category is selected
    category_descendants = list(ProductCategory.objects.filter(
        pk__in=category_ids).get_descendants(include_self=True))
    return list(Product.get_products(category_descendants))

# Select all products checklist callbacks
dash_utils.select_all_callbacks(
    app, dropdown_products_id, div_checklist_id, checklist_select_all_products_id)
# Select all categories checklist callbacks
dash_utils.select_all_callbacks(
    app, dropdown_categories_id, div_checklist_category_id, checklist_select_all_categories_id)


# !Code I may use ( TODO : to be deleted)
# card = dbc.Card([
#     dbc.CardHeader('Stock Value'),
#     dbc.CardBody(
#         [
#             filter_container(),
#             chart_container()
#         ]
#     ),
# ],  className='shadow')
