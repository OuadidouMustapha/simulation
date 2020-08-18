import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash

from ..models import SaleDetail, Sale, Order, StockControl, Product, ProductCategory
from common import utils as common_utils
from .. import utils
import datetime
import copy
from common.dashboards import dash_utils, dash_constants

app = DjangoDash('StockDio', add_bootstrap_links=True)

prefix = 'stock-dio'
dropdown_categories_id = prefix + '-dropdown-categories'
checklist_select_all_categories_id = prefix + '-checklist-select-all-categories'
div_checklist_category_id = prefix + '-div-checklist_category'
dropdown_products_id = prefix + '-dropdown-products'
checklist_select_all_products_id = prefix + '-checklist-select-all-products'
dropdown_y_axis_id = prefix + '-dropdown-y-axis'
input_date_range_id = prefix + '-input-date-range'
input_avg_sale_date_range_id = prefix + '-input-avg-sale-date-range'
dropdown_avg_quantity_period_id = prefix + '-radioitems-quantity-period'
radioitems_avg_sale_period_id = prefix + '-radioitems-sale-period'
radioitems_chart_type_id = prefix + '-radioitems-chart-type'
chart_stock_dio_id = prefix + '-chart-stock-dio'
chart_stock_dio_2_id = prefix + '-chart-stock-dio-two'
chart_stock_dio_3_id = prefix + '-chart-stock-dio-three'
chart_stock_dio_4_id = prefix + '-chart-stock-dio-four'
dropdown_group_by_field_id = prefix + '-dropdown-group-by'
chart_avg_delivered_quantity_by_product = prefix + '-chart-avg-quantity-by-product'
# chart_stock_value_by_product_id = prefix + '-chart-stock-value-by-product'
div_checklist_id = prefix + '-div-checklist'
input_dio_low_id = prefix + '-input-dio-low'
input_dio_high_id = prefix + '-input-dio-high'
bool_include_weekend_id = prefix + '-bool-include-weekend'



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
                dash_utils.get_kind_dropdown(dropdown_avg_quantity_period_id, label='Select avg. quantity period'),
                dbc.FormGroup([
                    dbc.Checklist(
                        options=[
                            {'label': 'Include Weekends', 'value': True},
                        ],
                        value=[True],
                        id=bool_include_weekend_id,
                        inline=True,
                        switch=True,
                    ),
                ]),
                dash_utils.get_kind_dropdown(
                    radioitems_avg_sale_period_id, label='Select avg. sale period'),
            ], sm=12, md=6, lg=3),

            dbc.Col([
                dash_utils.get_date_range(
                    input_date_range_id, label='Select range date', year_range=5),
                dash_utils.get_date_range(
                    input_avg_sale_date_range_id, label='Select avg sale date range', year_range=5),

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
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label('Select Date Interval'),
                dcc.Input(
                    id=input_dio_low_id,
                    type='number',
                    placeholder='DIO low value',
                    value=1,
                ),
                dcc.Input(
                    id=input_dio_high_id,
                    type='number',
                    value=2,
                )
            ]),
        ])
    ])
    return filter_container


def chart_container():
    chart_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_dio_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_dio_2_id)
            ], sm=12, md=12, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_dio_4_id)
            ], sm=12, md=12, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(chart_stock_dio_3_id)
            ], sm=12, md=12, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(
                    chart_avg_delivered_quantity_by_product)
            ], sm=12, md=12, lg=6),
            # dbc.Col([
            #     dash_utils.get_chart_card()
            # ], sm=12, md=12, lg=6),
        ]),
    ])
    return chart_container


app.layout = dash_utils.get_dash_layout(filter_container(), chart_container())


