from django.shortcuts import get_object_or_404
from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
from . import ids
from .app import app
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from django.utils.translation import gettext as _
from django_pandas.io import read_frame

from django.db.models import F
import pandas as pd
import numpy as np

from account.models import CustomUser

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from .components import helpers
from .components import deployment_alg
import cufflinks as cf
from plotly.subplots import make_subplots


cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True


@app.callback(
    [
        Output(ids.DATATABLE_DEPLOYMENT, 'data'),
        Output(ids.DATATABLE_DEPLOYMENT, 'columns'),
        Output(ids.DATATABLE_TRUCK, 'data'),
        Output(ids.DATATABLE_TRUCK, 'columns'),
        Output(ids.MESSAGE_SUCCESS, 'is_open'),
        Output(ids.DIV_W_PIE_BY, 'hidden'),
        Output(ids.DIV_W_T_BY, 'hidden'),
    ],
    [
        Input(ids.BUTTON_RUN, 'n_clicks'),
        Input(ids.DROPDOWN_SHOW_BY, 'value'),
        Input(ids.INPUT_DATE_RANGE, 'start_date'),
        Input(ids.INPUT_DATE_RANGE, 'end_date'),
    ]
)
def return_deployment_datatable(run_n_clicks, show_by, start_date, end_date):
    if run_n_clicks is not None:
        version_id = 21
        truckavailability_df, truck_assignment_df = deployment_alg.run_deployment(
            version_id, show_by, start_date, end_date)
        # truckavailability_df.to_csv('tmp/truckavailability_df.csv')
        # truck_assignment_df.to_csv('tmp/truck_assignment_df.csv')

        # truckavailability_df = pd.read_csv('tmp/truckavailability_df.csv')
        # truck_assignment_df = pd.read_csv('tmp/truck_assignment_df.csv')

        # Return dataframe
        data_deployment = truck_assignment_df.to_dict('records')
        columns_deployment = [{"name": i, "id": i} for i in truck_assignment_df.columns]
        data_truck = truck_assignment_df.to_dict('records')
        columns_truck = [{"name": i, "id": i} for i in truck_assignment_df.columns]

        # Show success message
        is_open = True
        div_hidden = False

        return data_deployment, columns_deployment, data_truck, columns_truck, is_open, div_hidden, div_hidden
    
    
@app.callback(
    Output(ids.FIGURE_WAREHOUSES_ID, 'figure'),

    
    [
        Input(ids.BUTTON_RUN, 'n_clicks'),
        Input(ids.DROPDOWN_SHOW_BY, 'value'),
        Input(ids.INPUT_DATE_RANGE, 'start_date'),
        Input(ids.INPUT_DATE_RANGE, 'end_date'),
    ],
    [
        State(ids.DATATABLE_DEPLOYMENT, 'data'),
        State(ids.DATATABLE_TRUCK, 'data'),
    ]
)
def return_deployment_graph(run_n_clicks, show_by, start_date, end_date, data_deployment, data_truck):
    # if run_n_clicks is not None:
    # Get dataframe
    truckavailability_df = pd.read_csv('tmp/truckavailability_df.csv')
    truck_assignment_df = pd.read_csv('tmp/truck_assignment_df.csv')

    # truck_assignment_df = pd.DataFrame.from_dict(data_deployment)
    # truckavailability_df = pd.DataFrame.from_dict(data_truck)
    print('truck_assignment_df  ddd', truck_assignment_df)
    print('truckavailability_df  ddd', truckavailability_df)
    
    truckavailability_df['Total'] = truckavailability_df.apply(
        lambda
            row: 1 ,
        axis=1
    )
        
    truckavailability_df['Nubmer of used'] = truckavailability_df.apply(
        lambda
            row: 1 if row['status'] == 'full' or row['status'] == 'used' else 0,
        axis=1
    )
    


    truckavailability_df = truckavailability_df.groupby(
        by=['warehouse'],
        as_index=False
    ).agg({
        'Total':'sum',
        'Nubmer of used':'sum',
    })
    
    truckavailability_df['str name'] = truckavailability_df.apply(
        lambda
            row: str(row['warehouse']),
        axis=1
    )
    

    figure = truckavailability_df.iplot(
        asFigure=True,
        kind='bar',
        barmode='group',
        x=['str name'],
        y=[
            'Total',
            'Nubmer of used'
        ],
        colors= [
                'rgb(255, 230, 0)',
                'rgb(0, 200, 0)',
                'rgb(255, 132, 0)',
                'rgb(0,255,0)',
                'rgb(255, 0, 0)',
        ],
        theme='white',
        title=_('Number of Orders by Date'),
        xTitle=_('Ordered Date'),
        yTitle=_('Number of Orders'),
    )
    
    return figure


