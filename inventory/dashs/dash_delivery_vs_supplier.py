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
from stock.models import Product, ProductCategory, Order, Supplier, OrderDetail, DeliveryDetail
from dash.exceptions import PreventUpdate
from django.db.models import Avg, Count, Min, Sum, F
import cufflinks as cf
import numpy as np
import statistics
from django_pandas.io import read_frame
import cufflinks as cf
from plotly.subplots import make_subplots
import time

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('DeliverySupplier',add_bootstrap_links=True)
_prefix = 'delivery'

#------------------------------------------{Id Graph}--------------------------------------------------------

figure_count_deliveries_id           = dash_utils.generate_html_id(_prefix, 'figure_count_deliverys_id')
figure_count_product_id              = dash_utils.generate_html_id(_prefix, 'figure_count_product_id')
figure_most_delivred_product_id      = dash_utils.generate_html_id(_prefix, 'figure_most_delivred_product_id')
figure_most_delivred_supplier_id     = dash_utils.generate_html_id(_prefix, 'figure_most_delivred_supplier_id')
figure_pie_statuts_product_id        = dash_utils.generate_html_id(_prefix, 'figure_pie_statuts_product_id')
figure_most_delivred_categories_id   = dash_utils.generate_html_id(_prefix, 'figure_pie_delivred_categories_id')
figure_pie_cat_id = dash_utils.generate_html_id(_prefix, 'figure_pie_cat_id')
figure_pie_abc_id = dash_utils.generate_html_id(_prefix, 'figure_pie_abc_id')
figure_pie_fmr_id = dash_utils.generate_html_id(_prefix, 'figure_pie_fmr_id')


#------------------------------------------------------------------------------------------------------------

details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')

#--------------------------------------------Dropdown  list -------------------------------------------------

dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
dropdown_categorie_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_categorie_list_id')
dropdown_delivery_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_delivery_list_id')
dropdown_supplier_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_supplier_list_id')
dropdown_statut_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_statut_list_id')
dropdown_fmr_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_fmr_list_id')
dropdown_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_warehouse_list_id')
dropdown_abc_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_abc_list_id')

#--------------------------------------------Div list -------------------------------------------
div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
div_delivery_list_id = dash_utils.generate_html_id(_prefix, 'div_delivery_list_id')
div_categorie_list_id = dash_utils.generate_html_id(_prefix, 'div_categorie_list_id')
div_supplier_list_id = dash_utils.generate_html_id(_prefix, 'div_supplier_list_id')
div_statut_list_id = dash_utils.generate_html_id(_prefix, 'div_statut_list_id')
div_fmr_list_id = dash_utils.generate_html_id(_prefix, 'div_fmr_list_id')
div_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'div_warehouse_list_id')
div_abc_list_id = dash_utils.generate_html_id(_prefix, 'div_abc_list_id')

#--------------------------------------------Checkbox list --------------------------------------
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
checkbox_categorie_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_categorie_list_id')
checkbox_delivery_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_delivery_list_id')
checkbox_supplier_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_supplier_list_id')
checkbox_statut_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_statut_list_id')
checkbox_fmr_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_fmr_list_id')
checkbox_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_fmr_list_id')
checkbox_abc_list_id = dash_utils.generate_html_id(_prefix, 'dcheckbox_abc_list_id')


input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

