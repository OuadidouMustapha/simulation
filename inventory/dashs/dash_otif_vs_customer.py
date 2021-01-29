# Import required libraries
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from common.dashboards import dash_utils
from dash.dependencies import Input, Output
from django.utils.translation import gettext as _
from django_plotly_dash import DjangoDash
from stock.models import Product, ProductCategory, Customer, OrderDetail
from django_pandas.io import read_frame
import cufflinks as cf

import numpy as np
from plotly.subplots import make_subplots
from django.db.models import F, ExpressionWrapper, DateTimeField,IntegerField,Case, CharField, Value, When,Sum

from multiprocessing import  Pool
import multiprocessing as mp

from django.db import connection
import pandas as pd
import resource


import colorlover, plotly

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('otif', add_bootstrap_links=True)
_prefix = 'otif'

import time



# TODO Avoid to repet query sets  in all callbacks


# ------------------------------------------{Id Graph}--------------------------------------------------------

figure_customer_id = dash_utils.generate_html_id(_prefix, 'figure_customer_id')
figure_ordersDetails_id = dash_utils.generate_html_id(_prefix, 'figure_orderDetails_id')
figure_otif_id = dash_utils.generate_html_id(_prefix, 'figure_otif_id')
figure_most_ordred_product_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_product_id')
figure_most_ordred_customer_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_customer_id')
figure_pie_orderDetail_id = dash_utils.generate_html_id(_prefix, 'figure_pie_orderDetail_id')
figure_pie_order_id = dash_utils.generate_html_id(_prefix, 'figure_pie_order_id')
figure_most_ordred_categories_id = dash_utils.generate_html_id(_prefix, 'figure_pie_ordred_categories_id')
figure_orders_id = dash_utils.generate_html_id(_prefix, 'figure_orders_id')

# ------------------------------------------------------------------------------------------------------------

details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')

# -------------------------------------------- Dropdown  list -------------------------------------------------

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


# ------------------------------------------------Mini Cards ------------------------------
mini_card_subtitle_bias_percent_id = dash_utils.generate_html_id(_prefix, 'mini_card_subtitle_bias_percent_id')

mini_card_subtitle_mad_id = dash_utils.generate_html_id(_prefix, 'mini_card_subtitle_mad_id')

mini_card_subtitle_mape_id = dash_utils.generate_html_id(_prefix, 'mini_card_subtitle_mape_id' )


# -----------------------------------------------------------------------------------------

input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

