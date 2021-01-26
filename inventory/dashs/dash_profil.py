# Import required libraries
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from common.dashboards import dash_utils
from dash.dependencies import Input, Output
from django.utils.translation import gettext as _
from django_plotly_dash import DjangoDash
from stock.models import Product, ProductCategory, Customer, OrderDetail,Warehouse,Circuit
from inventory.models import  StockCheck
from django_pandas.io import read_frame
import cufflinks as cf

import numpy as np
from plotly.subplots import make_subplots
from django.db.models import F, ExpressionWrapper, DateTimeField,IntegerField,Case, CharField, Value, When,Sum,Max

from multiprocessing import  Pool
import multiprocessing as mp

from django.db import connection
import pandas as pd
import resource


import colorlover, plotly

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('profil', add_bootstrap_links=True)
_prefix = 'profil'

import time



# TODO Avoid to repet query sets  in all callbacks


# ------------------------------------------{Id Graph}--------------------------------------------------------

figure_customer_id = dash_utils.generate_html_id(_prefix, 'figure_customer_id')
figure_ordersDetails_id = dash_utils.generate_html_id(_prefix, 'figure_orderDetails_id')
figure_otif_id = dash_utils.generate_html_id(_prefix, 'figure_otif_id')
figure_most_ordred_product_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_product_id')
figure_most_ordred_customer_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_customer_id')
figure_pie_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_categories_id')
figure_pie_abc_id = dash_utils.generate_html_id(_prefix, 'figure_pie_abc_id')
figure_pie_warehouse_id = dash_utils.generate_html_id(_prefix, 'figure_pie_warehouse_id')
figure_pie_fmr_id = dash_utils.generate_html_id(_prefix, 'figure_pie_fmr_id')
figure_most_ordred_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_ordred_categories_id')
figure_orders_id = dash_utils.generate_html_id(_prefix, 'figure_orders_id')

# ------------------------------------------------------------------------------------------------------------

details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')

# -------------------------------------------- Dropdown  list -------------------------------------------------

dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
dropdown_categorie_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_categorie_list_id')
dropdown_order_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_order_list_id')
dropdown_fmr_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_fmr_list_id')
dropdown_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_warehouse_list_id')
dropdown_abc_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_abc_list_id')

# --------------------------------------------Div list -------------------------------------------

div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
div_order_list_id = dash_utils.generate_html_id(_prefix, 'div_order_list_id')
div_categorie_list_id = dash_utils.generate_html_id(_prefix, 'div_categorie_list_id')
div_fmr_list_id = dash_utils.generate_html_id(_prefix, 'div_fmr_list_id')
div_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'div_warehouse_list_id')
div_abc_list_id = dash_utils.generate_html_id(_prefix, 'div_abc_list_id')

# --------------------------------------------Checkbox list --------------------------------------
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
checkbox_categorie_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_categorie_list_id')
checkbox_order_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_order_list_id')
checkbox_fmr_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_fmr_list_id')
checkbox_warehouse_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_fmr_list_id')
checkbox_abc_list_id = dash_utils.generate_html_id(_prefix, 'dcheckbox_abc_list_id')


# ------------------------------------------------Mini Cards ------------------------------
mini_card_products_number_id = dash_utils.generate_html_id(_prefix, 'mini_card_products_number_id')

mini_card_warehouses_number_id = dash_utils.generate_html_id(_prefix, 'mini_card_warehouses_number_id')

mini_card_categories_number_id = dash_utils.generate_html_id(_prefix, 'mini_card_categories_number_id' )

mini_card_circuits_number_id = dash_utils.generate_html_id(_prefix, 'mini_card_circuits_number_id' )



#-----------------------------------------------------------------------------------------

count_products           = Product.objects.count()
count_product_categories = ProductCategory.objects.count()
count_circuits           = Circuit.objects.count()
count_warhouses          = Warehouse.objects.count()


# -----------------------------------------------------------------------------------------


_all_products   = list(Product.objects.get_all_products())
_all_categories = list(ProductCategory.objects.get_all_productcategory())
_all_warehouses = list(Warehouse.objects.get_all_warehouses())
_all_status     = list(Product.objects.get_all_status_of_products())
_all_customers  = list(Customer.objects.get_all_customers())
_all_fmr_segmentation = list(Product.objects.get_all_fmr_segmentation_of_products())
_all_abc_segmentation = list(Product.objects.get_all_abc_segmentation_of_products())


cs12 = colorlover.scales['12']['qual']['Paired']


