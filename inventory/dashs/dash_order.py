# Import required libraries
import copy
import datetime as dt
import math
import pathlib
import time
import pickle
import urllib.request
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from common.dashboards import dash_constants, dash_utils
from dash.dependencies import ClientsideFunction, Input, Output, State
from django.db.models import Q
from django.utils.translation import gettext as _
from django_plotly_dash import DjangoDash
from inventory.models import Location, StockCheck, Operation
from plotly import offline
from stock.models import Product, ProductCategory, Order, Customer, OrderDetail
from dash.exceptions import PreventUpdate
from django.db.models import Avg, Count, Min, Sum
import cufflinks as cf
import numpy as np
import statistics
from django_pandas.io import read_frame
import cufflinks as cf
from plotly.subplots import make_subplots
import colorlover, plotly

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('Order', add_bootstrap_links=True)
_prefix = 'delivery'

# ------------------------------------------{Id Graph}--------------------------------------------------------

figure_count_orders_id = dash_utils.generate_html_id(_prefix, 'figure_count_orders_id')
figure_count_product_id = dash_utils.generate_html_id(_prefix, 'figure_count_product_id')
figure_most_ordred_product_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_product_id')
figure_most_ordred_customer_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_customer_id')
figure_pie_statuts_product_id = dash_utils.generate_html_id(_prefix, 'figure_pie_statuts_product_id')
figure_most_ordred_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_ordred_categories_id')

# ------------------------------------------------------------------------------------------------------------

details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')
details_customer_list_id = dash_utils.generate_html_id(_prefix, 'details_customer_list_id')

# --------------------------------------------Dropdown  list -------------------------------------------------

dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
dropdown_categorie_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_categorie_list_id')
dropdown_order_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_order_list_id')
dropdown_customer_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_customer_list_id')
dropdown_statut_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_statut_list_id')

# --------------------------------------------Div list -------------------------------------------
div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
div_order_list_id = dash_utils.generate_html_id(_prefix, 'div_order_list_id')
div_categorie_list_id = dash_utils.generate_html_id(_prefix, 'div_categorie_list_id')
div_customer_list_id = dash_utils.generate_html_id(_prefix, 'div_customer_list_id')
div_statut_list_id = dash_utils.generate_html_id(_prefix, 'div_statut_list_id')

# --------------------------------------------Checkbox list --------------------------------------
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
checkbox_categorie_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_categorie_list_id')
checkbox_order_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_order_list_id')
checkbox_customer_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_customer_list_id')
checkbox_statut_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_statut_list_id')

input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

table_forecast_dataframe_id = _prefix + '-table-forecast-dataframe'

_all_products = list(Product.objects.get_all_products())
_all_categories = list(ProductCategory.objects.get_all_productcategory())
_all_customers = list(Customer.objects.get_all_customers())[:1]
_all_status = list(Product.objects.get_all_status_of_products())[:100]

print('i am here ')
# _all_orderDetails = OrderDetail.objects.all()
# _all_orders = Order.objects.all()

layout = dict(
    autosize=True,
    automargin=True,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
)

cs12 = colorlover.scales['12']['qual']['Paired']


def filter_container():
    filter_container = html.Div([

        dbc.Row([
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id, _all_categories,
                    'Categories')
            ], sm=12, md=6, lg=4),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id, _all_status, 'Status')
            ], sm=12, md=6, lg=4),
            html.Details([
                html.Summary(_('Customer')),
                dbc.Col([
                    dash_utils.get_filter_dropdown(
                        dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id, _all_customers,
                        'Customers')
                ], sm=12, md=6, lg=4),
            ], id=details_customer_list_id, open=False),
            dbc.Col([
                dash_utils.get_date_range(
                    input_date_range_id,
                    label=_('Time horizon'),
                    year_range=2
                ),
            ], sm=12, md=6, lg=6),
        ]),

        html.Details([
            html.Summary(_('Products')),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_product_list_id, div_product_list_id, checkbox_product_list_id, _all_products, '')
            ], sm=12, md=12, lg=12),
        ], id=details_product_list_id, open=False),
    ])
    return filter_container