_all_products   = list(Product.objects.get_all_products())
_all_categories = list(ProductCategory.objects.get_all_productcategory())
_all_customers  = list(Customer.objects.get_all_customers())
_all_status     = list(Product.objects.get_all_status_of_products())


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
                    dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id, _all_customers,
                    'Customers',select_all=False,multi=False),
                html.Div(id="number-out"),
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
                    dash_utils.get_mini_card(mini_card_subtitle_bias_percent_id,title='OTIF Global',
                                             subtitle='')
                ], sm=12, md=4, lg=4),
                dbc.Col([
                    dash_utils.get_mini_card(mini_card_subtitle_mad_id, title='Number of Orders ',
                                             subtitle='', icon='fas fa-clipboard-list'),
                ], sm=12, md=4, lg=4),
                dbc.Col([
                    dash_utils.get_mini_card(mini_card_subtitle_mape_id,title='Number of Deliveries',subtitle='',icon='fas fa-dolly')
                ], sm=12, md=4, lg=4),
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


            html.Div(
                [
                    dcc.Loading(
                        html.Div(
                            [
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_orderDetail_id)
                                    ], sm=12, md=6, lg=6),
                                    dbc.Col([
                                        dcc.Graph(id=figure_pie_order_id)
                                    ], sm=12, md=6, lg=6)
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

    Output(figure_customer_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_OrderDetail_count_by_custmoer_figure(selected_products, selected_categories, selected_customers,
                                              selected_status, start_date,
                                              end_date):

    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        #product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=[selected_customers],
        order__ordered_at__lte=end_date
    )
    #
    # df = read_frame(results)

    # train = parallelize_dataframe(results, read_frame)

    results  = results.annotate(
        Not_Delivered =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity=0,then=1),
                When(order__delivery__deliverydetail__delivered_quantity=None, then=1),
                When(order__delivery__delivered_at=None, then=1),
                default=None,
                output_field=IntegerField()
            ),
        Partially_Delivered_In_Time =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'), desired_at__gte= F('order__delivery__delivered_at'),then=1),
                default=None,
                output_field=IntegerField()
            ),
        Partially_Delivered_Not_In_Time=
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),
                     order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'),
                     desired_at__lt=F('order__delivery__delivered_at'), then=1),
                default=None,
                output_field=IntegerField()
            ),
        Delivered_In_Time=
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                     desired_at__lte=F('order__delivery__delivered_at'), then=1),
                default=None,
                output_field=IntegerField()
            ),
        Delivered_Not_In_Time =
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                    desired_at__gte=F('order__delivery__delivered_at'), then=1),
                default=None,
                output_field=IntegerField()
            )
    )
    results  = results.values('customer_id','customer__reference').annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time =Sum('Delivered_In_Time'),
        Delivered_Not_In_Time =Sum('Delivered_Not_In_Time'),
    ).values('customer','customer__reference', 'Not_Delivered','Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time','Delivered_In_Time','Delivered_Not_In_Time')


    df = pd.DataFrame.from_records(results)

    print(df)
    # x = list(orderDetails.values_list('order_id', flat=True))
    # y = list(orderDetails.values_list('Partially_Delivered_In_Time', flat=True))
    #
    # figure = go.Figure(data=[
    #     dict(x=x, y=y, type='bar')
    # ])



    #
    #
    # new = df.groupby(
    #     by=['product_id', 'customer_id', 'order__id'],
    #     as_index=False
    # ).agg({
    #     'order__delivery__deliverydetail__delivered_quantity': 'sum',
    #     'order__delivery__delivered_at': 'max',
    #     'desired_at': 'first',
    #     'ordered_quantity': 'first',
    # })
    #
    # # TODO Rename Data Frames
    #
    # new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
    #     'datetime64[ns]')
    #
    # new['desired_at'] = new['desired_at'].astype(
    #     'datetime64[ns]')
    #
    # new_df = new.rename(
    #     columns={
    #         "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
    #         "order__delivery__delivered_at": "delivered_at",
    #     },
    #     errors="raise"
    # )
    #
    # if new_df.size != 0:
    #
    #     new_df['Not Delivered'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
    #         axis=1)
    #     new_df['Partially Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #
    #     new_df['Partially Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     df_data = new_df.groupby(['customer_id']).agg({
    #         'Not Delivered': 'sum',
    #         'Partially Delivered In Time': 'sum',
    #         'Partially Delivered Not In Time': 'sum',
    #         'Delivered In Time': 'sum',
    #         'Delivered Not In Time': 'sum',
    #     }).reset_index()
    #

    figure = df.iplot(
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
        x=['customer'],
        y=['Not_Delivered', 'Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time', 'Delivered_In_Time', 'Delivered_Not_In_Time'],
        theme='white',
        title='title',
        xTitle='customer',
        yTitle='Number of Orders',
    )
    # else:
    # figure = df.iplot(
    #     asFigure=True,
    #     kind='bar',
    #     barmode='group',
    #     x=['customer_id'],
    #     y=None,
    #     theme='white',
    #     title='title',
    #     xTitle='customer',
    #     yTitle='Number of Orders',
    # )

    return figure

