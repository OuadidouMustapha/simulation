# Import required libraries
import copy
import datetime as dt
import math
import pathlib
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
from inventory.models import Location, StockCheck,Operation
from plotly import offline
from stock.models import Product,ProductCategory
from dash.exceptions import PreventUpdate
from django.db.models import Sum
import cufflinks as cf

cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True
app = DjangoDash('StockImage',add_bootstrap_links=True)
_prefix = 'inventory'


#--------------------------------------------Dropdown  list -------------------------------------
dropdown_product_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_product_list_id')
dropdown_type_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_type_list_id')
dropdown_location_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_location_list_id')
dropdown_reference_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_reference_list_id')
dropdown_categorie_list_id = dash_utils.generate_html_id(_prefix, 'dropdown_categorie_list_id')


#--------------------------------------------Div list -------------------------------------------
div_product_list_id = dash_utils.generate_html_id(_prefix, 'div_product_list_id')
div_location_list_id = dash_utils.generate_html_id(_prefix, 'div_location_list_id')
div_reference_list_id = dash_utils.generate_html_id(_prefix, 'div_reference_list_id')
div_categorie_list_id = dash_utils.generate_html_id(_prefix, 'div_categorie_list_id')


#--------------------------------------------Checkbox list --------------------------------------
checkbox_product_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_product_list_id')
checkbox_categorie_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_categorie_list_id')
checkbox_reference_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_reference_list_id')
checkbox_location_list_id = dash_utils.generate_html_id(_prefix, 'checkbox_location_list_id')

#------------------------------------------------------------------------------------------------

input_date_range_id = dash_utils.generate_html_id(_prefix, 'input_date_range_id')



_all_products     = list(Product.objects.get_all_products())
_all_locations    = list(Location.objects.get_all_locations())
_all_categories   = list(ProductCategory.objects.get_all_productcategory())
_all_stock_checks = list(StockCheck.objects.get_all_stock_checks)



def filter_container():
    filter_container = html.Div([
        dbc.Row([
                dbc.Col([
                    dash_utils.get_filter_dropdown(
                        dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id, _all_categories, '')
                ], sm=12, md=6, lg=4),
                dbc.Col([
                    dash_utils.get_filter_dropdown(
                        dropdown_product_list_id, div_product_list_id, checkbox_product_list_id, _all_products, '')
                ], sm=12, md=6, lg=4),
                dbc.Col([
                    dash_utils.get_filter_dropdown(
                        dropdown_location_list_id, div_location_list_id, checkbox_location_list_id, _all_locations, '')
                ], sm=12, md=6, lg=4),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label(_('Groupe By')),
                dcc.Dropdown(
                    id= dropdown_type_list_id,
                    options=[
                        {'label': 'Location', 'value': 'Location'},
                        {'label': 'Product', 'value': 'Product'},
                        {'label': 'Categorie', 'value': 'Categorie'},
                        {'label': 'Location - Product', 'value': 'Location-Product'},
                    ],
                    value='Location-Product',
                ),
            ], sm=12, md=6, lg=4 ),

            dbc.Col([
                dash_utils.get_date_range(
                    input_date_range_id,
                    label=_('Time horizon'),
                    year_range=1
                ),
            ], sm=12, md=12, lg=12,style = {'display': 'block', 'cursor': 'pointer', 'margin-top':'20px' }),

            dbc.Col([
                dbc.Label(_('Date'),style = {'margin-top':'20px' },),
                dash_utils.get_filter_dropdown(
                    dropdown_reference_list_id, div_reference_list_id, checkbox_reference_list_id, _all_stock_checks,'',select_all=False,)
            ], sm=12, md=6, lg=4),
        ])
    ])
    return filter_container


layout = dict(
    autosize=True,
    automargin=True,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
)


def body_container():
    body_container = html.Div(
        [
            dcc.Store(id="aggregate_data_id"),
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="aggregate_graph")],
                        className="",
                    ),
                ],
                className="shadow-lg p-2 mb-5 bg-white rounded",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )
    return body_container


app.layout = dash_utils.get_dash_layout(filter_container(), body_container())


