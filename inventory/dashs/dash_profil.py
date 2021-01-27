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
from django.db.models import F, ExpressionWrapper, DateTimeField,IntegerField,Case, CharField, Value, When,Sum,Max,Count

from multiprocessing import  Pool
import multiprocessing as mp

from django.db import connection
import pandas as pd
import resource


import colorlover, plotly

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('profil', add_bootstrap_links=True)
_prefix = 'profil'

map_warehouse_location_id = _prefix + '-warehosue-location'
map_view_selector_id = _prefix + '-map-view-selector'

import time

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
df = pd.read_csv(
    "https://github.com/plotly/datasets/raw/master/dash-sample-apps/dash-oil-and-gas/data/wellspublic.csv",
    low_memory=False,
)

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# TODO Avoid to repet query sets  in all callbacks


# ------------------------------------------{Id Graph}--------------------------------------------------------

figure_customer_id = dash_utils.generate_html_id(_prefix, 'figure_customer_id')
figure_abc_id = dash_utils.generate_html_id(_prefix, 'figure_orderDetails_id')
figure_fmr_id = dash_utils.generate_html_id(_prefix, 'figure_fmr_id')
figure_most_ordred_product_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_product_id')
figure_most_ordred_customer_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_customer_id')
figure_pie_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_categories_id')
figure_pie_abc_id = dash_utils.generate_html_id(_prefix, 'figure_pie_abc_id')
figure_pie_warehouse_id = dash_utils.generate_html_id(_prefix, 'figure_pie_warehouse_id')
figure_pie_fmr_id = dash_utils.generate_html_id(_prefix, 'figure_pie_fmr_id')
figure_most_ordred_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_ordred_categories_id')
figure_orders_id = dash_utils.generate_html_id(_prefix, 'figure_orders_id')
figure_abc_by_date_id = dash_utils.generate_html_id(_prefix, 'figure_abc_by_date_id')
figure_fmr_by_date_id = dash_utils.generate_html_id(_prefix, 'figure_fmr_by_date_id')
figure_categorie_by_date_id = dash_utils.generate_html_id(_prefix, 'figure_categorie_by_date_id')

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
                    dash_utils.get_mini_card_profil(mini_card_products_number_id,title='Number of products',
                                             subtitle=count_products,icon="fas fa-boxes")
                ], sm=12, md=3, lg=3),
                dbc.Col([
                    dash_utils.get_mini_card_profil(mini_card_warehouses_number_id, title='Number of Warehouses ',
                                             subtitle=count_warhouses, icon="fas fa-warehouse"),
                ], sm=12, md=3, lg=3),
                dbc.Col([
                    dash_utils.get_mini_card_profil(mini_card_categories_number_id,title='Number of Categories',subtitle=count_product_categories,icon="fas fa-stream")
                ], sm=12, md=3, lg=3),
                dbc.Col([
                    dash_utils.get_mini_card_profil(mini_card_circuits_number_id,title='Number of Circuit',subtitle=count_circuits,icon="fas fa-code-branch")
                ], sm=12, md=3, lg=3),
            ]),
                
            html.Div(
                [
                    dcc.Loading(
                        html.Div(
                            [
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_warehouse_id),
                                        html.P(_('Distribution of Product in Warehouses'),className='font-weight-bold text-primary  h6  text-center'),
                                    ], sm=12, md=6, lg=6),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_categories_id),
                                        html.P(_('Distribution of Product By Categories'),className='font-weight-bold text-primary  h6  text-center'),
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
                                        dcc.Graph(id=figure_pie_abc_id),
                                        html.P(_('Distribution of Product By ABC classification'),className='font-weight-bold text-primary  h6  text-center'),
                                    ], sm=12, md=6, lg=6),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_fmr_id),
                                        html.P(_('Distribution of Product By FMR classification'),className='font-weight-bold text-primary  h6  text-center'),
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
                    dash_utils.get_chart_card(map_warehouse_location_id)
                ]),
            ]),
            
            dbc.Row([

                dbc.Col([
                    html.Div(
                        [
                            html.Div(
                                className='control-tabs',
                                children=[
                                    dcc.Tabs(
                                        value='what-is',
                                        children=[
                                            dcc.Tab(
                                                label=_('Evolution of Categories'),
                                                value='what-is',
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_categorie_by_date_id)],
                                                        className="",
                                                    )
                                                ),
                                            ),
                                            dcc.Tab(
                                                label=_('Evolution of ABC Classification'),
                                                value='abc_by_date',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=dcc.Loading(
                                                                html.Div(
                                                                    [dcc.Graph(id=figure_abc_by_date_id)],
                                                                    className="",
                                                                )
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                            dcc.Tab(
                                                label=_('Evolution of FMR Classification '),
                                                value='fmr_by_date',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=dcc.Loading(
                                                                html.Div(
                                                                    [dcc.Graph(id=figure_fmr_by_date_id)],
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
                ], sm=12, md=12, lg=12),
            ]),
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
                                                label=_('TOP 10 Product'),
                                                value='what-is',
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_orders_id)],
                                                        className="",
                                                    )
                                                ),
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
                                className='control-tabs',
                                children=[
                                    dcc.Tabs(
                                        value='what-is',
                                        children=[
                                            dcc.Tab(
                                                label=_('Distribution of Categories by Warehouses'),
                                                value='what-is',
                                                children=dcc.Loading(
                                                    html.Div(
                                                        [dcc.Graph(id=figure_customer_id)],
                                                        className="",
                                                    )
                                                ),
                                            ),
                                            dcc.Tab(
                                                label=_('Distribution of ABC Classification in Warehouses'),
                                                value='Product-at',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=dcc.Loading(
                                                                html.Div(
                                                                    [dcc.Graph(id=figure_abc_id)],
                                                                    className="",
                                                                )
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                            dcc.Tab(
                                                label=_('Distribution of FMR Classification in Warehouses'),
                                                value='Product',
                                                children=html.Div(
                                                    className='control-tab',
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children=dcc.Loading(
                                                                html.Div(
                                                                    [dcc.Graph(id=figure_fmr_id)],
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


    Output(figure_abc_id, "figure"),
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


    Output(figure_fmr_id, "figure"),
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



@app.callback(


    Output(figure_orders_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_warehouse_list_id, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
    ]
)
def plot_most_product_figure(selected_products, selected_categories, selected_warehouses, selected_abc,
                                    selected_fmr):
    
    stockChecks = StockCheck.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        warehouse__id__in=selected_warehouses,
    )
      
    stockChecks = stockChecks.order_by('product__id', 'warehouse__id', '-check_date').distinct('product__id', 'warehouse__id')
    
    results = stockChecks.values('product','quantity')
    
    df_data_cat = read_frame(results)
    
    
    df_data_cat = df_data_cat.groupby(
        by=['product'],
        as_index=False
    ).agg({
        'quantity': 'sum',
    })
    
    df_data_cat = df_data_cat.sort_values(by='quantity',ascending = True).head(10)


    print(df_data_cat,'momo')


    figure = df_data_cat.iplot(
        asFigure=True,
        kind='barh',
        barmode='stack',
        x=['product'],
        y=['quantity'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Most Ordered  Products',
    )  
    
    
    return figure



@app.callback(


    Output(figure_categorie_by_date_id, "figure"),
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
    
    stockChecks  = stockChecks.values('check_date','product__category__reference').annotate(
        quantity=Sum('quantity'),
    ).values('product__category__reference','check_date','quantity')
    
    
    df_data_cat = read_frame(stockChecks)

    

    
    cats = df_data_cat['product__category__reference'].drop_duplicates()
    
                
    for index, row_df in df_data_cat.iterrows():

                               
        df_data_cat[row_df['product__category__reference']] = df_data_cat.apply(
        lambda
            row: row['quantity'] if row.product__category__reference == row_df['product__category__reference'] else 0,
        axis=1)
      
    dict_agg = {'quantity':'sum'}
    
    print(df_data_cat,'technique')
    
    for row_cat in cats:
        dict_agg[row_cat] = 'sum'
        
    df_data_cat = df_data_cat.groupby(
        by=['check_date'],
        as_index=False
    ).agg(dict_agg)
      
    print('tafiflate',df_data_cat)
    

    
    figure = df_data_cat.iplot(
        asFigure=True,
        colors=[
            'rgb(255,0,0)',
            'rgb(255,165,0)',
            'rgb(0, 204, 0)',
            'rgb(0, 48, 240)',
            'rgb(0,255, 0)',
        ],
        x=['check_date'],
        y=['quantity'].append([row_cat for row_cat in cats]),
        theme='white',
        title='title',
        xTitle='customer',
        mode='markers',
        name="Oil Produced (bbl)",
        yTitle='Number of Orders',
    )
    
    figure.update_traces(
        type="scatter",
        mode="lines+markers",
        line=dict(shape="spline", smoothing=1.3),
        marker=dict(
            symbol="diamond-open",
            size=7,
        ),
    )

    
    return figure


@app.callback(


    Output(figure_abc_by_date_id, "figure"),
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
    
    stockChecks  = stockChecks.values('check_date','product__abc_segmentation').annotate(
        quantity=Sum('quantity'),
    ).values('product__abc_segmentation','check_date','quantity')
    
    
    df_data_cat = read_frame(stockChecks)

    

    
    cats = df_data_cat['product__abc_segmentation'].drop_duplicates()
    
                
    for index, row_df in df_data_cat.iterrows():

                               
        df_data_cat[row_df['product__abc_segmentation']] = df_data_cat.apply(
        lambda
            row: row['quantity'] if row.product__abc_segmentation == row_df['product__abc_segmentation'] else 0,
        axis=1)
      
    dict_agg = {'quantity':'sum'}
    
    print(df_data_cat,'technique')
    
    for row_cat in cats:
        dict_agg[row_cat] = 'sum'
        
    df_data_cat = df_data_cat.groupby(
        by=['check_date'],
        as_index=False
    ).agg(dict_agg)
      
    print('tafiflate',df_data_cat)
    

    
    figure = df_data_cat.iplot(
        asFigure=True,
        colors=[
            'rgb(255,0,0)',
            'rgb(255,165,0)',
            'rgb(0, 204, 0)',
            'rgb(0, 48, 240)',
            'rgb(0,255, 0)',
        ],
        x=['check_date'],
        y=['quantity'].append([row_cat for row_cat in cats]),
        theme='white',
        title='title',
        xTitle='customer',
        mode='markers',
        name="Oil Produced (bbl)",
        yTitle='Number of Orders',
    )
    
    figure.update_traces(
        type="scatter",
        mode="lines+markers",
        line=dict(shape="spline", smoothing=1.3),
        marker=dict(
            symbol="diamond-open",
            size=7,
        ),
    )

    
    return figure



@app.callback(


    Output(figure_fmr_by_date_id, "figure"),
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
    
    stockChecks  = stockChecks.values('check_date','product__fmr_segmentation').annotate(
        quantity=Sum('quantity'),
    ).values('product__fmr_segmentation','check_date','quantity')
    
    
    df_data_cat = read_frame(stockChecks)

    

    
    cats = df_data_cat['product__fmr_segmentation'].drop_duplicates()
    
                
    for index, row_df in df_data_cat.iterrows():

                               
        df_data_cat[row_df['product__fmr_segmentation']] = df_data_cat.apply(
        lambda
            row: row['quantity'] if row.product__fmr_segmentation == row_df['product__fmr_segmentation'] else 0,
        axis=1)
      
    dict_agg = {'quantity':'sum'}
    
    print(df_data_cat,'technique')
    
    for row_cat in cats:
        dict_agg[row_cat] = 'sum'
        
    df_data_cat = df_data_cat.groupby(
        by=['check_date'],
        as_index=False
    ).agg(dict_agg)
      
    print('tafiflate',df_data_cat)
    

    
    figure = df_data_cat.iplot(
        asFigure=True,
        colors=[
            'rgb(255,0,0)',
            'rgb(255,165,0)',
            'rgb(0, 204, 0)',
            'rgb(0, 48, 240)',
            'rgb(0,255, 0)',
        ],
        x=['check_date'],
        y=['quantity'].append([row_cat for row_cat in cats]),
        theme='white',
        title='title',
        xTitle='customer',
        mode='markers',
        name="Oil Produced (bbl)",
        yTitle='Number of Orders',
    )
    
    figure.update_traces(
        type="scatter",
        mode="lines+markers",
        line=dict(shape="spline", smoothing=1.3),
        marker=dict(
            symbol="diamond-open",
            size=7,
        ),
    )

    
    return figure



@app.callback(
    Output(map_warehouse_location_id, "figure"),
    [
        Input(dropdown_warehouse_list_id, 'value')
    ]
)
def update_well_map(selected_warehouses):
    _mapbox_access_token = 'pk.eyJ1IjoiYWJvMDA3IiwiYSI6ImNrOHNvb3pzdDAxbDQzbGxrNzdhdjVoaWIifQ.PzIABS28MHy7mn6pnq5zhg'
    _init_lat = 32
    _init_lon = -6
    layout = go.Layout(
        # clickmode="event+select",
        # dragmode="lasso",
        # showlegend=True,
        # autosize=True,
        # hovermode="closest",
        margin=dict(l=0, r=0, t=0, b=0),

        mapbox=dict(
            accesstoken=_mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(lat=_init_lat, lon=_init_lon),
            pitch=0,
            zoom=5,
            # style="stamen-terrain",
            style="mapbox://styles/abo007/ck90kt9zd0bk31ioa7g1v5z4v",
            # layers =  [{
            #             'source': {
            #                 'type': "FeatureCollection",
            #                 'features': [{
            #                     'type': "Feature",
            #                     'geometry': {
            #                         'type': "MultiPolygon",
            #                         'coordinates': [[[
            #                             [-73.606352888, 45.507489991], [-73.606133883, 45.50687600],
            #                             [-73.605905904, 45.506773980], [-73.603533905, 45.505698946],
            #                             [-73.602475870, 45.506856969], [-73.600031904, 45.505696003],
            #                             [-73.599379992, 45.505389066], [-73.599119902, 45.505632008],
            #                             [-73.598896977, 45.505514039], [-73.598783894, 45.505617001],
            #                             [-73.591308727, 45.516246185], [-73.591380782, 45.516280145],
            #                             [-73.596778656, 45.518690062], [-73.602796770, 45.521348046],
            #                             [-73.612239983, 45.525564037], [-73.612422919, 45.525642061],
            #                             [-73.617229085, 45.527751983], [-73.617279234, 45.527774160],
            #                             [-73.617304713, 45.527741334], [-73.617492052, 45.527498362],
            #                             [-73.617533258, 45.527512253], [-73.618074188, 45.526759105],
            #                             [-73.618271651, 45.526500673], [-73.618446320, 45.526287943],
            #                             [-73.618968507, 45.525698560], [-73.619388002, 45.525216750],
            #                             [-73.619532966, 45.525064183], [-73.619686662, 45.524889290],
            #                             [-73.619787038, 45.524770086], [-73.619925742, 45.524584939],
            #                             [-73.619954486, 45.524557690], [-73.620122362, 45.524377961],
            #                             [-73.620201713, 45.524298907], [-73.620775593, 45.523650879]
            #                         ]]]
            #                     }
            #                 }]
            #             },
            #             'type': "fill", 'below': "traces", 'color': "royalblue"}],
            # layers=[dict(
            #     below='traces',
            #     sourcetype="raster",
            #     source=[
            #         "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            #     ]

            # )]

        ),
    )
    
    # queryset
    qs = Warehouse.objects.filter(id__in=selected_warehouses).annotate(available_products=Count(F('stock__product')))
    lat = list(qs.values_list('lat', flat=True))
    lon = list(qs.values_list('lon', flat=True))
    address = list(qs.values_list('address', flat=True))
    name = list(qs.values_list('name', flat=True))
    
    
        
    available_products = list(qs.values_list('available_products', flat=True))
    
    lat_str = [str(num) for num in lat]
    
    lon_str = [str(num) for num in lon]

    text_list = list(
        map(
            lambda prd, add, name: '<b>Reference:</b> ' + 'name' +
            '<br><b>Available products:</b> ' + str('prd') +
            '<br><b>Address:</b> ' + 'add',
            'available_products',
            'address',
            'name',
            
            # "Well ID:" + str(int(item)),
            # dff[dff["fm_name"] == formation]["RecordNumber"],
        )
    )
    chart_data = []
    # for data in qs:
    new_chart_data = go.Scattermapbox(
        mode="markers",
        lat=lat_str,
        lon=lon_str,
        name='warehouses',
        text=text_list,
        marker={"size": 12, 'color':'red'},
        textposition="bottom right"

        # marker={'size': 20, 'symbol': ["bus", "harbor", "airport"]},
        # text=["Bus", "Harbor", "airport"],
    )

    chart_data.append(new_chart_data)
    return {"data": chart_data, "layout": layout}
  



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