#
@app.callback(
    [
        Output(figure_otif_id, "figure"),
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
def plot_order_count_figure(selected_products, selected_categories, selected_customers, selected_status, start_date,end_date):



    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        #product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=[selected_customers],
        order__ordered_at__lte=end_date
    )
    #
    # df = read_frame(results)

    # train = parallelize_dataframe(results, read_frame)

    results  = results.annotate(
        Not_Delivered =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity=0,then=1),
                When(order__delivery__deliverydetail__delivered_quantity=None, then=1),
                When(order__delivery__delivered_at=None, then=1),
                default=0,
                output_field=IntegerField()
            ),
        Partially_Delivered_In_Time =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'), desired_at__gte= F('order__delivery__delivered_at'),then=1),
                default=0,
                output_field=IntegerField()
            ),
        Partially_Delivered_Not_In_Time=
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),
                     order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'),
                     desired_at__lt=F('order__delivery__delivered_at'), then=1),
                default=0,
                output_field=IntegerField()
            ),
        Delivered_In_Time=
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                     desired_at__lte=F('order__delivery__delivered_at'), then=1),
                default=0,
                output_field=IntegerField()
            ),
        Delivered_Not_In_Time =
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                    desired_at__gte=F('order__delivery__delivered_at'), then=1),
                default=0,
                output_field=IntegerField()
            )
    )

    results  = results.values('order__ordered_at',).annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time =Sum('Delivered_In_Time'),
        Delivered_Not_In_Time =Sum('Delivered_Not_In_Time'),
    ).values('order__ordered_at','Not_Delivered','Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time','Delivered_In_Time','Delivered_Not_In_Time')

    df_data = read_frame(results)


    def otif(row):
        sum = row['Not_Delivered'] + row['Partially_Delivered_In_Time'] + row['Partially_Delivered_Not_In_Time'] + row['Delivered_In_Time'] + row['Delivered_Not_In_Time']
        if sum != 0:
            return (row['Delivered_In_Time'] / sum) * 100
        else:
            return 0

    df_data['OTIF'] = df_data.apply(
        lambda row: otif(row),
        axis=1)
    
    
    print(df_data,'deserto')

    figure = df_data.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['order__ordered_at'],
        y=[
            'OTIF'
        ],
        theme='white',
        title='title',
        xTitle='Ordered Date',
        yTitle='Number of Orders',
    )



    # ----------------------------------------------------{}-----------------------------------------------------------------------

    # results = OrderDetail.objects.filter(
    #     product__in=selected_products,
    #     # product__category__in=selected_categories,
    #     # product__status__in=selected_status,
    #     order__ordered_at__gte=start_date,
    #     customer__in=[selected_customers],
    #     order__ordered_at__lte=end_date
    # )
    #
    # orderDetails = results.values(
    #     'id',
    #     'order__id',
    #     'product_id',
    #     'customer_id',
    #     'order__delivery__id',
    #     'order__ordered_at',
    #     'ordered_quantity',
    #     'desired_at',
    #     'order__delivery__delivered_at',
    #     'order__delivery__deliverydetail__delivered_quantity'
    # )
    #
    # df = read_frame(orderDetails)
    #
    # new = df.groupby(
    #     by=['product_id', 'customer_id', 'order__id'],
    #     as_index=False
    # ).agg({
    #     'order__delivery__deliverydetail__delivered_quantity': 'sum',
    #     'order__delivery__delivered_at': 'max',
    #     'desired_at': 'first',
    #     'ordered_quantity': 'first',
    # })
    #
    # # TODO Rename Data Frames
    #
    # new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
    #     'datetime64[ns]')
    #
    # new['desired_at'] = new['desired_at'].astype(
    #     'datetime64[ns]')
    #
    # new_df = new.rename(
    #     columns={
    #         "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
    #         "order__delivery__delivered_at": "delivered_at",
    #     },
    #     errors="raise"
    # )
    #
    # if new_df.size != 0:
    #
    #     new_df['Not Delivered'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
    #         axis=1)
    #     new_df['Partially Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #
    #     new_df['Partially Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     df_data = new_df.groupby(['customer_id']).agg({
    #         'Not Delivered': 'sum',
    #         'Partially Delivered In Time': 'sum',
    #         'Partially Delivered Not In Time': 'sum',
    #         'Delivered In Time': 'sum',
    #         'Delivered Not In Time': 'sum',
    #     }).reset_index()
    #
    #     def otif(row):
    #         sum = row['Not Delivered'] + row['Partially Delivered In Time']+ row['Partially Delivered Not In Time'] + row['Delivered In Time'] + row['Delivered Not In Time']
    #         if sum != 0:
    #             return (row['Delivered In Time'] / sum) * 100
    #         else:
    #             return 0
    #
    #     df_data['OTIF'] = df_data.apply(
    #         lambda row: otif(row),
    #         axis=1)
    #
    #     frame = df_data.sort_values(by=['OTIF'], ascending=False)
    #
    #     figure = frame.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='group',
    #         x=['customer_id'],
    #         y=['OTIF'],
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='OTIF',
    #     )
    # else:
    #     figure = new_df.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='group',
    #         x=['customer_id'],
    #         y=None,
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='Number of Orders',
    #     )

    return figure