@app.callback(
    Output("aggregate_graph", "figure"),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_location_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_type_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
        Input(dropdown_reference_list_id, 'value'),
    ],
)
def make_aggregate_figure(selected_products, selected_locations,selected_categories,groupe_by,start_date,end_date,dates):

    layout_aggregate = copy.deepcopy(layout)

    data = []


    if(groupe_by=='Categorie') : 

        
        results = StockCheck.objects.filter(Q(location__in=selected_locations)&Q(product__in=selected_products)&Q(check_date__gte=start_date)&Q(check_date__lte=end_date)).values('product__category','check_date').order_by('product__category','check_date').annotate(sum=Sum('quantity'))
        for stock in results:
            print(stock)
        cats =_all_categories.copy()
        for cat in _all_categories :
            if cat['value'] in selected_categories:
                pass
            else :
                cats.remove(cat)
        for cat in cats :
            x = []
            y = []
            for target in results :
                if(cat['value'] == target['product__category']) :
                    x.append(target['check_date'])
                    y.append(target['sum'])
            data.append(
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name= 'Location : '+cat['label'] ,
                    x=x,
                    y=y,
                    line=dict(shape="spline", smoothing="2"),
                    marker=dict(symbol="diamond-open"),
                ),
            )
    elif(groupe_by=='Location') : 

        results = StockCheck.objects.filter(Q(location__in=selected_locations)&Q(product__in=selected_products)&Q(product__category__in=selected_categories)&Q(product__in=selected_products)&Q(product__category__in=selected_categories)&Q(check_date__gte=start_date)&Q(check_date__lte=end_date)).values('location','check_date').order_by('location','check_date').annotate(sum=Sum('quantity'))
       
        locs =_all_locations.copy()
        for loc in _all_locations:
            if loc['value'] in selected_locations:
                pass
            else :
                locs.remove(loc)
        for location in locs:
            x = []
            y = []
            for target in results :
                if(location['value'] == target['location']) : 
                    x.append(target['check_date'])
                    y.append(target['sum'])
            data.append(
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name= 'Location : ' + location['label'],
                    x=x,
                    y=y,
                    line=dict(shape="spline", smoothing="2"),
                    marker=dict(symbol="diamond-open"),
                ),
            )
                #---------------------------------------------------------------------{calcule stock}-----------------------------------------------------------
        
        #------------------------------------------------------{start calcule image stock } ------------------------------------------------------------------
        
        if selected_references:
            stock_images = StockCheck.objects.all().filter(Q(id__in=selected_references)).order_by('check_date')

        
            
            for stock_image in stock_images:
                range_futur_date = []
                range_past_date = []

                range_futur_date = pd.date_range(stock_image.check_date, end_date)
                range_past_date  = pd.date_range(start_date,stock_image.check_date)
                range_past_date  = range_past_date.sort_values(ascending=False)

                x_date     = []
                y_quantity = []

                x_date.append(stock_image.check_date)
                y_quantity.append(stock_image.quantity)
        
                #-------------------------------------------------future-------------------------------------------------------------------------
                if(len(df)!=0):
                    df = df[(df.product_id == stock_image .product.id)&((df.location_in_id==stock_image .location.id )|(df.location_out_id==stock_image.location.id ))]

                    for date in range_futur_date :
                        x_date.append(date)
                        y_quantity.append(y_quantity[-1])

                        newDf = df[(df.operation_date==date)]

                        if(len(newDf)!=0):
                            for index, row in newDf.iterrows():
                                if(row['location_in_id']==stock_image.location.id ) : 
                                    y_quantity[-1] = y_quantity[-1]+row['quantity']
                                elif(row['location_in_id']==stock_image.location.id & row['location_out_id'] == stock_image.location.id):
                                    pass
                                else : 
                                    y_quantity[-1] = y_quantity[-1]-row['quantity']

                #----------------------------------------------past-----------------------------------------------------------------------------------
                x_past_date = []
                y_past_quantity = []
                x_past_date.append(stock_image.check_date)
                y_past_quantity.append(stock_image.quantity)

                if(len(df)!=0):
                    df = df[(df.product_id == results[1].product.id)&((df.location_in_id==results[1].location.id )|(df.location_out_id==results[1].location.id ))]

                    for date in range_past_date[1::] :
                        x_past_date.append(date)
                        y_past_quantity.append(y_past_quantity[-1])

                        newDf = df[(df.operation_date==date)]

                        if(len(newDf)!=0):
                            for index, row in newDf.iterrows():
                                if(row['location_in_id']==results[1].location.id ) : 
                                    y_past_quantity[-1] = y_past_quantity[-1]-row['quantity']
                                elif(row['location_in_id']==results[1].location.id & row['location_out_id'] == results[1].location.id):
                                    y_past_quantity[-1] =y_past_quantity[-1]
                                else : 
                                    y_past_quantity[-1] =y_past_quantity[-1]+row['quantity']
                    # for operation in operations :

                    #     print(operation.location_in)
                    #     print(operation.location_out)
                    #     print(results[0].location)
                    #     print(results[0].product)
                    #     print(int(date.strftime('%Y%m%d')) == int(operation.operation_date.strftime('%Y%m%d')))
                    #     print(operation.product.id == results[0].product.id )
                    #     print('-----------------------------------------------------------------------------')
                    #     if( int(date.strftime('%Y%m%d')) == int(operation.operation_date.strftime('%Y%m%d')) and operation.product.id == results[0].product.id ):
                    #         print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                    #         print(operation)
                    #         if(operation.location_in.id==results[0].location.id ) : 
                    #             y_quantity[-1] = y_quantity[-1]+operation.quantity
                    #         elif(operation.location_in.id==results[0].location.id & operation.location_out.id == results[0].location.id):
                    #             pass
                    #         else : 
                    #             y_quantity[-1] = y_quantity[-1]-operation.quantity
                
        
                #-------------------------------------------------------- Plot -------------------------------------------------------------
                x_total = []
                y_total = []
                x_total =x_past_date[::-1]
                x_total.extend(x_date[2::])
                y_total = y_past_quantity[::-1]

                y_total.extend(y_quantity[2::])
                
                print(selected_references)
                data.append(
                    dict(
                        type="bar",
                        mode="lines+markers",
                        name= 'product '+stock_image.product.reference +'in '+stock_image.location.reference ,
                        x=x_total,
                        y=y_total,
                        line=dict(shape="spline", smoothing="2"),
                        marker=dict(symbol="diamond-open"),
                    ),
                )      
        
        #---------------------------------------------------------------------{end calcul stock}---------------------------------------------------------
    elif (groupe_by=='Product') :

        results = StockCheck.objects.filter(Q(location__in=selected_locations)&Q(product__in=selected_products)&Q(product__category__in=selected_categories)&Q(check_date__gte=start_date)&Q(check_date__lte=end_date)).values('product','check_date').order_by('product','check_date').annotate(sum=Sum('quantity'))
        
        prods =_all_products.copy()
        for prod in _all_products:
            if prod['value'] in selected_products:
                pass
            else :
                prods.remove(prod)
        for prod in prods:
            x = []
            y = []
            for target in results :
                if(prod['value'] == target['product']) : 
                    x.append(target['check_date'])
                    y.append(target['sum'])
            data.append(
                dict(
                    type="scatter",
                    mode="lines+markers",
                    name= 'Product : ' + prod['label'],
                    x=x,
                    y=y,
                    line=dict(shape="spline", smoothing="2"),
                    marker=dict(symbol="diamond-open"),
                ),
            )

    else :  

        if selected_categories and selected_products and selected_locations:

            print(selected_categories,selected_products,selected_locations)


            results = StockCheck.objects.filter(
                product__in=selected_products,
                location__in=selected_locations,
                product__category__in=selected_categories,
                check_date__gte=start_date,
                check_date__lte=end_date
            )

            print(results)
            operations = Operation.objects.all().filter(Q(product__in=selected_products)&Q(location__in=selected_locations)&Q(product__category__in=selected_categories)&Q(operation_date__gte=start_date)&Q(operation_date__lte=end_date)).values('operation_date','location','product').order_by('operation_date')

            print(operations)
            df = pd.DataFrame(list(operations.values()))

        #------------------------------{test}------------------------------------


        #---------------------------------------------------------------------{calcule stock}-----------------------------------------------------------

            if dates:
                stock_images = StockCheck.objects.all().filter(Q(check_date__in=dates)).order_by('check_date')

                for stock_image in stock_images:
                    range_futur_date = []
                    range_past_date = []

                    range_futur_date = pd.date_range(stock_image.check_date, end_date)
                    range_past_date  = pd.date_range(start_date,stock_image.check_date)
                    range_past_date  = range_past_date.sort_values(ascending=False)

                    x_date     = []
                    y_quantity = []

                    x_date.append(stock_image.check_date)
                    y_quantity.append(stock_image.quantity)
            
                    #-------------------------------------------------future-------------------------------------------------------------------------
                    if(len(df)!=0):
                        df_future = df[(df.product_id == stock_image .product.id)&((df.location_id==stock_image .location.id )|(df.location_id==stock_image.location.id ))]

                        for date in range_futur_date :
                            x_date.append(date)
                            y_quantity.append(y_quantity[-1])

                            newDf = df_future[(df_future.operation_date==date)]

                            if(len(newDf)!=0):
                                for index, row in newDf.iterrows():
                                    if(row['location_in_id']==stock_image.location.id ) : 
                                        y_quantity[-1] = y_quantity[-1]+row['quantity']
                                    elif(row['location_in_id']==stock_image.location.id & row['location_out_id'] == stock_image.location.id):
                                        pass
                                    else : 
                                        y_quantity[-1] = y_quantity[-1]-row['quantity']

                    #----------------------------------------------past-----------------------------------------------------------------------------------
                    x_past_date = []
                    y_past_quantity = []
                    x_past_date.append(stock_image.check_date)
                    y_past_quantity.append(stock_image.quantity)

                if(len(df)!=0):
                    df_past= df[(df.product_id == results[1].product.id)&((df.location_in_id==results[1].location.id )|(df.location_out_id==results[1].location.id ))]

                    for date in range_past_date[1::] :
                        x_past_date.append(date)
                        y_past_quantity.append(y_past_quantity[-1])

                        newDf = df_past[(df_past.operation_date==date)]

                        if(len(newDf)!=0):
                            for index, row in newDf.iterrows():
                                if(row['location_in_id']==results[1].location.id ) : 
                                    y_past_quantity[-1] = y_past_quantity[-1]-row['quantity']
                                elif(row['location_in_id']==results[1].location.id & row['location_out_id'] == results[1].location.id):
                                    y_past_quantity[-1] =y_past_quantity[-1]
                                else : 
                                    y_past_quantity[-1] =y_past_quantity[-1]+row['quantity']
                    # for operation in operations :

                    #     print(operation.location_in)
                    #     print(operation.location_out)
                    #     print(results[0].location)
                    #     print(results[0].product)
                    #     print(int(date.strftime('%Y%m%d')) == int(operation.operation_date.strftime('%Y%m%d')))
                    #     print(operation.product.id == results[0].product.id )
                    #     print('-----------------------------------------------------------------------------')
                    #     if( int(date.strftime('%Y%m%d')) == int(operation.operation_date.strftime('%Y%m%d')) and operation.product.id == results[0].product.id ):
                    #         print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                    #         print(operation)
                    #         if(operation.location_in.id==results[0].location.id ) : 
                    #             y_quantity[-1] = y_quantity[-1]+operation.quantity
                    #         elif(operation.location_in.id==results[0].location.id & operation.location_out.id == results[0].location.id):
                    #             pass
                    #         else : 
                    #             y_quantity[-1] = y_quantity[-1]-operation.quantity
                
        
                #-------------------------------------------------------- Plot -------------------------------------------------------------
                x_total = []
                y_total = []
                x_total =x_past_date[::-1]
                x_total.extend(x_date[2::])
                y_total = y_past_quantity[::-1]

                y_total.extend(y_quantity[2::])
                data.append(
                    dict(
                        type="scatter",
                        mode="lines+markers",
                        name= 'product '+stock_image.product.reference +'in '+stock_image.location.reference ,
                        x=x_total,
                        y=y_total,
                        line=dict(shape="spline", smoothing="2"),
                        marker=dict(symbol="diamond-open"),
                    ),
                )      
        
        #---------------------------------------------------------------------{end calcul stock}---------------------------------------------------------
        

            if len(results)!=0:

                prods = []
                for target in results : 
                    prods.append(target.product) if target.product not in prods else prods
                locs = []
                for target in results : 
                    locs.append(target.location) if target.location not in locs else locs
                for location in locs :
                    for product in prods:
                        x= []
                        y= []
                        for target in results :
                            if(target.product == product and target.location == location ):
                                x.append(target.check_date)
                                y.append(target.quantity)
                        data.append(
                            dict(
                                type="scatter",
                                mode="lines+markers",
                                name='(Prouduit : ' + product.reference +' -in '+ 'Location : ' + location.reference+')',
                                x=x,
                                y=y,
                                line=dict(shape="spline", smoothing="2"),
                                marker=dict(symbol="diamond-open"),
                            ),
                        )  
    layout_aggregate["title"] = "Stock-Image"
    return {
        'data': data,
        'layout':layout_aggregate
    }