def filter_container():
    filter_container = html.Div([

        dbc.Row([
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id, _all_categories,
                    'Categories')
            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_abc_list_id, div_abc_list_id, checkbox_abc_list_id, _all_abc_segmentation, 'ABC Segmentation')
            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_fmr_list_id, div_fmr_list_id, checkbox_fmr_list_id, _all_fmr_segmentation,
                    'FMR Segmentation'),
                html.Div(id="number-out"),
            ], sm=12, md=6, lg=3),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id, _all_warehouses,
                    'Warehouses',),
                html.Div(id="number-out"),
            ], sm=12, md=6, lg=3),
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
                    dash_utils.get_mini_card(mini_card_products_number_id,title='Number of products',
                                             subtitle=count_products,icon="fas fa-boxes")
                ], sm=12, md=3, lg=3),
                dbc.Col([
                    dash_utils.get_mini_card(mini_card_warehouses_number_id, title='Number of Warehouses ',
                                             subtitle=count_warhouses, icon="fas fa-warehouse"),
                ], sm=12, md=3, lg=3),
                dbc.Col([
                    dash_utils.get_mini_card(mini_card_categories_number_id,title='Number of Categories',subtitle=count_product_categories,icon="fas fa-stream")
                ], sm=12, md=3, lg=3),
                dbc.Col([
                    dash_utils.get_mini_card(mini_card_circuits_number_id,title='Number of Circuit',subtitle=count_circuits,icon="fas fa-code-branch")
                ], sm=12, md=3, lg=3),
            ]),
            
            html.Div(
                [
                    dcc.Loading(
                        html.Div(
                            [
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_warehouse_id)
                                    ], sm=12, md=6, lg=6),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_categories_id)
                                    ], sm=12, md=6, lg=6)
                                ])
                            ],
                            className="pretty_container",
                        ),
                    ),
                ],
                className="shadow-lg p-12 mb-5 bg-white rounded",
            ),
            html.Div(
                [
                    dcc.Loading(
                        html.Div(
                            [
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_abc_id)
                                    ], sm=12, md=6, lg=6),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_fmr_id)
                                    ], sm=12, md=6, lg=6)
                                ])
                            ],
                            className="pretty_container",
                        ),
                    ),
                ],
                className="shadow-lg p-12 mb-5 bg-white rounded",
            ),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        id='forna-body-1',
                        className='shadow-lg p-12 mb-5  rounded',
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
                                                label='Customers',
                                                value='what-is',
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_customer_id)],
                                                        className="",
                                                    )
                                                ),
                                            ),
                                            dcc.Tab(
                                                label='OTIF',
                                                value='Product',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=dcc.Loading(
                                                                html.Div(
                                                                    [dcc.Graph(id=figure_otif_id)],
                                                                    className="",
                                                                )
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ])
                                ],
                            ),
                            dcc.Store(id='forna-custom-colors-1')
                        ]
                    ),
                ], sm=12, md=6, lg=6),

                dbc.Col([
                    html.Div(
                        [
                            html.Div(
                                id='forna-control-tabs-2',
                                className='control-tabs',
                                children=[
                                    dcc.Tabs(
                                        id='forna-tabs-1',
                                        value='what-is',
                                        children=[
                                            dcc.Tab(
                                                label='OrdersDetails by Date',
                                                value='what-is',
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_ordersDetails_id)],
                                                        className="",
                                                    )
                                                ),
                                            ),
                                            dcc.Tab(
                                                label='Orders',
                                                value='Product-at',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=dcc.Loading(
                                                                html.Div(
                                                                    [dcc.Graph(id=figure_orders_id)],
                                                                    className="",
                                                                )
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ])
                                ],
                            ),
                        ],
                        className="shadow-lg p-12 mb-5 bg-white rounded",
                    ),
                ], sm=12, md=6, lg=6),
            ]),


        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    return body_container


def all_body():

    all = html.Div(children=[
        html.Div(className='row',  # Define the row element
                 children=[
                     html.Div(
                         className='pretty_container four columns',
                         children = html.Div(
                            children=filter_container(),
                        )
                     ),
                     # Define the left element
                     html.Div(
                         className='eight columns div-for-charts bg-grey',
                         children = body_container()
                     )
                     # Define the right element
                 ])
    ])

    return all
app.layout = dash_utils.get_dash_layout(filter_container(),body_container())





