import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from common.dashboards import dash_utils
from dash.dependencies import Input, Output
from django.utils.translation import gettext as _
from django_plotly_dash import DjangoDash
from stock.models import Product, ProductCategory, Supplier, OrderDetail,Delivery
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
from .app import app
from .ids import *


@app.callback(

    Output(FIGURE_SUPPLIER_ID, "figure"),
    [
        Input(DROPDOWN_PRODUCT_LIST_ID, "value"),
        Input(DROPDOWN_CATEGORIE_LIST_ID, "value"),
        Input(DROPDOWN_SUPPLIER_LIST_ID, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(INPUT_DATE_RANGE_ID, 'start_date'),
        Input(INPUT_DATE_RANGE_ID, 'end_date'),
    ]
)
def plot_OrderDetail_count_by_custmoer_figure(selected_products, 
                                              selected_categories,
                                              selected_suppliers,
                                              selected_abc,selected_fmr,
                                              start_date,
                                              end_date):

    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        order__ordered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        order__ordered_at__lte=end_date
    )
    #

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
    print(results)
    # dff = pd.DataFrame.from_records(res)
    # print(dff,'oppi')
    results  = results.values('supplier_id','supplier__reference').annotate(
        Not_Delivered=Sum('Not_Delivered'),
        Partially_Delivered_In_Time=Sum('Partially_Delivered_In_Time'),
        Partially_Delivered_Not_In_Time=Sum('Partially_Delivered_Not_In_Time'),
        Delivered_In_Time =Sum('Delivered_In_Time'),
        Delivered_Not_In_Time =Sum('Delivered_Not_In_Time'),
    ).values('supplier','supplier__reference', 'Not_Delivered','Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time','Delivered_In_Time','Delivered_Not_In_Time')


    df = pd.DataFrame.from_records(results)



    figure = df.iplot(
        asFigure=True,
        kind='bar',
        barmode='group',
        x=['supplier__reference'],
        y=['Not_Delivered', 'Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time', 'Delivered_In_Time', 'Delivered_Not_In_Time'],
        colors= [
            'rgb(255, 0, 0)',
            'rgb(0, 255, 0)',
            'rgb(255, 230, 0)',
            'rgb(0,200,0)',
            'rgb(255, 132, 0)',
        ],
        theme='white',
        title='title',
        xTitle='supplier',
        yTitle='Number of Orders',
    )


    return figure