# @app.callback(
#     dash.dependencies.Output(dropdown_categorie_list_id, "options"),
#     [dash.dependencies.Input(dropdown_categorie_list_id, "search_value")],
#     [dash.dependencies.State(dropdown_categorie_list_id, "value")],
# )
# def update_multi_cat_options(search_value, value):
#     if not search_value:
#         raise PreventUpdate
#     # Make sure that the set values are in the option list, else they will disappear
#     # from the shown select list, but still part of the `value`.
#     return [
#         o for o in _all_categories if search_value in o["label"] or o["value"] in (value or [])
#     ]


# @app.callback(
#     Output(dropdown_product_list_id, 'options'),
#     [Input(dropdown_categorie_list_id, 'value')])
# def set_cats_options(selected_categories):

#     products = Product.objects.all().filter(category_id__in=selected_categories)

#     if products :
         
#         return [{'label':product.reference , 'value': product.id } for product in products]
#     else :
#         return [{'label': '', 'value': '' }]


@app.callback(
    Output(dropdown_reference_list_id, 'options'),
    [
        Input(dropdown_product_list_id, "value"),
        Input(dropdown_location_list_id, "value"),
        Input(dropdown_categorie_list_id, "value"),
        Input(dropdown_reference_list_id, "value"),
        Input(dropdown_type_list_id, "value"),
        Input(input_date_range_id, 'start_date'),
        Input(input_date_range_id, 'end_date'),
    ])
