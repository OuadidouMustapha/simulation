import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash

from ..models import SaleDetail, Sale, Order, StockControl, Product, ProductCategory
from .. import utils
import datetime
import copy
from common.dashboards import dash_utils, dash_constants


app = DjangoDash('StockPareto', add_bootstrap_links=True)

prefix = 'stock-pareto'
dropdown_categories_id = prefix + '-dropdown-categories'
checklist_select_all_categories_id = prefix + '-checklist-select-all-categories'
div_checklist_category_id = prefix + '-div-checklist_category'
dropdown_products_id = prefix + '-dropdown-products'
checklist_select_all_products_id = prefix + '-checklist-select-all-products'
dropdown_y_axis_id = prefix + '-dropdown-y-axis'
input_period_date_range_id = prefix + '-input-date-range'
input_avg_sale_date_range_id = prefix + '-input-avg-sale-date-range'
radioitems_avg_quantity_period_id = prefix + '-radioitems-quantity-period'
radioitems_avg_sale_period_id = prefix + '-radioitems-sale-period'
radioitems_chart_type_id = prefix + '-radioitems-chart-type'
dropdown_group_by_field_id = prefix + '-dropdown-group-by-field'
bool_include_weekend_id = prefix + '-bool-include-weekend'
div_checklist_id = prefix + '-div-checklist'
# chart_stock_value_by_product_id = prefix + '-chart-stock-value-by-product'
input_dio_low_id = prefix + '-input-dio-low'
input_dio_high_id = prefix + '-input-dio-high'
chart_stock_pareto_id = prefix + '-chart-stock-pareto-id'
chart_top_total_cost_id = prefix + '-chart-top-total-cost-id'
chart_sale_pareto_id = prefix + '-chart-sale-pareto-id'
chart_top_delivered_total_cost_id = prefix + '-chart-top-delivered-total-cost-id'


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

            ], sm=12, md=6, lg=3),

            dbc.Col([
                dash_utils.get_group_by_dropdown(dropdown_group_by_field_id),
            ], sm=12, md=6, lg=3),

            dbc.Col([
                dash_utils.get_date_range(
                    input_period_date_range_id, label='Inventory range date', year_range=5),
            ], sm=12, md=6, lg=3),
        ]),
    ])
    return filter_container


def chart_container():
    chart_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_pareto_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_top_total_cost_id)
            ], sm=12, md=12, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_sale_pareto_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_top_delivered_total_cost_id)
            ], sm=12, md=12, lg=6),
        ]),
    ])
    return chart_container


app.layout = dash_utils.get_dash_layout(filter_container(), chart_container())