@app.callback(
    Output(FIGURE_OTIF_ID, "figure"),
    [
        Input(DROPDOWN_PRODUCT_LIST_ID, "value"),
        Input(DROPDOWN_CATEGORIE_LIST_ID, "value"),
        Input(DROPDOWN_SUPPLIER_LIST_ID, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(INPUT_DATE_RANGE_ID, 'start_date'),
        Input(INPUT_DATE_RANGE_ID, 'end_date'),
    ]
)
def plot_otif_by_date_figure(selected_products, selected_categories, selected_suppliers,selected_abc,
                                              selected_fmr, start_date,end_date):



    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        order__ordered_at__gte=start_date,
        supplier__in=[selected_suppliers],
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
    
    print(len(results),'olaa')

    df_data = read_frame(results)
    
    print(len(df_data),'olaa')


    def otif(row):
        sum = row['Not_Delivered'] + row['Partially_Delivered_In_Time'] + row['Partially_Delivered_Not_In_Time'] + row['Delivered_In_Time'] + row['Delivered_Not_In_Time']
        if sum != 0:
            return (row['Delivered_In_Time'] / sum) * 100
        else:
            return 0

    df_data['OTIF'] = df_data.apply(
        lambda row: otif(row),
        axis=1)
    
    


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
    
    figure.update_xaxes(
            tickformat = '%d %B %Y',
    )


    return figure
#
#
@app.callback(

    Output(FIGURE_ORDERSDETAILS_ID, "figure"),
    [
        Input(DROPDOWN_PRODUCT_LIST_ID, "value"),
        Input(DROPDOWN_CATEGORIE_LIST_ID, "value"),
        Input(DROPDOWN_SUPPLIER_LIST_ID, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(INPUT_DATE_RANGE_ID, 'start_date'),
        Input(INPUT_DATE_RANGE_ID, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_suppliers, selected_abc,selected_fmr, start_date,
                            end_date):


    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        order__ordered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        order__ordered_at__lte=end_date
    )

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

        x=['order__ordered_at'],
        y=['Not_Delivered', 'Partially_Delivered_In_Time','Partially_Delivered_Not_In_Time', 'Delivered_In_Time', 'Delivered_Not_In_Time'],
        colors= [
            'rgb(255, 0, 0)',
            'rgb(0, 255, 0)',
            'rgb(255, 230, 0)',
            'rgb(0,200,0)',
            'rgb(255, 132, 0)',
        ],
        theme='white',
        title='title',
        xTitle='date ',
        yTitle='Number of Orders',
    )
    
    figure.update_xaxes(
            tickformat = '%d %B %Y',
    )

    return figure
#
#
@app.callback(

    Output(FIGURE_ORDERS_ID, "figure"),
    [
        Input(DROPDOWN_PRODUCT_LIST_ID, "value"),
        Input(DROPDOWN_CATEGORIE_LIST_ID, "value"),
        Input(DROPDOWN_SUPPLIER_LIST_ID, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(INPUT_DATE_RANGE_ID, 'start_date'),
        Input(INPUT_DATE_RANGE_ID, 'end_date'),
    ]
)
def plot_order_count_figure(selected_products, selected_categories, selected_suppliers, selected_abc,selected_fmr, start_date,
                            end_date):


    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        order__ordered_at__gte=start_date,
        supplier__in=[selected_suppliers],
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
        colors= [
                'rgb(255, 230, 0)',
                'rgb(0, 200, 0)',
                'rgb(255, 132, 0)',
                'rgb(0,255,0)',
                'red',
        ],
        theme='white',
        title='title',
        xTitle='Ordered Date',
        yTitle='Number of Orders',
    )
    
    figure.update_xaxes(
            tickformat = '%d %B %Y',
    )

    return figure
#
#
@app.callback(

    [
        Output(FIGURE_PIE_ORDERDETAIL_ID, "figure"),
        Output(FIGURE_PIE_ORDER_ID, "figure"),
        Output(SUBTITLE_DELIVERIES_ID, 'children'),
        Output(SUBTITLE_ORDERS_ID, 'children'),
        Output(SUBTITLE_OTIF_ID, 'children'),
        # Output("400", "value"), 
        # Output("400", "children"),
        # Output("400", "color")   
    ],
    [
        Input(DROPDOWN_PRODUCT_LIST_ID, "value"),
        Input(DROPDOWN_CATEGORIE_LIST_ID, "value"),
        Input(DROPDOWN_SUPPLIER_LIST_ID, "value"),
        Input(dropdown_abc_list_id, "value"),
        Input(dropdown_fmr_list_id, "value"),
        Input(INPUT_DATE_RANGE_ID, 'start_date'),
        Input(INPUT_DATE_RANGE_ID, 'end_date'),
    ]
)
def plot_pie_statuts_product_figure(selected_products, selected_categories, selected_suppliers, selected_abc,selected_fmr,
                                    start_date, end_date):
    results = OrderDetail.objects.filter(
        product__in=selected_products,
        # product__category__in=selected_categories,
        product__fmr_segmentation__in=selected_fmr,
        product__abc_segmentation__in=selected_abc,
        order__ordered_at__gte=start_date,
        supplier__in=[selected_suppliers],
        order__ordered_at__lte=end_date
    )

    Number_of_deliveries  = results.values('order__delivery').distinct()

    
    Number_of_deliveries  = Number_of_deliveries.count()

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

    df_data = df_data.agg({
        'Not_Delivered': 'sum',
        'Delivered_In_Time': 'sum',
        'Partially_Delivered_In_Time': 'sum',
        'Partially_Delivered_Not_In_Time': 'sum',
        'Delivered_Not_In_Time': 'sum',
    }).reset_index()

    sum_all = df_data[0][0]+df_data[0][1]+df_data[0][2]+df_data[0][3]+df_data[0][4]

    if sum_all!=0:

        OTIF = (df_data[0][1]/sum_all)*100

    else:
        OTIF = 0

    OTIF = round(OTIF, 1)


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
    
    if OTIF>=80 : 
        color  = 'success' 
    elif OTIF>= 20 and OTIF<80 :
        color  = "info" 
    elif OTIF>= 10 and OTIF<20 :
        color  = 'warning' 
    else :
        color  = "danger"
    
    


    return figure_pie_orderDetail,figure_pie_order,Number_of_deliveries,Number_of_orders,str(OTIF)+'%'


dash_utils.select_all_callbacks(
    app, DROPDOWN_PRODUCT_LIST_ID, DIV_PRODUCT_LIST_ID, CHECKBOX_PRODUCT_LIST_ID)

dash_utils.select_all_callbacks(
    app, DROPDOWN_SUPPLIER_LIST_ID, DIV_SUPPLIER_LIST_ID, CHECKBOX_SUPPLIER_LIST_ID)

dash_utils.select_all_callbacks(
    app, dropdown_abc_list_id, div_abc_list_id, checkbox_abc_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_fmr_list_id, div_fmr_list_id, checkbox_fmr_list_id)

dash_utils.select_all_callbacks(
    app, DROPDOWN_CATEGORIE_LIST_ID, DIV_CATEGORIE_LIST_ID, CHECKBOX_CATEGORIE_LIST_ID)

dash_utils.select_all_callbacks(
    app, DROPDOWN_STATUT_LIST_ID, DIV_STATUT_LIST_ID, CHECKBOX_STATUT_LIST_ID)
