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
from inventory.models import Location, StockCheck
from plotly import offline
from stock.models import Product, ProductCategory, Order, Customer, OrderDetail,Supplier
from dash.exceptions import PreventUpdate
from django.db.models import Avg, Count, Min, Sum,F
import cufflinks as cf
import numpy as np
import statistics
from django_pandas.io import read_frame
import cufflinks as cf
from plotly.subplots import make_subplots
import time


cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('OrderSupplier', add_bootstrap_links=True)
_prefix = 'delivery'

# ------------------------------------------{Id Graph}--------------------------------------------------------

figure_count_orders_id = dash_utils.generate_html_id(_prefix, 'figure_count_orders_id')
figure_count_product_id = dash_utils.generate_html_id(_prefix, 'figure_count_product_id')
figure_most_ordred_product_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_product_id')
figure_most_ordred_supplier_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_supplier_id')
figure_pie_statuts_product_id = dash_utils.generate_html_id(_prefix, 'figure_pie_statuts_product_id')
figure_most_ordred_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_ordred_categories_id')

# ------------------------------------------------------------------------------------------------------------

details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')

# --------------------------------------------Dropdown  list -------------------------------------------------

dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
dropdown_categorie_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_categorie_list_id')
dropdown_order_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_order_list_id')
dropdown_supplier_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_supplier_list_id')
dropdown_statut_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_statut_list_id')

# --------------------------------------------Div list -------------------------------------------
div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
div_order_list_id = dash_utils.generate_html_id(_prefix, 'div_order_list_id')
div_categorie_list_id = dash_utils.generate_html_id(_prefix, 'div_categorie_list_id')
div_supplier_list_id = dash_utils.generate_html_id(_prefix, 'div_supplier_list_id')
div_statut_list_id = dash_utils.generate_html_id(_prefix, 'div_statut_list_id')

# --------------------------------------------Checkbox list --------------------------------------
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
checkbox_categorie_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_categorie_list_id')
checkbox_order_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_order_list_id')
checkbox_supplier_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_supplier_list_id')
checkbox_statut_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_statut_list_id')

input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

_all_products = list(Product.objects.get_all_products())
_all_categories = list(ProductCategory.objects.get_all_productcategory())
_all_suppliers = list(Supplier.objects.get_all_suppliers())[0:10]
_all_status = list(Product.objects.get_all_status_of_products())

layout = dict(
    autosize=True,
    automargin=True,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
)