#
#
@app.callback(

    Output(figure_ordersDetails_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_customers, selected_status, start_date,
                            end_date):


    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        #product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=[selected_customers],
        order__ordered_at__lte=end_date
    )
    #
    # df = read_frame(results)

    # train = parallelize_dataframe(results, read_frame)

    results  = results.annotate(
        Not_Delivered =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity=0,then=1),
                When(order__delivery__deliverydetail__delivered_quantity=None, then=1),
                When(order__delivery__delivered_at=None, then=1),
                default=None,
                output_field=IntegerField()
            ),
        Partially_Delivered_In_Time =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'), desired_at__gte= F('order__delivery__delivered_at'),then=1),
                default=None,
                output_field=IntegerField()
            ),
        Partially_Delivered_Not_In_Time=
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),
                     order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'),
                     desired_at__lt=F('order__delivery__delivered_at'), then=1),
                default=None,
                output_field=IntegerField()
            ),
        Delivered_In_Time=
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                     desired_at__lte=F('order__delivery__delivered_at'), then=1),
                default=None,
                output_field=IntegerField()
            ),
        Delivered_Not_In_Time =
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                    desired_at__gte=F('order__delivery__delivered_at'), then=1),
                default=None,
                output_field=IntegerField()
            )
    )
    results  = results.values('order__ordered_at').annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time =Sum('Delivered_In_Time'),
        Delivered_Not_In_Time =Sum('Delivered_Not_In_Time'),
    ).values('order__ordered_at','Not_Delivered','Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time','Delivered_In_Time','Delivered_Not_In_Time')


    df = pd.DataFrame.from_records(results)


    figure = df.iplot(
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
        x=['order__ordered_at'],
        y=['Not_Delivered', 'Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time', 'Delivered_In_Time', 'Delivered_Not_In_Time'],
        theme='white',
        title='title',
        xTitle='date ',
        yTitle='Number of Orders',
    )


    # ///////////////////////////////////////////////////////////////////////////////////////{ With Data Frames }////////////////////////////////////////////////////////////////////////////////
    # results = OrderDetail.objects.filter(
    #     product__in=selected_products,
    #     # product__category__in=selected_categories,
    #     # product__status__in=selected_status,
    #     order__ordered_at__gte=start_date,
    #     customer__in=[selected_customers],
    #     order__ordered_at__lte=end_date
    # )
    #
    # orderDetails = results.values(
    #     'id',
    #     'order__id',
    #     'product_id',
    #     'customer_id',
    #     'order__delivery__id',
    #     'order__ordered_at',
    #     'ordered_quantity',
    #     'desired_at',
    #     'order__delivery__delivered_at',
    #     'order__delivery__deliverydetail__delivered_quantity'
    # )
    #
    # new = read_frame(orderDetails)
    #
    # # new = df.groupby(
    # #     by=['product_id', 'customer_id', 'order__id'],
    # #     as_index=False
    # # ).agg({
    # #     'order__delivery__deliverydetail__delivered_quantity': 'sum',
    # #     'order__delivery__delivered_at': 'max',
    # #     'desired_at': 'first',
    # #     'order__ordered_at': 'first',
    # #     'ordered_quantity': 'first',
    # # })
    #
    # # TODO Rename Data Frames
    #
    # new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
    #     'datetime64[ns]')
    #
    # new['desired_at'] = new['desired_at'].astype(
    #     'datetime64[ns]')
    #
    # new_df = new.rename(
    #     columns={
    #         "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
    #         "order__delivery__delivered_at": "delivered_at",
    #         'order__ordered_at': 'ordered_at',
    #     },
    #     errors="raise"
    # )
    #
    # if new_df.size != 0:
    #
    #     new_df['Not Delivered'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
    #         axis=1)
    #     new_df['Partially Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #
    #     new_df['Partially Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     df_data = new_df.groupby(['ordered_at']).agg({
    #         'Not Delivered': 'sum',
    #         'Partially Delivered In Time': 'sum',
    #         'Partially Delivered Not In Time':'sum',
    #         'Delivered In Time': 'sum',
    #         'Delivered Not In Time': 'sum',
    #     }).reset_index()
    #
    #     figure = df_data.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='stack',
    #         colors=[
    #             'rgb(255,0,0)',
    #             'rgb(255,165,0)',
    #             'rgb(0, 204, 0)',
    #             'rgb(0, 48, 240)',
    #             'rgb(0,255, 0)',
    #         ],
    #         x='ordered_at',
    #         y=['Not Delivered', 'Partially Delivered In Time','Partially Delivered Not In Time', 'Delivered In Time', 'Delivered Not In Time'],
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='Number of Orders',
    #     )
    # else:
    #
    #     figure = new_df.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='group',
    #         x=['customer_id'],
    #         y=None,
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='Number of Orders',
    #     )

    return figure
