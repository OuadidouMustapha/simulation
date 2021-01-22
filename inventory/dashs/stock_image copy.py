# Import required libraries
import pickle
import copy
import pathlib
import urllib.request
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from stock.models import Product 
from inventory.models import Location,StockCheck
import plotly.graph_objs as go
from plotly import offline
import pandas as pd
from django.db.models import Q
from django_plotly_dash import DjangoDash
import dash_table



app = DjangoDash('StockImage')
# Create global chart template



app = DjangoDash('StockImage')
# Create global chart template



#-----------------------------------------------------------------


stock_images = StockCheck.objects.all()

stocks = []
#return the important attributes
for stock in stock_images:
    stocks.append([stock.id,stock.quantity,stock.product.reference,stock.location.id,stock.check_date])
#create a dataframe
stocks = pd.DataFrame(stocks,columns=['id','quantity','product_reference','location_id','check_date'])

df = stocks.copy()

df.set_index('id', inplace=True, drop=False)



#-----------------------------------------------------------------
products  = Product.objects.all()
locations = Location.objects.all()

product_options = [
    {"label": target.reference, "value": target.id }
    for target in products
]

location_options = [
    {"label": target.reference, "value": target.id }
    for target in locations
]

layout = dict(
    autosize=True,
    automargin=True,
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
)

# Create app layout
app.layout = html.Div([
    html.Div(
        [
            dcc.Store(id="aggregate_data_id"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="products",
                                options=product_options,
                                multi=True,
                                value=[target.id for target in products],
                                className="dcc_control",
                            ),
                            dcc.Dropdown(
                                id="locations",
                                options=location_options,
                                multi=True,
                                value=[target.id for target in locations],
                                className="dcc_control",
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),

                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="aggregate_graph")],
                        className="pretty_container five columns",
                    ),
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    ),
])

def filter_dataframe(df, products, locations):
    dff = df[
        df["product_reference"].isin(products)
        & df["location_id"].isin(locations)
    ]
    return dff

@app.callback(
    Output("aggregate_graph", "figure"),
    [
        Input("products", "value"),
        Input("locations", "value"),
    ],
)
def make_aggregate_figure(products, locations):

    layout_aggregate = copy.deepcopy(layout)

    all_products  = Product.objects.all()

    all_locations = Location.objects.all()

    data = []

    print('a'+str(len(all_locations)))

    if products is None and locations!=None :
        targets = StockCheck.objects.all().filter(Q(location__in=locations))
        prods = []
        for target in targets : 
            prods.append(target.product) if target.product not in prods else prods

        locs = []
        for target in targets : 
            locs.append(target.location) if target.location not in locs else locs


        print('desert 1 '+str(len(locs))+str(len(prods)))
        for product in prods :
            for location in locs:
                x= []
                y= []

                for target in targets :

                    if(target.product == product and target.location == location ):
                        x.append(target.check_date)
                        y.append(target.quantity)


                data.append(
                    go.Bar(x=x,y=x,name = 'p' + str(product) + 's'+str(location)),
                )
    elif locations is None and products!=None :
        targets = StockCheck.objects.all().filter(Q(product__in=products))
        prods = []
        for target in targets : 
            prods.append(target.product) if target.product not in prods else prods

        locs = []
        for target in targets : 
            locs.append(target.location) if target.location not in locs else locs


        print('desert 2 '+str(len(locs))+str(len(prods)))

        for location in locs :
            for product in prods:
                x = []
                y = []
                for target in targets :

                    if(target.product == product and target.location == location ):
                        x.append(target.check_date)
                        y.append(target.quantity)


                data.append(
                    go.Bar(x=x,y=x,name = 'p' + str(product) + 's'+str(location)),
                )
    elif locations!=None and products!=None : 
        targets = StockCheck.objects.all().filter(Q(product__in=products)&Q(location__in=locations))

        prods = []
        for target in targets : 
            prods.append(target.product) if target.product not in prods else prods

        locs = []
        for target in targets : 
            locs.append(target.location) if target.location not in locs else locs


        for location in locs :
            for product in prods:

                x= []
                y= []

                for target in targets :

                    if(target.product == product and target.location == location ):
                        x.append(target.check_date)
                        y.append(target.quantity)


                data.append(
                    go.Bar(x=x,y=x,name = 'p' + str(product) + 's'+str(location)),
                )
    else :
        targets = StockCheck.objects.all()

        prods = []
        for target in targets : 
            prods.append(target.product) if target.product not in prods else prods

        locs = []
        for target in targets : 
            locs.append(target.location) if target.location not in locs else locs


        print('desert 4 '+str(len(locs))+str(len(prods)))

        for location in locs:
            for product in prods:
                x= []
                y= []

                for target in targets :

                    if(target.product == product and target.location == location ):
                        x.append(target.check_date)
                        y.append(target.quantity)


                data.append(
                    go.Bar(x=x,y=x,name = 'p' + str(product) + 's'+str(location)),
                )

    # if products is None and locations is None:
    #     dff = df
    #     # pandas Series works enough like a list for this to be OK
    # else:
    #     dff = filter_dataframe(df,products,locations)
    # data = []

    all_products  = Product.objects.all()
    # all_locations = Location.objects.all()
    # if products is None and locations!=None:
    #     for location in locations:
    #         for product in all_products:
                
    #             data.append(
    #                 [
    #                     dict(
    #                         type="scatter",
    #                         mode="lines",
    #                         name="Gas Produced (mcf)",
    #                         x= dff["sold_at"],
    #                         y= dff[column],
    #                         line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
    #                     )
    #                  for column in ["quantity"] if column in dff ])

    layout_aggregate["title"] = "Aggregate: "

    return {
        'data': data,
        'layout':layout_aggregate
    }
            