_all_products = list(Product.objects.get_all_products())
_all_categories = list(ProductCategory.objects.get_all_productcategory())
_all_suppliers = list(Supplier.objects.get_all_suppliers())
_all_status = list(Product.objects.get_all_status_of_products())
_all_fmr_segmentation = list(Product.objects.get_all_fmr_segmentation_of_products())
_all_abc_segmentation = list(Product.objects.get_all_abc_segmentation_of_products())

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
                    _('Categories'))
            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_abc_list_id, div_abc_list_id, checkbox_abc_list_id, _all_abc_segmentation, _('ABC Segmentation'))
            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_fmr_list_id, div_fmr_list_id, checkbox_fmr_list_id, _all_fmr_segmentation,
                    _('FMR Segmentation')),
                html.Div(id="number-out"),
            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_supplier_list_id, div_supplier_list_id, checkbox_supplier_list_id, _all_suppliers,
                    _('suppliers'),select_all=False,multi=False)
            ], sm=12, md=6, lg=3),
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
                                                label=_('Graph Number Of deliveries'),
                                                value='what-is',
                                                children=
                                                dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_count_deliveries_id)],
                                                        className="",
                                                    ),
                                                ),
                                            ),
                                            dcc.Tab(
                                                label=_('Number Of Products'),
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
                                                label=_('Top 10 Products'),
                                                value='what-is',
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_most_delivred_product_id)],
                                                        className="",
                                                    )
                                                ),
                                            ),
                                            # dcc.Tab(
                                            #     label=_('Top 10 suppliers '),
                                            #     value='show-sequences',
                                            #     children=html.Div(
                                            #         className='control-tab',
                                            #         children=[
                                            #             dcc.Loading(
                                            #                 html.Div(
                                            #                     className='app-controls-block',
                                            #                     children=html.Div(
                                            #                         [dcc.Graph(id=figure_most_delivred_supplier_id)],
                                            #                         className="",
                                            #                     ),
                                            #                 ),
                                            #             ),
                                            #         ]
                                            #     )
                                            # ),
                                            dcc.Tab(
                                                label=_('Top 10 Categories'),
                                                value='show-sequences-',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        dcc.Loading(
                                                            html.Div(
                                                                className='app-controls-block',
                                                                children=html.Div(
                                                                    [dcc.Graph(id=figure_most_delivred_categories_id)],
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
                            [
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_cat_id),
                                        html.P(_('Categories'),className='font-weight-bold text-primary  h6  text-center'),
                                    ], sm=12, md=6, lg=4),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_abc_id),
                                        html.P(_('ABC Segmentation '),className='font-weight-bold text-primary  h6  text-center'),
                                    ], sm=12, md=6, lg=4),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_fmr_id),
                                        html.P(_('FMR Segmentation'),className='font-weight-bold text-primary  h6  text-center'),
                                    ], sm=12, md=6, lg=4)
                                ])
                            ],
                            className="pretty_container",
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

    Output(figure_count_deliveries_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_suppliers, selected_abc,
                                    selected_fmr, start_date,
                            end_date):
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        delivery__delivered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        delivery__delivered_at__lte=end_date)
    results = results.values('delivery__delivered_at', 'delivery').distinct()
    results = results.values('delivery__delivered_at').annotate(count=Count('delivery'))
    results = results.values('delivery__delivered_at', 'count')

    order_df = read_frame(results)

    figure = order_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['delivery__delivered_at'],
        y=['count'],
        theme='white',
        title=_('Number of Deliveries by date '),
        xTitle=_('date'),
        yTitle=_('Number of Deliveries'),
    )

    return figure


@app.callback(

    Output(figure_count_product_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_suppliers, selected_abc,
                                    selected_fmr, start_date,
                            end_date):
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        delivery__delivered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        delivery__delivered_at__lte=end_date)

    qs = results.values('delivery__delivered_at')
    qs = qs.annotate(delivered_quantity_sum=Sum(F('delivered_quantity')))
    qs = qs.values('delivery__delivered_at', 'delivered_quantity_sum')

    order_df = read_frame(qs)

    figure = order_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['delivery__delivered_at'],
        y=['delivered_quantity_sum'],
        theme='white',
        title=_('Quantity of Products by Date'),
        xTitle=_('date'),
        yTitle=_('Quantity'),
    )

    return figure


@app.callback(

    Output(figure_most_delivred_product_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_order_product_figure(selected_products, selected_categories, selected_suppliers, selected_abc,
                                    selected_fmr,
                                   start_date, end_date):
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        delivery__delivered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        delivery__delivered_at__lte=end_date)
    # results = results.values('product', 'ordered_quantity')
    qs = results.values('product').annotate(delivered_quantity=Sum('delivered_quantity')).order_by('-delivered_quantity')[:10]
    


    # TODO fix the order by product

    order_df = read_frame(qs)
    
    order_df =  order_df.sort_values('delivered_quantity',ascending = True)

    figure = order_df.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['product'],
        y=['delivered_quantity'],
        theme='white',
        title=_('Most Products by Quantity'),
        xTitle=_('Quantity'),
        yTitle=_('Most Products'),
    )
    return figure


# @app.callback(

#     Output(figure_most_delivred_supplier_id, "figure"),

#     [
#         Input(dropdown_product_list_id, "value"),
#         Input(dropdown_categorie_list_id, "value"),
#         Input(dropdown_supplier_list_id, "value"),
#         Input(dropdown_abc_list_id, "value"),
#         Input(dropdown_fmr_list_id, "value"),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def plot_most_order_custmoer_figure(selected_products, selected_categories, selected_suppliers, selected_abc,
#                                     selected_fmr,
#                                     start_date, end_date):
#     results = DeliveryDetail.objects.filter(
#         product__in=selected_products,
#         product__category__in=selected_categories,
#         product__fmr_segmentation__in=selected_fmr,
#         product__abc_segmentation__in=selected_abc,
#         delivery__delivered_at__gte=start_date,
#         supplier__in=[selected_suppliers],
#         delivery__delivered_at__lte=end_date)