@app.callback(

    [
        Output(figure_pie_categories_id, "figure"),
        Output(figure_pie_warehouse_id, "figure"),
        Output(figure_pie_abc_id, "figure"),
        Output(figure_pie_fmr_id, "figure"),
    ],
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_warehouse_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
    ]
)
def plot_pie_statuts_product_figure(selected_products, selected_categories, selected_warehouses, selected_abc,
                                    selected_fmr):
    
    stockChecks = StockCheck.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        warehouse__id__in=selected_warehouses,
    )
    
    
    stockChecks = stockChecks.order_by('product__id', 'warehouse__id', '-check_date','product__category').distinct('product__id', 'warehouse__id')
    stockChecks_cat = stockChecks.values('product__category__reference','quantity')
    stockChecks_abc = stockChecks.values('product__abc_segmentation','quantity')
    stockChecks_fmr = stockChecks.values('product__fmr_segmentation','quantity')
    stockChecks_warehouse = stockChecks.values('warehouse','quantity')
    
    df_data_cat = read_frame(stockChecks_cat)
    df_data_abc = read_frame(stockChecks_abc)
    df_data_fmr = read_frame(stockChecks_fmr)
    df_data_whahouse = read_frame(stockChecks_warehouse)
    
    
    
    df_data_cat = df_data_cat.groupby(
        by=['product__category__reference'],
        as_index=False
    ).agg({
        'quantity': 'sum',
    })
    
    df_data_abc = df_data_abc.groupby(
        by=['product__abc_segmentation'],
        as_index=False
    ).agg({
        'quantity': 'sum',
    })
    
    df_data_fmr = df_data_fmr.groupby(
        by=['product__fmr_segmentation'],
        as_index=False
    ).agg({
        'quantity': 'sum',
    })
    
    df_data_whahouse = df_data_whahouse.groupby(
        by=['warehouse'],
        as_index=False
    ).agg({
        'quantity': 'sum',
    })
    
    # stockChecks  = stockChecks.values('product__category').annotate(
    #     sum=Sum('quantity'),
    # ).values('product__category__reference','sum')
    
    # df_data = read_frame(stockChecks)
    
    

    figure_pie_orderDetail = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    figure_pie_fmr = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    figure_pie_warehouse = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    figure_pie_categories =  make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])



    figure_pie_categories.add_trace(
        go.Pie(
            labels=df_data_cat['product__category__reference'],
            values=df_data_cat['quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'rgb(0,255,0)',
                    'rgb(255, 230, 0)',
                    'rgb(255, 132, 0)',
                ]
            },
        )
    , 1, 1)

    figure_pie_orderDetail.add_trace(
        go.Pie(
            labels=df_data_abc['product__abc_segmentation'],
            values=df_data_abc['quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'rgb(0,255,0)',
                    'rgb(255, 230, 0)',
                    'rgb(255, 132, 0)',
                ]
            },
        )
    , 1, 1)
    
    figure_pie_warehouse.add_trace(
        go.Pie(
            labels=df_data_whahouse['warehouse'],
            values=df_data_whahouse['quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'rgb(0,255,0)',
                    'rgb(255, 230, 0)',
                    'rgb(255, 132, 0)',
                ]
            },
        )
    , 1, 1)
    
    figure_pie_fmr.add_trace(
        go.Pie(
            labels=df_data_fmr['product__fmr_segmentation'],
            values=df_data_fmr['quantity'],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'rgb(0,255,0)',
                    'rgb(255, 230, 0)',
                    'rgb(255, 132, 0)',
                ]
            },
        )
    , 1, 1)

    figure_pie_orderDetail.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure_pie_categories.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure_pie_fmr.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure_pie_warehouse.update_traces(hole=.4, hoverinfo="label+percent+name")

    return figure_pie_categories,figure_pie_warehouse,figure_pie_orderDetail,figure_pie_fmr

@app.callback(


    Output(figure_customer_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_warehouse_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
    ]
)
def plot_pie_statutsd_product_figure(selected_products, selected_categories, selected_warehouses, selected_abc,
                                    selected_fmr):
    
    stockChecks = StockCheck.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        warehouse__id__in=selected_warehouses,
    )
    
    stockChecks = stockChecks.order_by('product__id', 'warehouse__id', '-check_date','product__category').distinct('product__id', 'warehouse__id')
    stockChecks_warehouse = stockChecks.values('warehouse','product__category__reference')
    
    df_data_cat = read_frame(stockChecks_warehouse)
    
    print(df_data_cat,'sahara')
    
    df_data_cat = df_data_cat.groupby(
        by=['warehouse','product__category__reference'],
        as_index=False
    ).size().reset_index()
    
    print(df_data_cat,'mpl')
    
    cats = df_data_cat['product__category__reference'].drop_duplicates()
    
                
    for index, row_df in df_data_cat.iterrows():
        
                               
        df_data_cat[row_df['product__category__reference']] = df_data_cat.apply(
        lambda
            row: row['size'] if row.product__category__reference == row_df['product__category__reference'] else 0,
        axis=1)
        
    print('hello',df_data_cat)
    
    figure = df_data_cat.iplot(
        asFigure=True,
        kind='bar',
        barmode='group',
        colors=[
            'rgb(255,0,0)',
            'rgb(255,165,0)',
            'rgb(0, 204, 0)',
            'rgb(0, 48, 240)',
            'rgb(0,255, 0)',
        ],
        x=['warehouse'],
        y=[row_cat for row_cat in cats],
        theme='white',
        title='title',
        xTitle='customer',
        yTitle='Number of Orders',
    )
    
    return figure

