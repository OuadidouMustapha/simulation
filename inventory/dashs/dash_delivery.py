# Import required libraries
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from common.dashboards import dash_constants, dash_utils
from dash.dependencies import ClientsideFunction, Input, Output, State
from django.utils.translation import gettext as _
from django_plotly_dash import DjangoDash
from stock.models import Product,ProductCategory,Delivery,Customer,DeliveryDetail
from django_pandas.io import read_frame
import cufflinks as cf
from plotly.subplots import make_subplots

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

app = DjangoDash('delivery',add_bootstrap_links=True)
_prefix = 'delivery'

#------------------------------------------{Id Graph}--------------------------------------------------------

figure_count_deliveries_id           = dash_utils.generate_html_id(_prefix, 'figure_count_deliverys_id')
figure_count_product_id              = dash_utils.generate_html_id(_prefix, 'figure_count_product_id')
figure_most_delivred_product_id      = dash_utils.generate_html_id(_prefix, 'figure_most_delivred_product_id')
figure_most_delivred_customer_id     = dash_utils.generate_html_id(_prefix, 'figure_most_delivred_customer_id')
figure_pie_statuts_product_id        = dash_utils.generate_html_id(_prefix, 'figure_pie_statuts_product_id')
figure_most_delivred_categories_id   = dash_utils.generate_html_id(_prefix, 'figure_pie_delivred_categories_id')


#------------------------------------------------------------------------------------------------------------

details_product_list_id = dash_utils.generate_html_id(_prefix, 'details_product_list_id')

#--------------------------------------------Dropdown  list -------------------------------------------------

dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
dropdown_categorie_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_categorie_list_id')
dropdown_delivery_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_delivery_list_id')
dropdown_customer_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_customer_list_id')
dropdown_statut_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_statut_list_id')

#--------------------------------------------Div list -------------------------------------------
div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
div_delivery_list_id = dash_utils.generate_html_id(_prefix, 'div_delivery_list_id')
div_categorie_list_id = dash_utils.generate_html_id(_prefix, 'div_categorie_list_id')
div_customer_list_id = dash_utils.generate_html_id(_prefix, 'div_customer_list_id')
div_statut_list_id = dash_utils.generate_html_id(_prefix, 'div_statut_list_id')

#--------------------------------------------Checkbox list --------------------------------------
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
checkbox_categorie_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_categorie_list_id')
checkbox_delivery_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_delivery_list_id')
checkbox_customer_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_customer_list_id')
checkbox_statut_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_statut_list_id')


input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')