@app.callback(
    Output(chart_stock_pareto_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(input_period_date_range_id, 'start_date'),
        Input(input_period_date_range_id, 'end_date'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_stock_pareto_chart(
        category_ids,
        product_ids,
        inventory_date_start,
        inventory_date_end,
        group_by_field):

    # Build filter for the query
    filter_kwargs = {}
    filter_kwargs['inventory_date__gte'] = inventory_date_start
    filter_kwargs['inventory_date__lte'] = inventory_date_end
    filter_kwargs['stock__product__category__in'] = ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True)
    filter_kwargs['stock__product__in'] = product_ids

    # Get the query
    qs = StockControl.objects.get_cumul_product_total_cost(filter_kwargs, group_by_field)
    y_axis = list(qs.values_list('cumul_product_total_cost_corrected', flat=True))
    pareto_value = y_axis[-1] * (80/100)

    # Prepare chart elements
    # Chart data
    chart_data = []
    # Prepare chart elements
    chart_data += go.Bar(
        # x=list(qs.values_list('stock__product__reference', flat=True)),
        x=[x+1 for x in range(qs.count())],
        y=list(qs.values_list('product_total_cost', flat=True)),
        name='Inventory product value',
    ),
    chart_data += go.Scatter(
        x=[x+1 for x in range(qs.count())],
        y=y_axis,
        name='Cumulative value',
        line_shape='spline'
    ),


    # Chart layout
    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Inventory pareto chart'
    chart_layout['xaxis'] = dict(title='Product count')
    chart_layout['yaxis'] = dict(title='Inventory value')
    chart_layout['annotations'] = [
        dict(
            x=0.1,
            y=pareto_value,
            xref='paper',
            yref='y',
            text='80% values',
            ax=0,
            ay=-10
        )
    ]
    chart_layout['shapes'] = [
        dict(
            type='line',
            yref='y',
            xref='paper',
            y0=pareto_value,
            x0=0,
            y1=pareto_value,
            x1=1,
            fillcolor='red',
            layer='below',
            line=dict(
                color='red',
                width=2,
            )
        ),
    ]
    figure = {'data': chart_data, 'layout': chart_layout}

    return figure


@app.callback(
    Output(chart_top_total_cost_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(input_period_date_range_id, 'start_date'),
        Input(input_period_date_range_id, 'end_date'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_top_stock_items_chart(
        category_ids,
        product_ids,
        inventory_date_start,
        inventory_date_end,
        group_by_field):

    # Chart layout
    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Top products values'
    chart_layout['xaxis'] = dict(title='Product')
    chart_layout['yaxis'] = dict(title='Total cost')

    # Build filter for the query
    filter_kwargs = {}
    filter_kwargs['inventory_date__gte'] = inventory_date_start
    filter_kwargs['inventory_date__lte'] = inventory_date_end
    filter_kwargs['stock__product__category__in'] = ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True)
    filter_kwargs['stock__product__in'] = product_ids
    # Get the query
    queryset = StockControl.objects.get_cumul_product_total_cost(filter_kwargs, group_by_field)
    
    
    # Prepare chart elements
    chart_data = go.Bar(
        x=list(queryset.values_list('stock__product__reference', flat=True)),
        y=list(queryset.values_list('product_total_cost', flat=True)),
        name='key',
    ),
    figure = {'data': chart_data, 'layout': chart_layout}

    return figure

@app.callback(
    Output(chart_sale_pareto_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(input_period_date_range_id, 'start_date'),
        Input(input_period_date_range_id, 'end_date'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_sale_pareto_chart(
        category_ids,
        product_ids,
        sold_at_start,
        sold_at_end,
        group_by_field):

    # Build filter for the query
    filter_kwargs = {}
    filter_kwargs['sale__sold_at__gte'] = sold_at_start
    filter_kwargs['sale__sold_at__lte'] = sold_at_end
    filter_kwargs['stock__product__category__in'] = ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True)
    filter_kwargs['stock__product__in'] = product_ids

    # Get the query
    qs = SaleDetail.objects.get_cumul_delivered_product_total_cost(filter_kwargs, group_by_field)
    y_axis = list(qs.values_list(
        'cumul_delivered_product_total_cost_corrected', flat=True))
    pareto_value = y_axis[-1] * (80/100)

    # Prepare chart elements
    # Chart data
    chart_data = []
    chart_data += go.Bar(
        x=[x+1 for x in range(qs.count())],
        y=list(qs.values_list('delivered_product_total_cost', flat=True)),
        name='Delivered product value',
    ),
    chart_data += go.Scatter(
        x=[x+1 for x in range(qs.count())],
        y=y_axis,
        name='Cumulative value',
        line_shape='spline'
    ),
    # Chart layout
    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Sales pareto chart'
    chart_layout['xaxis'] = dict(title='Product count')
    chart_layout['yaxis'] = dict(title='Sale value')
    chart_layout['annotations'] = [
        dict(
            x=0.1,
            y=pareto_value,
            xref='paper',
            yref='y',
            text='80% values',
            ax=0,
            ay=-10
        )
    ]
    chart_layout['shapes'] = [
        dict(
            type='line',
            yref='y',
            xref='paper',
            y0=pareto_value,
            x0=0,
            y1=pareto_value,
            x1=1,
            fillcolor='red',
            layer='below',
            line=dict(
                color='red',
                width=2,
            )
        ),
    ]
    figure = {'data': chart_data, 'layout': chart_layout}

    return figure


@app.callback(
    Output(chart_top_delivered_total_cost_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(input_period_date_range_id, 'start_date'),
        Input(input_period_date_range_id, 'end_date'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_chart(
        category_ids,
        product_ids,
        sold_at_start,
        sold_at_end,
        group_by_field):

    # Chart layout
    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Top product sales value'
    chart_layout['xaxis'] = dict(title='Product')
    chart_layout['yaxis'] = dict(title='Total cost')

    # Build filter for the query
    filter_kwargs = {}
    filter_kwargs['sale__sold_at__gte'] = sold_at_start
    filter_kwargs['sale__sold_at__lte'] = sold_at_end
    filter_kwargs['stock__product__category__in'] = ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True)
    filter_kwargs['stock__product__in'] = product_ids
    # Get the query
    queryset = SaleDetail.objects.get_cumul_delivered_product_total_cost(
        filter_kwargs, group_by_field)
    
    
    # Prepare chart elements
    chart_data = go.Bar(
        x=list(queryset.values_list('stock__product__reference', flat=True)),
        y=list(queryset.values_list('delivered_product_total_cost', flat=True)),
        name='key',
    ),
    figure = {'data': chart_data, 'layout': chart_layout}

    return figure


@app.callback(
    Output(dropdown_products_id, 'options'),
    [
        Input(dropdown_categories_id, 'value')
    ]
)
def set_products_of_categories(category_ids):
    # Filter existing product_ids by keeping items where the category is selected
    category_descendants = list(ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True))
    return list(Product.get_products(category_descendants))


# Select all products checklist callbacks
dash_utils.select_all_callbacks(
    app, dropdown_products_id, div_checklist_id, checklist_select_all_products_id)
# Select all categories checklist callbacks
dash_utils.select_all_callbacks(
    app, dropdown_categories_id, div_checklist_category_id, checklist_select_all_categories_id)