@app.callback(


    Output(figure_ordersDetails_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_warehouse_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
    ]
)
def plot_pie_statutsd_product_figure(selected_products, selected_categories, selected_warehouses, selected_abc,
                                    selected_fmr):
    
    stockChecks = StockCheck.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        warehouse__id__in=selected_warehouses,
    )
       
    stockChecks = stockChecks.order_by('product__id', 'warehouse__id', '-check_date','product__abc_segmentation').distinct('product__id', 'warehouse__id')
    
    
    stockChecks_warehouse = stockChecks.values('warehouse','product__abc_segmentation')
    
    df_data_cat = read_frame(stockChecks_warehouse)
    
    print(df_data_cat,'sahara')
    
    
    df_data_cat = df_data_cat.groupby(
        by=['warehouse','product__abc_segmentation'],
        as_index=False
    ).size().reset_index()
    
    print(df_data_cat,'mpl')
    
    cats = df_data_cat['product__abc_segmentation'].drop_duplicates()
    
                
    for index, row_df in df_data_cat.iterrows():
        
                               
        df_data_cat[row_df['product__abc_segmentation']] = df_data_cat.apply(
        lambda
            row: row['size'] if row.product__abc_segmentation == row_df['product__abc_segmentation'] else 0,
        axis=1)
        
    print('hello',df_data_cat)
    
    figure = df_data_cat.iplot(
        asFigure=True,
        kind='bar',
        barmode='group',
        colors=[
            'rgb(255,0,0)',
            'rgb(255,165,0)',
            'rgb(0, 204, 0)',
            'rgb(0, 48, 240)',
            'rgb(0,255, 0)',
        ],
        x=['warehouse'],
        y=[row_cat for row_cat in cats],
        theme='white',
        title='title',
        xTitle='customer',
        yTitle='Number of Orders',
    )
    
    return figure


@app.callback(


    Output(figure_otif_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_warehouse_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
    ]
)
def plot_pie_statutsd_product_ffigure(selected_products, selected_categories, selected_warehouses, selected_abc,
                                    selected_fmr):
    
    stockChecks = StockCheck.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        warehouse__id__in=selected_warehouses,
    )
    
    
    
    
    stockChecks = stockChecks.order_by('product__id', 'warehouse__id', '-check_date','product__fmr_segmentation').distinct('product__id', 'warehouse__id')
    
    

    stockChecks_warehouse = stockChecks.values('warehouse','product__fmr_segmentation')
    
    df_data_cat = read_frame(stockChecks_warehouse)
    
    print(df_data_cat,'sahara')
    
    
    
    df_data_cat = df_data_cat.groupby(
        by=['warehouse','product__fmr_segmentation'],
        as_index=False
    ).size().reset_index()
    
    print(df_data_cat,'mpl')
    
    cats = df_data_cat['product__fmr_segmentation'].drop_duplicates()
    
                
    for index, row_df in df_data_cat.iterrows():
        
                               
        df_data_cat[row_df['product__fmr_segmentation']] = df_data_cat.apply(
        lambda
            row: row['size'] if row.product__fmr_segmentation == row_df['product__fmr_segmentation'] else 0,
        axis=1)
        
    print('hello',df_data_cat)
    
    figure = df_data_cat.iplot(
        asFigure=True,
        kind='bar',
        barmode='group',
        colors=[
            'rgb(255,0,0)',
            'rgb(255,165,0)',
            'rgb(0, 204, 0)',
            'rgb(0, 48, 240)',
            'rgb(0,255, 0)',
        ],
        x=['warehouse'],
        y=[row_cat for row_cat in cats],
        theme='white',
        title='title',
        xTitle='customer',
        yTitle='Number of Orders',
    )
    
    return figure

    
    

dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_fmr_list_id, div_fmr_list_id, checkbox_fmr_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_abc_list_id, div_abc_list_id, checkbox_abc_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id)