@app.callback(
    
    Output(ids.FIGURE_PIE_ID, 'figure'),
    [
        Input(ids.DROPDOWN_W_PIE_BY, 'value'),
        Input(ids.BUTTON_RUN, 'n_clicks'),
        Input(ids.DROPDOWN_SHOW_BY, 'value'),
        Input(ids.INPUT_DATE_RANGE, 'start_date'),
        Input(ids.INPUT_DATE_RANGE, 'end_date'),
    ]
)
def return_deployment_graph(warhouses,run_n_clicks, show_by, start_date, end_date):

    # truckavailability_df, truck_assignment_df = deployment_alg.run_deployment(
    #     show_by, start_date, end_date)
    # truckavailability_df.to_csv('tmp/truckavailability_df.csv')
    # truck_assignment_df.to_csv('tmp/truck_assignment_df.csv')
    
    if run_n_clicks is not None:
        truckavailability_df = pd.read_csv('tmp/truckavailability_df.csv')
        truck_assignment_df = pd.read_csv('tmp/truck_assignment_df.csv')
        
        newdf = truckavailability_df[truckavailability_df['warehouse'].isin(warhouses)]
        
        
        
        # newdf['freq'] = newdf.groupby('status')['status'].transform('count')
        
        newdf['freq'] = newdf.apply(
            lambda
                row: 1 ,
            axis=1
        )
        
        print(newdf)
        

        
        figure= make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
        
        figure.add_trace(
            go.Pie(
                labels=newdf['status'],
                values=newdf['freq'],
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
        figure.update_traces(hole=.4, hoverinfo="label+value+name")


    

    return figure


@app.callback(
    
    Output(ids.FIGURE_TOP_ID, 'figure'),
    [
        Input(ids.DROPDOWN_W_T_BY, 'value'),
        Input(ids.BUTTON_RUN, 'n_clicks'),
        Input(ids.DROPDOWN_SHOW_BY, 'value'),
        Input(ids.INPUT_DATE_RANGE, 'start_date'),
        Input(ids.INPUT_DATE_RANGE, 'end_date'),
    ]
)
def return_deployment_grapeh(warhouses,run_n_clicks, show_by, start_date, end_date):

    # truckavailability_df, truck_assignment_df = deployment_alg.run_deployment(
    #     show_by, start_date, end_date)
    # truckavailability_df.to_csv('tmp/truckavailability_df.csv')
    # truck_assignment_df.to_csv('tmp/truck_assignment_df.csv')
    
    
    

    truck_assignment_df = pd.read_csv('tmp/truck_assignment_df.csv')
    
    newdf = truck_assignment_df[truck_assignment_df['warehouse'].isin(warhouses)]
    
    if newdf.size!=0:
        newdf['Quantity'] = newdf.apply(
            lambda
                row:quantity(row),axis=1
        )

    
    if newdf.size!=0:
    
        newdf = newdf.groupby(
            by=['product'],
            as_index=False
        ).agg({
            'Quantity':'sum',
        })
    
    
    
        df = newdf.sort_values('Quantity',ascending = True).head(10)
    

    
        df['str prod'] = df.apply(
            lambda
                row: str(row['product']),
            axis=1
        )
        
        
        figure = df.iplot(
            asFigure=True,
            kind='barh',
            barmode='stack',
            x=['str prod'],
            y=['Quantity'],
            theme='white',
            title=_('Most 10 Products'),
            xTitle=_('Quantity'),
            yTitle=_('Product'),
        )
        return figure
    
    else :
        figure = newdf.iplot(
            asFigure=True,
            kind='barh',
            barmode='stack',
            x=None,
            y=None,
            theme='white',
            title=_('Most 10 Products'),
            xTitle=_('Quantity'),
            yTitle=_('Product'),
        )
        return figure
        



def quantity(row):
    try : 
        out = row['pallet_size']*row['deployed_quantity']        
    except   :
       out =  None  
    return out
                