def set_stock_images_reference_options(selected_products, selected_locations,selected_categories,selected_references,groupe_by,start_date,end_date):
    if groupe_by == 'Location-Product':
        # stock_images = StockCheck.objects.all().filter(Q(product__in=selected_products)&Q(location__in=selected_locations)&Q(product__category__in=selected_categories)&Q(check_date__gte=start_date)&Q(check_date__lte=end_date)).values('check_date').order_by('check_date')
        # if len(stock_images)!=0 :
        #     return [{'label':str(stock_image['check_date']) , 'value': stock_image['check_date'] } for stock_image in stock_images]
        # else :
        #     return [{'label':'--' , 'value': '--' }]
        pass
            
    elif groupe_by == 'Location' :
        stock_images = StockCheck.objects.filter(Q(location__in=selected_locations)&Q(product__in=selected_products)&Q(product__category__in=selected_categories)&Q(check_date__gte=start_date)&Q(check_date__lte=end_date)).values('location__reference','location__id','check_date').order_by('location','check_date').annotate(sum=Sum('quantity'))
        return [{'label':str(stock_image['location__reference'])+'--at--'+str(stock_image['check_date']) , 'value': stock_image['location__reference'] } for stock_image in stock_images]
# @app.callback(
#     Output(dropdown_categorie_list_id, 'options'),
#     [Input(dropdown_product_list_id, 'value')])
# def set_product_options(selected_products):

#     if(selected_products):
#         products = Product.objects.all().filter(id__in=selected_products)
    
#     else : 
#         products = Product.objects.all()
#     categories = []
#     for p in products : 
#         categories.append(p.category) if p.category not in categories else categories
#     return [{'label':category.reference , 'value': category.id } for category in categories]


# dash_utils.select_all_callbacks(
#     app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)

# dash_utils.select_all_callbacks(
#     app, dropdown_location_list_id, div_location_list_id, checkbox_location_list_id)

# dash_utils.select_all_callbacks(
#     app, dropdown_categorie_list_id, div_categorie_list_id, checkbox_categorie_list_id)

# dash_utils.select_all_callbacks(
#     app, dropdown_reference_list_id, div_reference_list_id, checkbox_reference_list_id)
            