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
from plotly.subplots import make_subplots

import colorlover, plotly

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('otif', add_bootstrap_links=True)
_prefix = 'otif'

# ------------------------------------------{Id Graph}--------------------------------------------------------

figure_customer_id = dash_utils.generate_html_id(_prefix, 'figure_customer_id')
figure_ordersDetails_id = dash_utils.generate_html_id(_prefix, 'figure_orderDetails_id')
figure_count_product_id = dash_utils.generate_html_id(_prefix, 'figure_count_product_id')
figure_most_ordred_product_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_product_id')
figure_most_ordred_customer_id = dash_utils.generate_html_id(_prefix, 'figure_most_ordred_customer_id')
figure_pie_statuts_product_id = dash_utils.generate_html_id(_prefix, 'figure_pie_statuts_product_id')
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

input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

_all_products = list(Product.objects.get_all_products())
_all_categories = list(ProductCategory.objects.get_all_productcategory())
_all_customers = list(Customer.objects.get_all_customers())[0:10]
_all_status = list(Product.objects.get_all_status_of_products())

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
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id, _all_customers,
                    'Customers')
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
                                                label='Customers',
                                                value='what-is',
                                                children=html.Div(
                                                    [dcc.Graph(id=figure_customer_id)],
                                                    className="",
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
                                                            children=html.Div(
                                                                [dcc.Graph(id=figure_count_product_id)],
                                                                className="",
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
                ], sm=12, md=12, lg=12),

            ]),
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
                                        children=html.Div(
                                            [dcc.Graph(id=figure_ordersDetails_id)],
                                            className="",
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
                                                    children=html.Div(
                                                        [dcc.Graph(id=figure_orders_id)],
                                                        className="",
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
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id=figure_pie_statuts_product_id)],
                        className="pretty_container",
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
        #product__category__in=selected_categories,
        #product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        #customer__in=selected_customers,
        order__ordered_at__lte=end_date
    )

    orderDetails = results.values(
        'id',
        'order__id',
        'product_id',
        'customer_id',
        'order__delivery__id',
        'order__ordered_at',
        'ordered_quantity',
        'desired_at',
        'order__delivery__delivered_at',
        'order__delivery__deliverydetail__delivered_quantity'
    )

    df = read_frame(orderDetails)

    new = df.groupby(
        by=['product_id', 'customer_id', 'order__id'],
        as_index=False
    ).agg({
        'order__delivery__deliverydetail__delivered_quantity': 'sum',
        'order__delivery__delivered_at': 'max',
        'desired_at': 'first',
        'ordered_quantity': 'first',
    })

    # TODO Rename Data Frames

    new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
        'datetime64[ns]')

    new['desired_at'] = new['desired_at'].astype(
        'datetime64[ns]')

    new_df = new.rename(
        columns={
            "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
            "order__delivery__delivered_at": "delivered_at",
        },
        errors="raise"
    )

    if new_df.size != 0:

        new_df['Not Delivered'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
            axis=1)
        new_df['Partially Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)

        new_df['Partially Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        new_df['Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)
        new_df['Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        df_data = new_df.groupby(['customer_id']).agg({
            'Not Delivered': 'sum',
            'Partially Delivered In Time': 'sum',
            'Partially Delivered Not In Time': 'sum',
            'Delivered In Time': 'sum',
            'Delivered Not In Time': 'sum',
        }).reset_index()

        figure = df_data.iplot(
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
            x=['customer_id'],
            y=['Not Delivered', 'Partially Delivered In Time','Partially Delivered Not In Time', 'Delivered In Time', 'Delivered Not In Time'],
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='Number of Orders',
        )
    else:
        figure = new_df.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x=['customer_id'],
            y=None,
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='Number of Orders',
        )

    return figure