#     results = results.values('supplier')
#     results = results.annotate(delivered_quantity=Sum('delivered_quantity'))
#     results = results.order_by('delivered_quantity')[0:10]

#     order_df = read_frame(results)

#     figure = order_df.iplot(
#         asFigure=True,
#         kind='barh',
#         barmode='stack',
#         x=['supplier'],
#         y=['delivered_quantity'],
#         theme='white',
#         title='title',
#         xTitle='date',
#         yTitle='Most Order Custmoers',
#     )
#     return figure


@app.callback(

    Output(figure_most_delivred_categories_id, "figure"),

    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_order_categories_figure(selected_products, selected_categories, selected_suppliers, selected_abc,
                                    selected_fmr,
                                      start_date, end_date):
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        delivery__delivered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        delivery__delivered_at__lte=end_date)

    results = results.values('product__category__reference')
    results = results.annotate(delivered_quantity=Sum('delivered_quantity'))
    results = results.order_by('-delivered_quantity')[:10]

    order_df = read_frame(results)
    
    order_df =  order_df.sort_values('delivered_quantity',ascending = True)

    figure = order_df.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['product__category__reference'],
        y=['delivered_quantity'],
        theme='white',
        title=_('Most 10 Categories by Quantity'),
        xTitle=_('Quantity'),
        yTitle=_('Categories'),
    )
    return figure


@app.callback(

    [
        Output(figure_pie_abc_id, "figure"),
        Output(figure_pie_fmr_id, "figure"),
        Output(figure_pie_cat_id, "figure"),
    ],
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_supplier_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_pie_statuts_product_figure(selected_products, selected_categories, selected_suppliers, selected_abc,
                                    selected_fmr,
                                    start_date, end_date):
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        delivery__delivered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        delivery__delivered_at__lte=end_date)
    results = results.values('delivered_quantity', 'product__category__reference','product__abc_segmentation','product__fmr_segmentation')

    results_category = results.values('product__category__reference')
    results_category = results_category.annotate(delivered_quantity=Sum('delivered_quantity'))
    results_category = results_category.order_by('delivered_quantity')


    results_abc = results.values('product__abc_segmentation')
    results_abc = results_abc.annotate(delivered_quantity=Sum('delivered_quantity'))
    results_abc = results_abc.order_by('delivered_quantity')
    
    results_fmr = results.values('product__fmr_segmentation')
    results_fmr = results_fmr.annotate(delivered_quantity=Sum('delivered_quantity'))
    results_fmr = results_fmr.order_by('delivered_quantity')



    ordered_category_df = read_frame(results_category)
    ordered_abc_df = read_frame(results_abc)
    ordered_fmr_df = read_frame(results_fmr)
    

    figure_cat = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    figure_abc = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    figure_fmr = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    
    figure_cat.add_trace(
        go.Pie(
            labels=ordered_category_df['product__category__reference'],
            values=ordered_category_df['delivered_quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'red',
                    'rgb(0,255,0)',
                    'rgb(255, 255, 0)'
                ]
            },
        )
    , 1, 1)
    
    figure_abc.add_trace(
        go.Pie(
            labels=ordered_abc_df['product__abc_segmentation'],
            values=ordered_abc_df['delivered_quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'red',
                    'rgb(0,255,0)',
                    'rgb(255, 255, 0)'
                ]
            },
        )
    , 1, 1)
        
    figure_fmr.add_trace(
        go.Pie(
            labels=ordered_fmr_df['product__fmr_segmentation'],
            values=ordered_fmr_df['delivered_quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'red',
                    'rgb(0,255,0)',
                    'rgb(255, 255, 0)'
                ]
            },
        )
    , 1, 1)
    
    figure_cat.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure_abc.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure_fmr.update_traces(hole=.4, hoverinfo="label+percent+name")

    return figure_abc,figure_fmr,figure_cat


dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_supplier_list_id, div_supplier_list_id, checkbox_supplier_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_fmr_list_id, div_fmr_list_id, checkbox_fmr_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_abc_list_id, div_abc_list_id, checkbox_abc_list_id)