_all_products     = list(Product.objects.get_all_products())
_all_categories   = list(ProductCategory.objects.get_all_productcategory())
_all_customers    = list(Customer.objects.get_all_customers())
_all_status       = list(Product.objects.get_all_status_of_products())


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
                    dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id, _all_categories, 'Categories')
            ], sm=12, md=6, lg=4),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id, _all_status, 'Status')
            ], sm=12, md=6, lg=4),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id, _all_customers, 'Customers')
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
                                                label='Graph Numbre Of deliverys          ',
                                                value='what-is',
                                                children= html.Div(
                                                    [dcc.Graph(id=figure_count_deliveries_id)],
                                                    className="",
                                                ),
                                            ),
                                            dcc.Tab(
                                                label='Number Of deliveryd Products',
                                                value='Product',
                                                children=html.Div(
                                                    className='control-tab', 
                                                    children=[
                                                        html.Div(
                                                            className='app-controls-block',
                                                            children= html.Div(
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
                                            children= html.Div(
                                                [dcc.Graph(id=figure_most_delivred_product_id)],
                                                className="",
                                            ),
                                        ),
                                        dcc.Tab(
                                            label='Top 10 Customers Making deliverys',
                                            value='show-sequences',
                                            children=html.Div(
                                                className='control-tab', 
                                                children=[
                                                    html.Div(
                                                        className='app-controls-block',
                                                        children= html.Div(
                                                            [dcc.Graph(id=figure_most_delivred_customer_id)],
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
                                                        children= html.Div(
                                                            [dcc.Graph(id=figure_most_delivred_categories_id)],
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
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_delivery_count_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
    results = DeliveryDetail.objects.filter(
            product__in=selected_products,
            product__category__in=selected_categories,
            product__status__in=selected_status,
            delivery__delivered_at__gte=start_date,
            customer__in=selected_customers,
            delivery__delivered_at__lte=end_date)
    results = results.values('delivery__delivered_at','delivery')

    delivery_df = read_frame(results)

    delivery_df = delivery_df.groupby(
        by=['delivery__delivered_at','delivery'],
    ).size()
    
    delivery_df = delivery_df.groupby(
        by=['delivery__delivered_at'],
    ).size().reset_index(name='counts')

    figure = delivery_df.iplot(
        asFigure=True, 
        kind='bar', 
        barmode='stack',
        x=['delivery__delivered_at'], 
        y=['counts'],
        theme='white',
        title='title',
        xTitle='date',
        yTitle='Numbre of deliverys',
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
def plot_delivery_count_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
    results = DeliveryDetail.objects.filter(
            product__in=selected_products,
            product__category__in=selected_categories,
            product__status__in=selected_status,
            delivery__delivered_at__gte=start_date,
            customer__in=selected_customers,
            delivery__delivered_at__lte=end_date)
    results = results.values('delivery__delivered_at','delivery','delivered_quantity')

    delivery_df = read_frame(results)

    delivery_df = delivery_df.groupby(
        by=['delivery__delivered_at'],
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index()

    figure = delivery_df.iplot(
        asFigure=True, 
        kind='bar', 
        barmode='stack',
        x=['delivery__delivered_at'], 
        y=['delivered_quantity'],
        theme='white', 
        title='title',
        xTitle='date',
        yTitle='Numbre of Products',
    )
    return figure


@app.callback(

    Output(figure_most_delivred_product_id, "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_delivery_product_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
    results = DeliveryDetail.objects.filter(
            product__in=selected_products,
            product__category__in=selected_categories,
            product__status__in=selected_status,
            delivery__delivered_at__gte=start_date,
            customer__in=selected_customers,
            delivery__delivered_at__lte=end_date)
    results = results.values('product','delivered_quantity')

    delivery_df = read_frame(results)
    
    print(delivery_df)
    
    delivery_df = delivery_df.groupby(
        by=['product'],
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index().sort_values(['delivered_quantity'],ascending=True)[:10]

    figure = delivery_df.iplot(
        asFigure=True, 
        kind='barh', 
        barmode='stack',
        x=['product'], 
        y=['delivered_quantity'],
        theme='white', 
        title='title',
        xTitle='date',
        yTitle='Most delivered  Products',
    )
    return figure

@app.callback(

    Output(figure_most_delivred_customer_id, "figure"),
    
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_delivery_custmoer_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
    
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__status__in=selected_status,
        delivery__delivered_at__gte=start_date,
        customer__in=selected_customers,
        delivery__delivered_at__lte=end_date)
    
    results = results.values('customer','delivered_quantity')

    delivery_df = read_frame(results)
    
    print(delivery_df)
    
    delivery_df = delivery_df.groupby(
        by=['customer'],
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index().sort_values(['delivered_quantity'],ascending=True)[:10]

    figure = delivery_df.iplot(
        asFigure=True, 
        kind='barh',
        barmode='stack',
        x=['customer'], 
        y=['delivered_quantity'],
        theme='white', 
        title='title',
        xTitle='date',
        yTitle='Most delivery Custmoers',
    )
    return figure

@app.callback(

    Output(figure_most_delivred_categories_id, "figure"),
    
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_customer_list_id, "value"),
        Input(dropdown_statut_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ]
)
def plot_most_delivery_categories_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
    
    results = DeliveryDetail.objects.filter(
        product__in=selected_products,
        product__category__in=selected_categories,
        product__status__in=selected_status,
        delivery__delivered_at__gte=start_date,
        customer__in=selected_customers,
        delivery__delivered_at__lte=end_date)
    
    results = results.values('product__category__reference','delivered_quantity')

    delivery_df = read_frame(results)
    
    print(delivery_df)
    
    delivery_df = delivery_df.groupby(
        by=['product__category__reference'],
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index().sort_values(['delivered_quantity'],ascending=True)[:10]

    figure = delivery_df.iplot(
        asFigure=True, 
        kind='barh',
        barmode='stack',
        x=['product__category__reference'], 
        y=['delivered_quantity'],
        theme='white', 
        title='title',
        xTitle='date',
        yTitle='Most 10 delivery categories',
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
def plot_pie_statuts_product_figure(selected_products,selected_categories,selected_customers,selected_status,start_date,end_date):
    results = DeliveryDetail.objects.filter(
            product__in=selected_products,
            product__category__in=selected_categories,
            product__status__in=selected_status,
            delivery__delivered_at__gte=start_date,
            customer__in=selected_customers,
            delivery__delivered_at__lte=end_date)
    results = results.values('product__status','delivered_quantity','product__category__reference')

    delivery_df = read_frame(results)
    
    deliveryd_category_df = read_frame(results)
        
    delivery_df = delivery_df.groupby(
        by=['product__status'],
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index().sort_values(['delivered_quantity'],ascending=True)
       
    deliveryd_category_df = deliveryd_category_df.groupby(
        by=['product__category__reference'],
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index().sort_values(['delivered_quantity'],ascending=True)
    
    figure = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    
    figure.add_trace(go.Pie(labels=delivery_df['product__status'], values=delivery_df['delivered_quantity'], name=""),1, 1)
    
    figure.add_trace(go.Pie(labels=deliveryd_category_df['product__category__reference'], values=deliveryd_category_df['delivered_quantity'], name=""),1, 2)
   
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
    app, dropdown_customer_list_id, div_customer_list_id, checkbox_customer_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

dash_utils.select_all_callbacks(
    app, dropdown_statut_list_id, div_statut_list_id, checkbox_statut_list_id)
