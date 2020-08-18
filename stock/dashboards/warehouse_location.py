import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
import datetime
from .. import utils
from ..models import Warehouse
import copy
from common.dashboards import dash_utils, dash_constants


# app = DjangoDash('StockValue', external_stylesheets=[dbc.themes.BOOTSTRAP])
app = DjangoDash('WarehouseLocation', add_bootstrap_links=True)

prefix = 'warehouse-location'
map_warehouse_location_id = prefix + '-warehosue-location'
map_view_selector_id = prefix + '-map-view-selector'



def filter_container():
    filter_container = html.Div([
        dbc.Row([
            dbc.Col([
                dcc.RadioItems(
                    id=map_view_selector_id,
                    options=[
                                # {"label": "basic", "value": "basic"},
                                # {"label": "satellite",
                                #  "value": "satellite"},
                                # {"label": "outdoors", "value": "outdoors"},
                                # {
                                #     "label": "satellite-street",
                                #     "value": "mapbox://styles/mapbox/satellite-streets-v9",
                                # },
                                ],
                    value="basic",
                ),
            ]),
        ]),
    ])
    return filter_container

def chart_container():
    chart_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_chart_card(map_warehouse_location_id)
            ]),
        ]),
    ])
    return chart_container

app.layout = dash_utils.get_dash_layout(filter_container(), chart_container())

@app.callback(
    Output(map_warehouse_location_id, "figure"),
    [
        Input(map_view_selector_id, 'value')
    ]
)
def update_well_map(style):
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
            zoom=8,
            style="mapbox://styles/abo007/ck90kt9zd0bk31ioa7g1v5z4v",
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
    qs = Warehouse.objects.get_warehouses()
    lat = list(qs.values_list('lat', flat=True))
    lon = list(qs.values_list('lon', flat=True))
    address = list(qs.values_list('address', flat=True))
    name = list(qs.values_list('name', flat=True))
    
    available_products = list(qs.values_list('available_products', flat=True))

    text_list = list(
        map(
            lambda prd, add, name: '<b>Reference:</b> ' + name +
            '<br><b>Available products:</b> ' + str(prd) +
            '<br><b>Address:</b> ' + add,
            available_products,
            address,
            name,
            
            # "Well ID:" + str(int(item)),
            # dff[dff["fm_name"] == formation]["RecordNumber"],
        )
    )
    chart_data = []
    # for data in qs:
    new_chart_data = go.Scattermapbox(
        mode="markers",
        lat=lat,
        lon=lon,
        name='warehouses',
        text=text_list,
        marker={"size": 10, 'color':'green'},
        textposition="bottom right"

        # marker={'size': 20, 'symbol': ["bus", "harbor", "airport"]},
        # text=["Bus", "Harbor", "airport"],
    )


    # data = go.Scattermapbox(
    #     lat=['37.497562'],
    #     lon=['-82.755728'],
    #     mode="markers",
    #     # marker={"color": colormap[formation], "size": 9},
    #     text=['text'],
    #     name=['name'],
    #     # selectedpoints=selected_index,
    #     # customdata='cust data',
    # )
    chart_data.append(new_chart_data)
    return {"data": chart_data, "layout": layout}