#
#
@app.callback(

    Output(figure_orders_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_customers, selected_status, start_date,
                            end_date):


    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        #product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=[selected_customers],
        order__ordered_at__lte=end_date
    )
    #
    # df = read_frame(results)

    # train = parallelize_dataframe(results, read_frame)

    results  = results.annotate(
        Not_Delivered =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity=0,then=1),
                When(order__delivery__deliverydetail__delivered_quantity=None, then=1),
                When(order__delivery__delivered_at=None, then=1),
                default=0,
                output_field=IntegerField()
            ),
        Partially_Delivered_In_Time =
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'), desired_at__gte= F('order__delivery__delivered_at'),then=1),
                default=0,
                output_field=IntegerField()
            ),
        Partially_Delivered_Not_In_Time=
            Case(
                When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),
                     order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'),
                     desired_at__lt=F('order__delivery__delivered_at'), then=1),
                default=0,
                output_field=IntegerField()
            ),
        Delivered_In_Time=
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                     desired_at__lte=F('order__delivery__delivered_at'), then=1),
                default=0,
                output_field=IntegerField()
            ),
        Delivered_Not_In_Time =
            Case(
                When(
                    order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                    desired_at__gte=F('order__delivery__delivered_at'), then=1),
                default=0,
                output_field=IntegerField()
            )
    )

    results  = results.values('order__ordered_at','order').annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time =Sum('Delivered_In_Time'),
        Delivered_Not_In_Time =Sum('Delivered_Not_In_Time'),
    ).values('order__ordered_at','order','Not_Delivered','Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time','Delivered_In_Time','Delivered_Not_In_Time')

    df_data = read_frame(results)

    print(results,"hello mustapha")



    df_data['sum_all'] = df_data.apply(
        lambda
            row: row['Not_Delivered'] + row['Partially_Delivered_In_Time'] + row[
            'Partially_Delivered_Not_In_Time'] + row['Delivered_In_Time'] + row['Delivered_Not_In_Time'],
        axis=1)

    df_data['Order Not_Delivered'] = df_data.apply(
        lambda
            row: 1 if row['Not_Delivered'] == row['sum_all'] and row['Not_Delivered'] != 0 else None,
        axis=1
    )

    df_data['Order Partially_Delivered_In_Time'] = df_data.apply(
        lambda row: 1 if (
                row['Partially_Delivered_Not_In_Time'] == 0
                and row['Delivered_Not_In_Time'] == 0
                and row['Not_Delivered'] < row['sum_all']
                and (
                        row['Delivered_In_Time'] < row['sum_all']
                        or row['Partially_Delivered_In_Time'] != 0
                )
                and row['Delivered_In_Time'] <= row['sum_all']
                and row['sum_all'] != 0
        ) else 0, axis=1)

    df_data['Order Partially_Delivered_Not_In_Time'] = df_data.apply(
        lambda row: 1 if (row['Partially_Delivered_Not_In_Time'] != 0 or (
                row['Delivered_Not_In_Time'] < row['sum_all'] and row['Delivered_Not_In_Time'] != 0)) and row[
                             'sum_all'] != 0 else 0, axis=1)

    df_data['Order Delivered_In_Time'] = df_data.apply(
        lambda
            row: 1 if row['Delivered_In_Time'] == row['sum_all'] and row['Delivered_In_Time'] != 0 else 0,
        axis=1
    )

    df_data['Order Delivered_Not_In_Time'] = df_data.apply(
        lambda
            row: 1 if row['Delivered_Not_In_Time'] != 0 and row['Delivered_Not_In_Time'] + row[
            'Delivered_In_Time'] == row['sum_all'] else 0,
        axis=1
    )

    df_data = df_data.groupby(
        by=['order__ordered_at'],
        as_index=False
    ).agg({
        'Order Partially_Delivered_Not_In_Time':'sum',
        'Order Delivered_In_Time':'sum',
        'Order Delivered_Not_In_Time':'sum',
        'Order Partially_Delivered_In_Time':'sum',
        'Order Not_Delivered':'sum',
    })

    # def otif(row):
    #     sum = row['Not Delivered'] + row['Partially Delivered Not In Time'] + row['Partially Delivered In Time'] + \
    #           row['Delivered In Time'] + row['Delivered Not In Time']
    #     if sum != 0:
    #         return (row['Delivered In Time'] / sum) * 100
    #     else:
    #         return 0
    #
    # df_data['OTIF'] = df_data.apply(
    #     lambda row: otif(row),
    #     axis=1)


    figure = df_data.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['order__ordered_at'],
        y=[
            'Order Partially_Delivered_Not_In_Time',
            'Order Delivered_In_Time',
            'Order Delivered_Not_In_Time',
            'Order Partially_Delivered_In_Time',
            'Order Not_Delivered'
        ],
        theme='white',
        title='title',
        xTitle='Ordered Date',
        yTitle='Number of Orders',
    )
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # results = OrderDetail.objects.filter(
    #     product__in=selected_products,
    #     # product__category__in=selected_categories,
    #     # product__status__in=selected_status,
    #     order__ordered_at__gte=start_date,
    #     customer__in=[selected_customers],
    #     order__ordered_at__lte=end_date
    # )
    #
    # orderDetails = results.values(
    #     'id',
    #     'order',
    #     'order__reference',
    #     'order__ordered_at',
    #     'ordered_quantity',
    #     'desired_at',
    #     'order__delivery__delivered_at',
    #     'order__delivery__deliverydetail__delivered_quantity'
    # )
    #
    # new = read_frame(orderDetails)
    #
    # # new = df.groupby(
    # #     by=['product_id', 'customer_id', 'order__id','order__reference'],
    # #     as_index=False
    # # ).agg({
    # #     'order__delivery__deliverydetail__delivered_quantity': 'sum',
    # #     'order__delivery__delivered_at': 'max',
    # #     'desired_at': 'first',
    # #     'order__ordered_at': 'first',
    # #     'ordered_quantity': 'first',
    # # })
    #
    # # TODO Rename Data Frames
    #
    # new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
    #     'datetime64[ns]')
    #
    # new['desired_at'] = new['desired_at'].astype(
    #     'datetime64[ns]')
    #
    # new_df = new.rename(
    #     columns={
    #         "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
    #         "order__delivery__delivered_at": "delivered_at",
    #         'order__ordered_at': 'ordered_at',
    #     },
    #     errors="raise"
    # )
    #
    # if new_df.size != 0:
    #
    #     new_df['Not Delivered'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
    #         axis=1)
    #     new_df['Partially Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #
    #     new_df['Partially Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     df_data = new_df.groupby(['order__id','order__reference']).agg({
    #         'Not Delivered': 'sum',
    #         'Partially Delivered In Time': 'sum',
    #         'Partially Delivered Not In Time': 'sum',
    #         'Delivered In Time': 'sum',
    #         'ordered_at': 'first',
    #         'Delivered Not In Time': 'sum',
    #     }).reset_index()
    #
    #     df_data['sum_all'] = df_data.apply(
    #         lambda
    #             row: row['Not Delivered'] + row['Partially Delivered In Time'] + row[
    #             'Partially Delivered Not In Time'] + row['Delivered In Time'] + row['Delivered Not In Time'],
    #         axis=1)
    #
    #     df_data['Order Not Delivered'] = df_data.apply(
    #         lambda
    #             row: 1 if row['Not Delivered'] == row['sum_all'] and row['Not Delivered'] != 0 else None,
    #         axis=1
    #     )
    #
    #     df_data['Order Partially Delivered In Time'] = df_data.apply(
    #         lambda row: 1 if (
    #                 row['Partially Delivered Not In Time'] == 0
    #                 and row['Delivered Not In Time'] == 0
    #                 and row['Not Delivered'] < row['sum_all']
    #                 and (
    #                         row['Delivered In Time'] < row['sum_all']
    #                         or row['Partially Delivered In Time'] != 0
    #                 )
    #                 and row['Delivered In Time'] <= row['sum_all']
    #                 and row['sum_all'] != 0
    #         ) else None, axis=1)
    #
    #     df_data['Order Partially Delivered Not In Time'] = df_data.apply(
    #         lambda row: 1 if (row['Partially Delivered Not In Time'] != 0 or (
    #                     row['Delivered Not In Time'] < row['sum_all'] and row['Delivered Not In Time'] != 0)) and row[
    #                              'sum_all'] != 0 else None, axis=1)
    #
    #     df_data['Order Delivered In Time'] = df_data.apply(
    #         lambda
    #             row: 1 if row['Delivered In Time'] == row['sum_all'] and row['Delivered In Time'] != 0 else None,
    #         axis=1
    #     )
    #
    #     df_data['Order Delivered Not In Time'] = df_data.apply(
    #         lambda
    #             row: 1 if row['Delivered Not In Time'] != 0 and row['Delivered Not In Time'] + row[
    #             'Delivered In Time'] == row['sum_all'] else None,
    #         axis=1
    #     )
    #
    #     # def otif(row):
    #     #     sum = row['Not Delivered'] + row['Partially Delivered Not In Time'] + row['Partially Delivered In Time'] + \
    #     #           row['Delivered In Time'] + row['Delivered Not In Time']
    #     #     if sum != 0:
    #     #         return (row['Delivered In Time'] / sum) * 100
    #     #     else:
    #     #         return 0
    #     #
    #     # df_data['OTIF'] = df_data.apply(
    #     #     lambda row: otif(row),
    #     #     axis=1)
    #
    #
    #     figure = df_data.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='group',
    #         x=['ordered_at','order__reference'],
    #         y=[
    #             'Order Partially Delivered Not In Time',
    #             'Order Delivered In Time',
    #             'Order Delivered Not In Time',
    #             'Order Partially Delivered In Time',
    #             'Order Not Delivered'
    #         ],
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='Number of Orders',
    #     )
    # else:
    #
    #     figure = new_df.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='group',
    #         x=['customer_id'],
    #         y=None,
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='Number of Orders',
    #     )

    return figure