@app.callback(

    Output(figure_count_product_id, "figure"),
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
        product__category__in=selected_categories,
        product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=selected_customers,
        order__ordered_at__lte=end_date
    )

    orderDetails = results.values(
        'id',
        'order__id',
        'product_id',
        'customer_id',
        'order__delivery__id',
        'order__ordered_at',
        'ordered_quantity',
        'desired_at',
        'order__delivery__delivered_at',
        'order__delivery__deliverydetail__delivered_quantity'
    )

    df = read_frame(orderDetails)

    new = df.groupby(
        by=['product_id', 'customer_id', 'order__id'],
        as_index=False
    ).agg({
        'order__delivery__deliverydetail__delivered_quantity': 'sum',
        'order__delivery__delivered_at': 'max',
        'desired_at': 'first',
        'ordered_quantity': 'first',
    })

    # TODO Rename Data Frames

    new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
        'datetime64[ns]')

    new['desired_at'] = new['desired_at'].astype(
        'datetime64[ns]')

    new_df = new.rename(
        columns={
            "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
            "order__delivery__delivered_at": "delivered_at",
        },
        errors="raise"
    )

    if new_df.size != 0:

        new_df['Not Delivered'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
            axis=1)
        new_df['Partially Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)

        new_df['Partially Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        new_df['Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)
        new_df['Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        df_data = new_df.groupby(['customer_id']).agg({
            'Not Delivered': 'sum',
            'Partially Delivered In Time': 'sum',
            'Partially Delivered Not In Time': 'sum',
            'Delivered In Time': 'sum',
            'Delivered Not In Time': 'sum',
        }).reset_index()

        def otif(row):
            sum = row['Not Delivered'] + row['Partially Delivered In Time']+ row['Partially Delivered Not In Time'] + row['Delivered In Time'] + row[
                'Delivered Not In Time']
            if sum != 0:
                return (row['Delivered In Time'] / sum) * 100
            else:
                return 0

        df_data['OTIF'] = df_data.apply(
            lambda row: otif(row),
            axis=1)

        frame = df_data.sort_values(by=['OTIF'], ascending=False)

        figure = frame.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x=['customer_id'],
            y=['OTIF'],
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='OTIF',
        )
    else:
        figure = new_df.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x=['customer_id'],
            y=None,
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
        product__category__in=selected_categories,
        product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=selected_customers,
        order__ordered_at__lte=end_date
    )

    orderDetails = results.values(
        'id',
        'order__id',
        'product_id',
        'customer_id',
        'order__delivery__id',
        'order__ordered_at',
        'ordered_quantity',
        'desired_at',
        'order__delivery__delivered_at',
        'order__delivery__deliverydetail__delivered_quantity'
    )

    df = read_frame(orderDetails)

    new = df.groupby(
        by=['product_id', 'customer_id', 'order__id'],
        as_index=False
    ).agg({
        'order__delivery__deliverydetail__delivered_quantity': 'sum',
        'order__delivery__delivered_at': 'max',
        'desired_at': 'first',
        'order__ordered_at': 'first',
        'ordered_quantity': 'first',
    })

    # TODO Rename Data Frames

    new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
        'datetime64[ns]')

    new['desired_at'] = new['desired_at'].astype(
        'datetime64[ns]')

    new_df = new.rename(
        columns={
            "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
            "order__delivery__delivered_at": "delivered_at",
            'order__ordered_at': 'ordered_at',
        },
        errors="raise"
    )

    if new_df.size != 0:

        new_df['Not Delivered'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
            axis=1)
        new_df['Partially Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)

        new_df['Partially Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        new_df['Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)
        new_df['Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        df_data = new_df.groupby(['ordered_at']).agg({
            'Not Delivered': 'sum',
            'Partially Delivered In Time': 'sum',
            'Partially Delivered Not In Time':'sum',
            'Delivered In Time': 'sum',
            'Delivered Not In Time': 'sum',
        }).reset_index()

        figure = df_data.iplot(
            asFigure=True,
            kind='bar',
            barmode='stack',
            colors=[
                'rgb(255,0,0)',
                'rgb(255,165,0)',
                'rgb(0, 204, 0)',
                'rgb(0, 48, 240)',
                'rgb(0,255, 0)',
            ],
            x='ordered_at',
            y=['Not Delivered', 'Partially Delivered In Time','Partially Delivered Not In Time', 'Delivered In Time', 'Delivered Not In Time'],
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='Number of Orders',
        )
    else:

        figure = new_df.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x=['customer_id'],
            y=None,
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
        product__category__in=selected_categories,
        product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=selected_customers,
        order__ordered_at__lte=end_date
    )

    orderDetails = results.values(
        'id',
        'order__id',
        'product_id',
        'customer_id',
        'order__delivery__id',
        'order__ordered_at',
        'ordered_quantity',
        'desired_at',
        'order__delivery__delivered_at',
        'order__delivery__deliverydetail__delivered_quantity'
    )

    df = read_frame(orderDetails)

    new = df.groupby(
        by=['product_id', 'customer_id', 'order__id'],
        as_index=False
    ).agg({
        'order__delivery__deliverydetail__delivered_quantity': 'sum',
        'order__delivery__delivered_at': 'max',
        'desired_at': 'first',
        'order__ordered_at': 'first',
        'ordered_quantity': 'first',
    })

    # TODO Rename Data Frames

    new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
        'datetime64[ns]')

    new['desired_at'] = new['desired_at'].astype(
        'datetime64[ns]')

    new_df = new.rename(
        columns={
            "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
            "order__delivery__delivered_at": "delivered_at",
            'order__ordered_at': 'ordered_at',
        },
        errors="raise"
    )

    print(new_df)

    if new_df.size != 0:

        new_df['Not Delivered'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
            axis=1)
        new_df['Partially Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)

        new_df['Partially Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        new_df['Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)
        new_df['Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        df_data = new_df.groupby(['order__id']).agg({
            'Not Delivered': 'sum',
            'Partially Delivered In Time': 'sum',
            'Partially Delivered Not In Time': 'sum',
            'Delivered In Time': 'sum',
            'ordered_at': 'first',
            'Delivered Not In Time': 'sum',
        }).reset_index()

        df_data['sum_all'] = df_data.apply(
            lambda
                row: row['Not Delivered'] + row['Partially Delivered In Time'] + row[
                'Partially Delivered Not In Time'] + row['Delivered In Time'] + row['Delivered Not In Time'],
            axis=1)

        df_data['Order Not Delivered'] = df_data.apply(
            lambda
                row: 1 if row['Not Delivered'] == row['sum_all'] and row['Not Delivered'] != 0 else None,
            axis=1
        )

        df_data['Order Partially Delivered In Time'] = df_data.apply(
            lambda row: 1 if (
                    row['Partially Delivered Not In Time'] == 0
                    and row['Delivered Not In Time'] == 0
                    and row['Not Delivered'] < row['sum_all']
                    and (
                            row['Delivered In Time'] < row['sum_all']

                            or row['Partially Delivered In Time'] != 0
                    )
                    and row['Delivered In Time'] <= row['sum_all']
                    and row['sum_all'] != 0
            ) else None, axis=1)

        df_data['Order Partially Delivered Not In Time'] = df_data.apply(
            lambda row: 1 if (row['Partially Delivered Not In Time'] != 0 or (
                        row['Delivered Not In Time'] < row['sum_all'] and row['Delivered Not In Time'] != 0)) and row[
                                 'sum_all'] != 0 else None, axis=1)

        df_data['Order Delivered In Time'] = df_data.apply(
            lambda
                row: 1 if row['Delivered In Time'] == row['sum_all'] and row['Delivered In Time'] != 0 else None,
            axis=1
        )

        df_data['Order Delivered Not In Time'] = df_data.apply(
            lambda
                row: 1 if row['Delivered Not In Time'] != 0 and row['Delivered Not In Time'] + row[
                'Delivered In Time'] == row['sum_all'] else None,
            axis=1
        )

        def otif(row):
            sum = row['Not Delivered'] + row['Partially Delivered Not In Time'] + row['Partially Delivered In Time'] + \
                  row['Delivered In Time'] + row['Delivered Not In Time']
            if sum != 0:
                return (row['Delivered In Time'] / sum) * 100
            else:
                return 0

        df_data['OTIF'] = df_data.apply(
            lambda row: otif(row),
            axis=1)

        print(df_data)

        figure = df_data.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x='ordered_at',
            y=[
                'Order Partially Delivered Not In Time',
                'Order Delivered In Time',
                'Order Delivered Not In Time',
                'Order Partially Delivered In Time',
                'Order Not Delivered'
            ],
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='Number of Orders',
        )
    else:

        figure = new_df.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x=['customer_id'],
            y=None,
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='Number of Orders',
        )

    return figure