def body_container():
    body_container = html.Div(
        [
            dbc.Row([
                dbc.Col([
                    html.Div(
                        id='forna-body-1',
                        className='shadow-lg p-12 mb-5 bg-white rounded',
                        children=[
                            html.Div(
                                id='forna-control-tabs',
                                className='control-tabs',
                                children=[
                                    dcc.Tabs(
                                        id='forna-tabs',
                                        value='what-is',
                                        children=[
                                            dcc.Tab(
                                                label='Graph Number Of Orders          ',
                                                value='what-is',
                                                children=html.Div(
                                                    [dcc.Graph(id=figure_count_orders_id)],
                                                    className="",
                                                ),
                                            ),
                                            dcc.Tab(
                                                label='Number Of Ordered Products',
                                                value='Product',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=html.Div(
                                                                [dcc.Graph(id=figure_count_product_id)],
                                                                className="",
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ])
                                ]
                            ),
                            dcc.Store(id='forna-custom-colors-1')
                        ]
                    ),
                ], sm=12, md=6, lg=6),
                dbc.Col([
                    html.Div(
                        id='forna-body-2',
                        className='shadow-lg p-12 mb-5 bg-white rounded',
                        children=[
                            html.Div(
                                id='forna-control-tabs-2',
                                className='control-tabs',
                                children=[
                                    dcc.Tabs(
                                        id='forna-tabs',
                                        value='what-is',
                                        children=[
                                            dcc.Tab(
                                                label='Top 10 Ordred Products',
                                                value='what-is',
                                                children=html.Div(
                                                    [dcc.Graph(id=figure_most_ordred_product_id)],
                                                    className="",
                                                ),
                                            ),
                                            dcc.Tab(
                                                label='Top 10 Customers Making Orders',
                                                value='show-sequences',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=html.Div(
                                                                [dcc.Graph(id=figure_most_ordred_customer_id)],
                                                                className="",
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                            dcc.Tab(
                                                label='Top 10 Ordred  Categories',
                                                value='show-sequences-',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=html.Div(
                                                                [dcc.Graph(id=figure_most_ordred_categories_id)],
                                                                className="",
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ])
                                ]
                            ),
                            dcc.Store(id='forna-custom-colors-2')
                        ]
                    ),
                ], sm=12, md=6, lg=6),
            ]),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id=figure_pie_statuts_product_id)],
                        className="pretty_container",
                    ),
                ],
                className="shadow-lg p-12 mb-5 bg-white rounded",
            ),
            dbc.Row([
                dbc.Col([
                    dash_utils.get_datatable_card(table_forecast_dataframe_id)
                ], sm=12, md=12, lg=12),
            ]),

        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    return body_container


app.layout = dash_utils.get_dash_layout(filter_container(), body_container())


@app.callback(
    [
        Output(figure_count_orders_id, "figure"),
        Output(figure_count_product_id, "figure"),
        Output(figure_most_ordred_product_id, "figure"),
        Output(figure_most_ordred_customer_id, "figure"),
        Output(figure_most_ordred_categories_id, "figure"),
        Output(figure_pie_statuts_product_id, "figure"),
    ],
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_product_figure(selected_products, selected_categories, selected_customers, selected_status,
                                    start_date, end_date):
    results = OrderDetail.objects.filter(
            product__in=selected_products,
            # product__category__in=selected_categories,
            # product__status__in=selected_status,
            order__ordered_at__gte=start_date,
            # customer__in=selected_customers,
            order__ordered_at__lte=end_date)

    results = results.select_related('order', 'product')
    results = results.values('order__ordered_at', 'ordered_quantity','product','customer','product__category__reference','product__status')
    print(results)
    print('result done')



    order_df = read_frame(results)

    print('desert')

    order_count_products_df = order_df.groupby(
        by=['order__ordered_at'],
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index()


    order_count_orders_df = order_df.groupby(
        by=['order__ordered_at'],
    ).size().reset_index(name='counts')

    order_most_ordred_product_df = order_df.groupby(
        by=['product'],
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index().sort_values(['ordered_quantity'],ascending=True)[:10]

    order_most_ordred_customer_df = order_df.groupby(
        by=['customer'],
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index().sort_values(['ordered_quantity'],ascending=True)[:10]

    order_most_ordred_category_df = order_df.groupby(
        by=['product__category__reference'],
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index().sort_values(['ordered_quantity'],ascending=True)[:10]



    order_status_df = order_df.groupby(
        by=['product__status'],
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index().sort_values(['ordered_quantity'],ascending=True)

    orderd_category_df = order_df.groupby(
        by=['product__category__reference'],
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index().sort_values(['ordered_quantity'],ascending=True)

    figure_pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])

    figure_pie.add_trace(go.Pie(labels=order_status_df['product__status'], values=order_status_df['ordered_quantity'], name=""),1, 1)

    figure_pie.add_trace(go.Pie(labels=orderd_category_df['product__category__reference'], values=orderd_category_df['ordered_quantity'], name=""),1, 2)

    figure_pie.update_traces(hole=.4, hoverinfo="label+percent+name")

    figure_pie.update_layout(
        title_text="Pie Chart",
        annotations=[
            dict(text='Status', x=0.21, y=0.5, font_size=20, showarrow=False),
            dict(text='Categories', x=0.805, y=0.5, font_size=20, showarrow=False)
        ]
    )

    figure_most_ordred_category = order_most_ordred_category_df.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['product__category__reference'],
        y=['ordered_quantity'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Most 10 Order categories',
    )

    figure_most_ordred_customer = order_most_ordred_customer_df.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['customer'],
        y=['ordered_quantity'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Most Order Custmoers',
    )

    figure_most_ordred_product = order_most_ordred_product_df.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['product'],
        y=['ordered_quantity'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Most Ordered  Products',
    )

    figure_count_orders = order_count_orders_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['order__ordered_at'],
        y=['counts'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Numbre of Orders',
    )

    figure_count_product = order_count_products_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['order__ordered_at'],
        y=['ordered_quantity'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Numbre of Products',
    )
    return figure_count_orders,figure_count_product,figure_most_ordred_product,figure_most_ordred_customer, figure_most_ordred_category,figure_pie


# @app.callback(
#
#     Output(figure_count_orders_id, "figure"),
#     [
#         Input(table_forecast_dataframe_id, 'data'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_order_count_figure(data,end):
#     # results = OrderDetail.objects.filter(
#     #         product__in=selected_products,
#     #         # product__category__in=selected_categories,
#     #         # product__status__in=selected_status,
#     #         order__ordered_at__gte=start_date,
#     #         # customer__in=selected_customers,
#     #         order__ordered_at__lte=end_date
#     # )
#
#     # results = results.values('order__ordered_at','order')
#
#     print('1182')
#
#     order_df = pd.DataFrame.from_dict(data)
#
#
#     # order_df = order_df.groupby(
#     #     by=['order__ordered_at','order'],
#     # ).size()
#
#     if len(order_df) == 0:
#         figure = order_df.iplot(
#             asFigure=True,
#             kind='bar',
#             barmode='stack',
#             x=None,
#             y=None,
#             theme='white',
#             title='title',
#             xTitle='date',
#             yTitle='Numbre of Orders',
#         )
#     else:
#         order_df = order_df.groupby(
#             by=['order__ordered_at'],
#         ).size().reset_index(name='counts')
#
#         figure = order_df.iplot(
#             asFigure=True,
#             kind='bar',
#             barmode='stack',
#             x=['order__ordered_at'],
#             y=['counts'],
#             theme='white',
#             title='title',
#             xTitle='date',
#             yTitle='Numbre of Orders',
#         )
#     return figure
#
#
# @app.callback(
#
#     Output(figure_count_product_id, "figure"),
#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_customer_list_id, "value"),
#         Input(dropdown_statut_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_order_count_product_figure(selected_products, selected_categories, selected_customers, selected_status,
#                                     start_date, end_date):
#     # results = OrderDetail.objects.filter(
#     #         product__in=selected_products,
#     #         # product__category__in=selected_categories,
#     #         # product__status__in=selected_status,
#     #         order__ordered_at__gte=start_date,
#     #         # customer__in=selected_customers,
#     #         order__ordered_at__lte=end_date)
#
#     results = _all_orderDetails.values('order__ordered_at', 'ordered_quantity')
#
#     print('2')
#
#     order_df = read_frame(results)
#
#     print('1')
#
#     order_df = order_df.groupby(
#         by=['order__ordered_at'],
#     ).agg({
#         'ordered_quantity': 'sum',
#     }).reset_index()
#
#     figure = order_df.iplot(
#         asFigure=True,
#         kind='bar',
#         barmode='stack',
#         x=['order__ordered_at'],
#         y=['ordered_quantity'],
#         theme='white',
#         title='title',
#         xTitle='date',
#         yTitle='Numbre of Products',
#     )
#     return figure


#
#
# @app.callback(
#
#     Output(figure_most_ordred_product_id, "figure"),
#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_customer_list_id, "value"),
#         Input(dropdown_statut_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_most_order_product_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
#     results = OrderDetail.objects.filter(
#             product__in=selected_products,
#             # product__category__in=selected_categories,
#             # product__status__in=selected_status,
#             order__ordered_at__gte=start_date,
#             # customer__in=selected_customers,
#             order__ordered_at__lte=end_date)
#     results = results.values('product','ordered_quantity')
#
#     order_df = read_frame(results)
#
#     print(order_df)
#
#     order_df = order_df.groupby(
#         by=['product'],
#     ).agg({
#         'ordered_quantity': 'sum',
#     }).reset_index().sort_values(['ordered_quantity'],ascending=True)[:10]
#
#     figure = order_df.iplot(
#         asFigure=True,
#         kind='barh',
#         barmode='stack',
#         x=['product'],
#         y=['ordered_quantity'],
#         theme='white',
#         title='title',
#         xTitle='date',
#         yTitle='Most Ordered  Products',
#     )
#     return figure
#
# @app.callback(
#
#     Output(figure_most_ordred_customer_id, "figure"),
#
#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_customer_list_id, "value"),
#         Input(dropdown_statut_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_most_order_custmoer_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
#
#     results = OrderDetail.objects.filter(
#         product__in=selected_products,
#         # product__category__in=selected_categories,
#         # product__status__in=selected_status,
#         order__ordered_at__gte=start_date,
#         # customer__in=selected_customers,
#         order__ordered_at__lte=end_date)
#
#     results = results.values('customer','ordered_quantity')
#
#     order_df = read_frame(results)
#
#     print(order_df)
#
#     order_df = order_df.groupby(
#         by=['customer'],
#     ).agg({
#         'ordered_quantity': 'sum',
#     }).reset_index().sort_values(['ordered_quantity'],ascending=True)[:10]
#
#     figure = order_df.iplot(
#         asFigure=True,
#         kind='barh',
#         barmode='stack',
#         x=['customer'],
#         y=['ordered_quantity'],
#         theme='white',
#         title='title',
#         xTitle='date',
#         yTitle='Most Order Custmoers',
#     )
#     return figure
#
# @app.callback(
#
#     Output(figure_most_ordred_categories_id, "figure"),
#
#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_customer_list_id, "value"),
#         Input(dropdown_statut_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_most_order_categories_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
#
#     results = OrderDetail.objects.filter(
#         product__in=selected_products,
#         # product__category__in=selected_categories,
#         # product__status__in=selected_status,
#         order__ordered_at__gte=start_date,
#         # customer__in=selected_customers,
#         order__ordered_at__lte=end_date)
#
#     results = results.values('product__category__reference','ordered_quantity')
#
#     order_df = read_frame(results)
#
#     print(order_df)
#
#     order_df = order_df.groupby(
#         by=['product__category__reference'],
#     ).agg({
#         'ordered_quantity': 'sum',
#     }).reset_index().sort_values(['ordered_quantity'],ascending=True)[:10]
#
#     figure = order_df.iplot(
#         asFigure=True,
#         kind='barh',
#         barmode='stack',
#         x=['product__category__reference'],
#         y=['ordered_quantity'],
#         theme='white',
#         title='title',
#         xTitle='date',
#         yTitle='Most 10 Order categories',
#     )
#     return figure
#
# @app.callback(
#
#     Output(figure_pie_statuts_product_id, "figure"),
#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_customer_list_id, "value"),
#         Input(dropdown_statut_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_pie_statuts_product_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
#     results = OrderDetail.objects.filter(
#             product__in=selected_products,
#             # product__category__in=selected_categories,
#             # product__status__in=selected_status,
#             order__ordered_at__gte=start_date,
#             # customer__in=selected_customers,
#             order__ordered_at__lte=end_date)
#     results = results.values('product__status','ordered_quantity','product__category__reference')
#
#     order_df = read_frame(results)
#
#     orderd_category_df = read_frame(results)
#
#     order_df = order_df.groupby(
#         by=['product__status'],
#     ).agg({
#         'ordered_quantity': 'sum',
#     }).reset_index().sort_values(['ordered_quantity'],ascending=True)
#
#     orderd_category_df = orderd_category_df.groupby(
#         by=['product__category__reference'],
#     ).agg({
#         'ordered_quantity': 'sum',
#     }).reset_index().sort_values(['ordered_quantity'],ascending=True)
#
#     figure = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
#
#     figure.add_trace(go.Pie(labels=order_df['product__status'], values=order_df['ordered_quantity'], name=""),1, 1)
#
#     figure.add_trace(go.Pie(labels=orderd_category_df['product__category__reference'], values=orderd_category_df['ordered_quantity'], name=""),1, 2)
#
#     figure.update_traces(hole=.4, hoverinfo="label+percent+name")
#
#     figure.update_layout(
#         title_text="Pie Chart",
#         annotations=[
#             dict(text='Status', x=0.21, y=0.5, font_size=20, showarrow=False),
#             dict(text='Categories', x=0.805, y=0.5, font_size=20, showarrow=False)
#         ]
#     )
#     return figure

#
# @app.callback(
#     [
#         # Dataframe
#         Output(table_forecast_dataframe_id, 'data'),
#         Output(table_forecast_dataframe_id, 'columns'),
#     ],
#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_customer_list_id, "value"),
#         Input(dropdown_statut_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def dataframe_date_filter(selected_products, selected_categories, selected_customers, selected_status, start_date,
#                           end_date):
#     results = OrderDetail.objects.filter(
#         product__in=selected_products,
#         # product__category__in=selected_categories,
#         # product__status__in=selected_status,
#         order__ordered_at__gte=start_date,
#         # customer__in=selected_customers,
#         order__ordered_at__lte=end_date
#     )
#
#     # results = Order.objects.filter(
#     #     # product__category__in=selected_categories,
#     #     # product__status__in=selected_status,
#     #     ordered_at__gte=start_date,
#     #     # customer__in=selected_customers,
#     #     ordered_at__lte=end_date
#     # )
#
#     results = results.values('order__ordered_at')
#
#     print(results)
#
#     order_df = read_frame(results)
#
#     data = order_df.to_dict('records')
#
#     columns = [{"name": i, "id": i} for i in order_df.columns]
#
#     return data,columns


dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id)