#
#
@app.callback(

    [
        Output(figure_pie_orderDetail_id, "figure"),
        Output(figure_pie_order_id, "figure"),
        Output(mini_card_subtitle_bias_percent_id, 'children'),
        Output(mini_card_subtitle_mape_id, 'children'),
        Output(mini_card_subtitle_mad_id, 'children'),
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
def plot_pie_statuts_product_figure(selected_products, selected_categories, selected_customers, selected_status,
                                    start_date, end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        # product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=[selected_customers],
        order__ordered_at__lte=end_date
    )

    #

    count_deliveries  = results.values('order__delivery').distinct().count()


    # train = parallelize_dataframe(results, read_frame)

    results = results.annotate(
        Not_Delivered=
        Case(
            When(order__delivery__deliverydetail__delivered_quantity=0, then=1),
            When(order__delivery__deliverydetail__delivered_quantity=None, then=1),
            When(order__delivery__delivered_at=None, then=1),
            default=0,
            output_field=IntegerField()
        ),
        Partially_Delivered_In_Time=
        Case(
            When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),
                 order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'),
                 desired_at__gte=F('order__delivery__delivered_at'), then=1),
            default=0,
            output_field=IntegerField()
        ),
        Partially_Delivered_Not_In_Time=
        Case(
            When(order__delivery__deliverydetail__delivered_quantity__lt=F('ordered_quantity'),
                 order__delivery__deliverydetail__delivered_quantity__gt=F('ordered_quantity'),
                 desired_at__lt=F('order__delivery__delivered_at'), then=1),
            default=0,
            output_field=IntegerField()
        ),
        Delivered_In_Time=
        Case(
            When(
                order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                desired_at__lte=F('order__delivery__delivered_at'), then=1),
            default=0,
            output_field=IntegerField()
        ),
        Delivered_Not_In_Time=
        Case(
            When(
                order__delivery__deliverydetail__delivered_quantity__gte=F('ordered_quantity'),
                desired_at__gte=F('order__delivery__delivered_at'), then=1),
            default=0,
            output_field=IntegerField()
        )
    )

    # ************************************

    results_order  = results.values('order').annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time =Sum('Delivered_In_Time'),
        Delivered_Not_In_Time =Sum('Delivered_Not_In_Time'),
    ).values('order','Not_Delivered','Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time','Delivered_In_Time','Delivered_Not_In_Time')

    df_data_order = read_frame(results_order)

    print(df_data_order,len(df_data_order.index),'ouadidou')

    Number_of_orders = len(df_data_order.index)

    df_data_order['sum_all'] = df_data_order.apply(
        lambda
            row: row['Not_Delivered'] + row['Partially_Delivered_In_Time'] + row[
            'Partially_Delivered_Not_In_Time'] + row['Delivered_In_Time'] + row['Delivered_Not_In_Time'],
        axis=1)

    df_data_order['Order Not_Delivered'] = df_data_order.apply(
        lambda
            row: 1 if row['Not_Delivered'] == row['sum_all'] and row['Not_Delivered'] != 0 else None,
        axis=1
    )

    df_data_order['Order Partially_Delivered_In_Time'] = df_data_order.apply(
        lambda row: 1 if (
                row['Partially_Delivered_Not_In_Time'] == 0
                and row['Delivered_Not_In_Time'] == 0
                and row['Not_Delivered'] < row['sum_all']
                and (
                        row['Delivered_In_Time'] < row['sum_all']
                        or row['Partially_Delivered_In_Time'] != 0
                )
                and row['Delivered_In_Time'] <= row['sum_all']
                and row['sum_all'] != 0
        ) else 0, axis=1)

    df_data_order['Order Partially_Delivered_Not_In_Time'] = df_data_order.apply(
        lambda row: 1 if (row['Partially_Delivered_Not_In_Time'] != 0 or (
                row['Delivered_Not_In_Time'] < row['sum_all'] and row['Delivered_Not_In_Time'] != 0)) and row[
                             'sum_all'] != 0 else 0, axis=1)

    df_data_order['Order Delivered_In_Time'] = df_data_order.apply(
        lambda
            row: 1 if row['Delivered_In_Time'] == row['sum_all'] and row['Delivered_In_Time'] != 0 else 0,
        axis=1
    )

    df_data_order['Order Delivered_Not_In_Time'] = df_data_order.apply(
        lambda
            row: 1 if row['Delivered_Not_In_Time'] != 0 and row['Delivered_Not_In_Time'] + row[
            'Delivered_In_Time'] == row['sum_all'] else 0,
        axis=1
    )

    df_data_order = df_data_order.agg({
        'Order Not_Delivered': 'sum',
        'Order Delivered_In_Time':'sum',
        'Order Partially_Delivered_In_Time':'sum',
        'Order Partially_Delivered_Not_In_Time': 'sum',
        'Order Delivered_Not_In_Time': 'sum',
    }).reset_index()

    # ************************************
    results = results.annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time=Sum('Delivered_In_Time'),
        Delivered_Not_In_Time=Sum('Delivered_Not_In_Time'),
    ).values('Not_Delivered', 'Partially_Delivered_In_Time',
             'Partially_Delivered_Not_In_Time', 'Delivered_In_Time', 'Delivered_Not_In_Time')

    df_data = read_frame(results)


    labels = df_data.index
    values = df_data.values

    print(labels,values,'desert')

    df_data = df_data.agg({
        'Not_Delivered': 'sum',
        'Delivered_In_Time': 'sum',
        'Partially_Delivered_In_Time': 'sum',
        'Partially_Delivered_Not_In_Time': 'sum',
        'Delivered_Not_In_Time': 'sum',
    }).reset_index()

    sum_all = df_data[0][0]+df_data[0][1]+df_data[0][2]+df_data[0][3]+df_data[0][4]

    if sum_all!=0:

        OTIF = (df_data[0][0]/sum_all)*100

    else:
        OTIF = 0

    OTIF = round(OTIF, 3)


    figure_pie_orderDetail = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    figure_pie_order =  make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])



    figure_pie_order.add_trace(
        go.Pie(
            labels=df_data_order['index'],
            values=df_data_order[0],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'red',
                    'rgb(0, 200, 0)',
                    'rgb(0,255,0)',
                    'rgb(255, 230, 0)',
                    'rgb(255, 132, 0)',
                ]
            },
        )
    , 1, 1)

    figure_pie_orderDetail.add_trace(
        go.Pie(
            labels=df_data['index'],
            values=df_data[0],
            pull=[0.1, 0.2, 0.2, 0.2],
            name="",
            marker={
                'colors': [
                    'red',
                    'rgb(0, 200, 0)',
                    'rgb(0,255,0)',
                    'rgb(255, 230, 0)',
                    'rgb(255, 132, 0)',
                ]
            },
        )
    , 1, 1)

    figure_pie_orderDetail.update_traces(hole=.4, hoverinfo="label+percent+name")
    figure_pie_order.update_traces(hole=.4, hoverinfo="label+percent+name")
    # results = OrderDetail.objects.filter(
    #     product__in=selected_products,
    #     # product__category__in=selected_categories,
    #     # product__status__in=selected_status,
    #     order__ordered_at__gte=start_date,
    #     customer__in=[selected_customers],
    #     order__ordered_at__lte=end_date
    # )
    #
    # orderDetails = results.values(
    #     'id',
    #     'order__id',
    #     'product_id',
    #     'customer_id',
    #     'order__delivery__id',
    #     'order__ordered_at',
    #     'ordered_quantity',
    #     'desired_at',
    #     'order__delivery__delivered_at',
    #     'order__delivery__deliverydetail__delivered_quantity'
    # )
    #
    # df = read_frame(orderDetails)
    #
    # new = df.groupby(
    #     by=['product_id', 'customer_id', 'order__id'],
    #     as_index=False
    # ).agg({
    #     'order__delivery__deliverydetail__delivered_quantity': 'sum',
    #     'order__delivery__delivered_at': 'max',
    #     'desired_at': 'first',
    #     'ordered_quantity': 'first',
    # })
    #
    # # TODO Rename Data Frames
    #
    # new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
    #     'datetime64[ns]')
    #
    # new['desired_at'] = new['desired_at'].astype(
    #     'datetime64[ns]')
    #
    # new_df = new.rename(
    #     columns={
    #         "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
    #         "order__delivery__delivered_at": "delivered_at",
    #     },
    #     errors="raise"
    # )
    #
    #
    #
    # if new_df.size != 0:
    #
    #     new_df['Not Delivered'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
    #         axis=1)
    #     new_df['Partially Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #
    #     new_df['Partially Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
    #         axis=1)
    #     new_df['Delivered Not In Time'] = new_df.apply(
    #         lambda
    #             row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
    #         axis=1)
    #
    #
    #     df_data = new_df.agg({
    #         'Not Delivered': 'sum',
    #         'Delivered In Time': 'sum',
    #         'Partially Delivered In Time': 'sum',
    #         'Partially Delivered Not In Time': 'sum',
    #         'Delivered Not In Time': 'sum',
    #     }).reset_index()
    #
    #
    #     figure = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    #
    #
    #     figure.add_trace(
    #         go.Pie(
    #             labels=df_data['index'],
    #             values=df_data[0],
    #             name="",
    #             marker={
    #                 'colors': [
    #                     'red',
    #                     'rgb(255,165,0)',
    #                     'rgb(0, 204, 0)',
    #                     'rgb(0, 48, 240)',
    #                 ]
    #             },
    #         )
    #         , 1, 1)
    #
    #     figure.update_traces(hole=.4, hoverinfo="label+percent+name")
    # else:
    #     figure = new_df.iplot(
    #         asFigure=True,
    #         kind='bar',
    #         barmode='group',
    #         x=['customer_id'],
    #         y=None,
    #         theme='white',
    #         title='title',
    #         xTitle='customer',
    #         yTitle='Number of Orders',
    #     )

    return figure_pie_orderDetail,figure_pie_order,str(OTIF)+'%',Number_of_orders,count_deliveries


dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id)