@app.callback(

    Output(figure_pie_statuts_product_id, "figure"),
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
        product__category__in=selected_categories,
        product__status__in=selected_status,
        order__ordered_at__gte=start_date,
        customer__in=selected_customers,
        order__ordered_at__lte=end_date
    )

    orderDetails = results.values(
        'id',
        'order__id',
        'product_id',
        'customer_id',
        'order__delivery__id',
        'order__ordered_at',
        'ordered_quantity',
        'desired_at',
        'order__delivery__delivered_at',
        'order__delivery__deliverydetail__delivered_quantity'
    )

    df = read_frame(orderDetails)

    new = df.groupby(
        by=['product_id', 'customer_id', 'order__id'],
        as_index=False
    ).agg({
        'order__delivery__deliverydetail__delivered_quantity': 'sum',
        'order__delivery__delivered_at': 'max',
        'desired_at': 'first',
        'ordered_quantity': 'first',
    })

    # TODO Rename Data Frames

    new['order__delivery__delivered_at'] = new['order__delivery__delivered_at'].astype(
        'datetime64[ns]')

    new['desired_at'] = new['desired_at'].astype(
        'datetime64[ns]')

    new_df = new.rename(
        columns={
            "order__delivery__deliverydetail__delivered_quantity": "delivered_quantity",
            "order__delivery__delivered_at": "delivered_at",
        },
        errors="raise"
    )

    figure = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])

    if new_df.size != 0:

        new_df['Not Delivered'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity == 0 or row.delivered_quantity is None or row.delivered_at is None else None,
            axis=1)
        new_df['Partially Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)

        new_df['Partially Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if 0 < row.delivered_quantity < row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        new_df['Delivered In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at >= row.delivered_at else None,
            axis=1)
        new_df['Delivered Not In Time'] = new_df.apply(
            lambda
                row: 1 if row.delivered_quantity >= row.ordered_quantity and row.desired_at < row.delivered_at else None,
            axis=1)
        df_data = new_df.agg({
            'Not Delivered': 'sum',
            'Delivered In Time': 'sum',
            'Partially Delivered In Time': 'sum',
            'Partially Delivered Not In Time': 'sum',
            'Delivered Not In Time': 'sum',
        }).reset_index()

        figure.add_trace(
            go.Pie(
                labels=df_data['index'],
                values=df_data[0],
                name="",
                marker={
                    'colors': [
                        'red',
                        'rgb(255,165,0)',
                        'rgb(0, 204, 0)',
                        'rgb(0, 48, 240)',
                    ]
                },
            )
            , 1, 1)

        figure.update_traces(hole=.4, hoverinfo="label+percent+name")
    else:
        figure = new_df.iplot(
            asFigure=True,
            kind='bar',
            barmode='group',
            x=['customer_id'],
            y=None,
            theme='white',
            title='title',
            xTitle='customer',
            yTitle='Number of Orders',
        )

    return figure


dash_utils.select_all_callbacks(
    app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id)