import colorlover, plotly

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
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_supplier_list_id, div_supplier_list_id, checkbox_supplier_list_id, _all_suppliers,
                    'suppliers')
            ], sm=12, md=6, lg=4),
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
                                                children=
                                                    dcc.Loading(
                                                        html.Div(
                                                            [dcc.Graph(id=figure_count_orders_id)],
                                                            className="",
                                                        ),
                                                    ),
                                            ),
                                            dcc.Tab(
                                                label='Number Of Ordered Products',
                                                value='Product',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        dcc.Loading(
                                                            html.Div(
                                                                className='app-controls-block',
                                                                children=html.Div(
                                                                    [dcc.Graph(id=figure_count_product_id)],
                                                                    className="",
                                                                ),
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
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_most_ordred_product_id)],
                                                        className="",
                                                    )
                                                ),
                                            ),
                                            dcc.Tab(
                                                label='Top 10 suppliers Making Orders',
                                                value='show-sequences',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        dcc.Loading(
                                                            html.Div(
                                                                className='app-controls-block',
                                                                children=html.Div(
                                                                    [dcc.Graph(id=figure_most_ordred_supplier_id)],
                                                                    className="",
                                                                ),
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
                                                        dcc.Loading(
                                                            html.Div(
                                                                className='app-controls-block',
                                                                children=html.Div(
                                                                    [dcc.Graph(id=figure_most_ordred_categories_id)],
                                                                    className="",
                                                                ),
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
                    dcc.Loading(
                        html.Div(
                            className='app-controls-block',
                            children=
                            html.Div(
                                [dcc.Graph(id=figure_pie_statuts_product_id)],
                                className="pretty_container",
                            ),
                        ),
                    ),
                ],
                className="shadow-lg p-12 mb-5 bg-white rounded",
            ),

        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    return body_container


app.layout = dash_utils.get_dash_layout(filter_container(), body_container())


@app.callback(

    Output(figure_count_orders_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_suppliers, selected_status, start_date,
                            end_date):

    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        # supplier__in=selected_suppliers,
        order__ordered_at__lte=end_date)
    results = results.values('order__ordered_at','order').distinct()
    results = results.values('order__ordered_at').annotate(count=Count('order'))
    results = results.values('order__ordered_at', 'count')
    #
    # x = list(results.values_list('order__ordered_at', flat=True))
    # y = list(results.values_list('count', flat=True))
    #
    # figure = go.Figure(data=[
    #     dict(x=x, y=y, type='bar')
    # ])

    start_time_2 = time.time()


    order_df = read_frame(results)

    # order_df = order_df.groupby(
    #     by=['order__ordered_at'],
    # ).size().reset_index(name='counts')
    print("--- %s seconds ------- rrad data frame  ---" % (time.time() - start_time_2))

    start_time_3 = time.time()
    figure = order_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['order__ordered_at'],
        y=['count'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Numbre of Orders',
    )

    print("--- %s seconds ------- fig data frame  ---" % (time.time() - start_time_3))

    start_time_4 = time.time()

    x = list(results.values_list('order__ordered_at', flat=True))
    y = list(results.values_list('count', flat=True))

    print("--- %s seconds ------- fig data frame  ---" % (time.time() - start_time_4))

    figure = go.Figure(data=[
        dict(x=x, y=y, type='bar')
    ])

    print("--- %s seconds ------- go figure  ---" % (time.time() - start_time_4))



    return figure


@app.callback(

    Output(figure_count_product_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_suppliers, selected_status, start_date,
                            end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        # supplier__in=selected_suppliers,
        order__ordered_at__lte=end_date
    )

    # order_df = read_frame(results)
    #
    # order_df = order_df.groupby(
    #     by=['order__ordered_at'],
    # ).agg({
    #     'ordered_quantity': 'sum',
    # }).reset_index()
    #
    # figure = order_df.iplot(
    #     asFigure=True,
    #     kind='bar',
    #     barmode='stack',
    #     x=['order__ordered_at'],
    #     y=['ordered_quantity'],
    #     theme='white',
    #     title='title',
    #     xTitle='date',
    #     yTitle='Numbre of Products',
    # )
    # return figure

    qs = results.values('order__ordered_at')
    qs = qs.annotate(ordered_quantity_sum=Sum(F('ordered_quantity')))
    qs = qs.values('order__ordered_at', 'ordered_quantity_sum')


    order_df = read_frame(qs)


    figure = order_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['order__ordered_at'],
        y=['ordered_quantity_sum'],
        theme='white',
        title='title',
        xTitle='date',
        # yTitle='Numbre of Products',
    )

    return figure


@app.callback(

    Output(figure_most_ordred_product_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_order_product_figure(selected_products, selected_categories, selected_suppliers, selected_status,
                                   start_date, end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        # supplier__in=selected_suppliers,
        order__ordered_at__lte=end_date)
    # results = results.values('product', 'ordered_quantity')
    results = results.values('product')
    results = results.annotate(ordered_quantity=Sum('ordered_quantity'))
    results = results.order_by('ordered_quantity')[0:10]

    order_df = read_frame(results)


    figure = order_df.iplot(
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
    return figure


@app.callback(

    Output(figure_most_ordred_supplier_id, "figure"),

    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_order_custmoer_figure(selected_products, selected_categories, selected_suppliers, selected_status,
                                    start_date, end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        # supplier__in=selected_suppliers,
        order__ordered_at__lte=end_date)

    results = results.values('supplier')
    results = results.annotate(ordered_quantity=Sum('ordered_quantity'))
    results = results.order_by('ordered_quantity')[0:10]


    order_df = read_frame(results)

    figure = order_df.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['supplier'],
        y=['ordered_quantity'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Most Order Custmoers',
    )
    return figure


@app.callback(

    Output(figure_most_ordred_categories_id, "figure"),

    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_order_categories_figure(selected_products, selected_categories, selected_suppliers, selected_status,
                                      start_date, end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        # supplier__in=selected_suppliers,
        order__ordered_at__lte=end_date)

    results = results.values('product__category__reference')
    results = results.annotate(ordered_quantity=Sum('ordered_quantity'))
    results = results.order_by('ordered_quantity')[0:10]

    order_df = read_frame(results)


    figure = order_df.iplot(
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
    return figure


@app.callback(

    Output(figure_pie_statuts_product_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_pie_statuts_product_figure(selected_products, selected_categories, selected_suppliers, selected_status,
                                    start_date, end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        # supplier__in=selected_suppliers,
        order__ordered_at__lte=end_date)
    results = results.values('product__status', 'ordered_quantity', 'product__category__reference')

    results_category = results.values('product__category__reference')
    results_category = results_category.annotate(ordered_quantity=Sum('ordered_quantity'))
    results_category = results_category.order_by('ordered_quantity')


    results_status = results.values('product__status')
    results_status = results_status.annotate(ordered_quantity=Sum('ordered_quantity'))
    results_status = results_status.order_by('ordered_quantity')



    order_df = read_frame(results_status)

    orderd_category_df = read_frame(results_category)

    figure = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])

    figure.add_trace(go.Pie(labels=order_df['product__status'], values=order_df['ordered_quantity'], name=""), 1, 1)

    figure.add_trace(
        go.Pie(labels=orderd_category_df['product__category__reference'], values=orderd_category_df['ordered_quantity'],
               name=""), 1, 2)

    figure.update_traces(hole=.4, hoverinfo="label+percent+name")

    figure.update_layout(
        title_text="Pie Chart",
        annotations=[
            dict(text='Status', x=0.21, y=0.5, font_size=20, showarrow=False),
            dict(text='Categories', x=0.805, y=0.5, font_size=20, showarrow=False)
        ]
    )
    return figure


dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_supplier_list_id, div_supplier_list_id, checkbox_supplier_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id)