@app.callback(
    Output(chart_stock_dio_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(dropdown_avg_quantity_period_id, 'value'),
        Input(radioitems_avg_sale_period_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(input_avg_sale_date_range_id, 'start_date'),
        Input(input_avg_sale_date_range_id, 'end_date'),
        Input(input_dio_low_id, 'value'),
        Input(input_dio_high_id, 'value'),
        Input(radioitems_chart_type_id, 'value'),
        Input(bool_include_weekend_id, 'value'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_charts(
        category_ids,
        product_ids,
        avg_quantity_period,
        avg_sale_period,
        inventory_date_start,
        inventory_date_end,
        sold_at_start_date,
        sold_at_end_date,
        dio_level_low,
        dio_level_high,
        chart_type,
        include_weekend,
        group_by):
    queryset_product = StockControl.get_stock_dio(
        sold_at_start_date,
        sold_at_end_date,
        avg_quantity_period,
        avg_sale_period,
        inventory_date_start=inventory_date_start,
        inventory_date_end=inventory_date_end,
        category_ids=category_ids,
        product_ids=product_ids,
        include_weekend=include_weekend,
        group_by=group_by,
    )
    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Stock DIO Counter of {} by Date Interval'.format(
        group_by)
    chart_layout['xaxis'] = dict(title=f'{group_by.capitalize()}')
    chart_layout['yaxis'] = dict(title='DIO counter')
    chart_layout['barmode'] = chart_type
    chart_layout['colorway'] = ['tomato', 'orange', 'darkseagreen']
    chart_layout['legend'] = dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1,
    )


    # Group data by category as a preparation for plotting
    dataset_grouped_product = utils.count_dio_average_by_level_range(
        queryset_product,
        dio_level_low,
        dio_level_high,
        category_key='stock__product__category__reference' if group_by == 'category' else 'stock__product__reference',
        x_key='avg_dio',
    )

    # Build chart data
    chartdata_product = utils.build_dio_chart_series(
        dataset_grouped_product, dio_level_low, dio_level_high)


    # figure = {'data': chartdata, 'layout': layout}
    figure_product = {'data': chartdata_product, 'layout': chart_layout}

    return figure_product


@app.callback(
    Output(chart_avg_delivered_quantity_by_product, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(dropdown_avg_quantity_period_id, 'value'),
        Input(radioitems_avg_sale_period_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(input_avg_sale_date_range_id, 'start_date'),
        Input(input_avg_sale_date_range_id, 'end_date'),
        Input(input_dio_low_id, 'value'),
        Input(input_dio_high_id, 'value'),
        Input(radioitems_chart_type_id, 'value'),
        Input(bool_include_weekend_id, 'value'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_chart(
        category_ids,
        product_ids,
        avg_quantity_period,
        avg_sale_period,
        inventory_date_start,
        inventory_date_end,
        sold_at_start_date,
        sold_at_end_date,
        dio_level_low,
        dio_level_high,
        chart_type,
        include_weekend,
        group_by):

    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Avg. Delivered Quantity by Product in Selected Period'
    chart_layout['xaxis'] = dict(title='Products')
    chart_layout['yaxis'] = dict(title='Average Delivered Quantity')
    chart_layout['barmode'] = chart_type


    # Build chart data for average qunatity
    ## old version (calculate average sale quantity by date range selection)
    avg_delivered_quantity_queryset = StockControl.avg_delivered_quantity_by_product_in_date_range(
        sold_at_start_date,
        sold_at_end_date,
        category_ids,
        product_ids,
    )

    chartdata_avg_quantity = [
        go.Bar(
            # TODO : parameter `named=true` to avoid repetition
            x=list(avg_delivered_quantity_queryset.values_list(
                'stock__product__reference', flat=True)),
            y=list(avg_delivered_quantity_queryset.values_list(
                'avg_quantity', flat=True)),
            name='AVG quantity between {} & {}'.format(
                sold_at_start_date, sold_at_end_date),
        ),
    ]



    # figure = {'data': chartdata, 'layout': layout}
    figure_avg_quantity = {
        'data': chartdata_avg_quantity, 'layout': chart_layout}

    # return figure, figure_category, figure_product
    return figure_avg_quantity


@app.callback(
    Output(chart_stock_dio_2_id, 'figure'),

    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(dropdown_avg_quantity_period_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(radioitems_chart_type_id, 'value'),
        Input(input_dio_low_id, 'value'),
        Input(input_dio_high_id, 'value'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_chart_two(
    category_ids,
    product_ids,
    avg_quantity_period,
    start_date,
    end_date,
    chart_type,
    dio_low_value,
    dio_high_value,
    group_by):
    qs = StockControl.get_stock_value(
        category_ids,
        product_ids,
        start_date,
        end_date,
        avg_quantity_period,
        group_by=group_by
    )

    qs_grouped = common_utils.group_data_by_category(
        qs,
        category_key='stock__product__category__reference' if group_by == 'category' else 'stock__product__reference',
        x_key='inventory_date_truncated',
        y_key='avg_dio'
    )

    chartdata = utils.build_scatter_chart(
        qs_grouped, x_key='x', y_key='y')

    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Stock DIO (2)'
    chart_layout['xaxis'] = dict(
        title='Date in {}s'.format(avg_quantity_period.capitalize()))
    chart_layout['yaxis'] = dict(title='DIOs')
    chart_layout['barmode'] = chart_type
    chart_layout['shapes'] = [
        dict(
            type='rect',
            yref='paper',
            xref='paper',
            y0=0,
            x0=0,
            y1=1,
            x1=1,
            fillcolor='darkseagreen',
            opacity=0.5,
            layer='below',
            line=dict(
                color='darkseagreen',
                width=1,
            )

        ),
        dict(
            type='rect',
            yref='y',
            xref='paper',
            y0=dio_low_value,
            x0=0,
            y1=dio_high_value,
            x1=1,
            fillcolor='orange',
            opacity=0.5,
            layer='below',
            line=dict(
                color='orange',
                width=1,
            )
        ),
        dict(
            type='rect',
            yref='y',
            xref='paper',
            y0=0,
            x0=0,
            y1=dio_low_value,
            x1=1,
            fillcolor='tomato',
            opacity=0.5,
            layer='below',
            line=dict(
                color='tomato',
                width=1,
            )
        ),
    ]


    figure = {'data': chartdata, 'layout': chart_layout}
    return figure


@app.callback(
    Output(chart_stock_dio_3_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(dropdown_avg_quantity_period_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(radioitems_chart_type_id, 'value'),
        Input(input_dio_low_id, 'value'),
        Input(input_dio_high_id, 'value'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_chart_three(
    category_ids,
    product_ids,
    avg_quantity_period,
    start_date,
    end_date,
    chart_type,
    dio_low_value,
    dio_high_value,
    group_by,
):

    qs = StockControl.get_stock_value(
        category_ids,
        product_ids,
        start_date,
        end_date,
        avg_quantity_period,
        group_by=group_by
    )

    qs_grouped = common_utils.group_data_by_category(
        qs,
        category_key='stock__product__category__reference' if group_by == 'category' else 'stock__product__reference',
        x_key='inventory_date_truncated',
        y_key='avg_dio'
    )

    chartdata = common_utils.build_chart_series(qs_grouped)

    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Average Stock DIO Over Time by {}'.format(
        group_by.capitalize())
    chart_layout['xaxis'] = dict(
        title='Date in {}s'.format(avg_quantity_period.capitalize()))
    chart_layout['yaxis'] = dict(title='DIOs')
    chart_layout['barmode'] = chart_type

    figure = {'data': chartdata, 'layout': chart_layout}
    return figure

@app.callback(
    Output(chart_stock_dio_4_id, 'figure'),
    [
        Input(dropdown_categories_id, 'value'),
        Input(dropdown_products_id, 'value'),
        Input(dropdown_avg_quantity_period_id, 'value'),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(radioitems_chart_type_id, 'value'),
        Input(input_dio_low_id, 'value'),
        Input(input_dio_high_id, 'value'),
        Input(dropdown_group_by_field_id, 'value'),
    ]
)
def update_chart_four(
    category_ids,
    product_ids,
    avg_quantity_period,
    start_date,
    end_date,
    chart_type,
    dio_low_value,
    dio_high_value,
    group_by_field,
):
    filter_kwargs = {}
    filter_kwargs['inventory_date__gte'] = start_date
    filter_kwargs['inventory_date__lte'] = end_date
    filter_kwargs['stock__product__category__in'] = ProductCategory.tree.filter(
        pk__in=category_ids).get_descendants(include_self=True)
    filter_kwargs['stock__product__in'] = product_ids

    qs = StockControl.objects.annotate_count_avg_dio(
        dio_low_value,
        dio_high_value,
        filter_kwargs=filter_kwargs,
        group_by_field=group_by_field,
        kind=avg_quantity_period,
    )
    x_axis = list(qs.values_list(
        'inventory_date_truncated', flat=True))
    y_axis_1 = list(qs.values_list(
        'count_avg_dio_lev1', flat=True))
    y_axis_2 = list(qs.values_list(
        'count_avg_dio_lev2', flat=True))
    y_axis_3 = list(qs.values_list(
        'count_avg_dio_lev3', flat=True))


    # Prepare chart elements
    # Chart data
    chart_data = [
        go.Bar(
            x=x_axis,
            y=y_axis_1,
            name='DIO less than {} days'.format(dio_low_value),
        ),
        go.Bar(
            x=x_axis,
            y=y_axis_2,
            name='DIO between [{}, {}[ days'.format(
                dio_low_value, dio_high_value),
        ),
        go.Bar(
            x=x_axis,
            y=y_axis_3,
            name='DIO more than {} days'.format(dio_high_value),
        ),
    ]

    chart_layout = copy.deepcopy(dash_constants.layout)
    chart_layout['title'] = 'Stock DIO Counter Over Time by Date Interval'
    chart_layout['xaxis'] = dict(
        title='Date in {}s'.format(avg_quantity_period.capitalize()))
    chart_layout['yaxis'] = dict(title='DIO counter')
    chart_layout['barmode'] = chart_type
    chart_layout['colorway'] = ['tomato', 'orange', 'darkseagreen']
    chart_layout['legend'] = dict(
        orientation="h",
        yanchor="bottom",
        x=0,
        y=1,
    )

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

