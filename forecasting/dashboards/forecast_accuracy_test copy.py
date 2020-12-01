import copy
import datetime

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
import cufflinks as cf
# cf.go_offline()
cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True



from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from django_pandas.io import read_frame
from django_plotly_dash import DjangoDash

from common import utils as common_utils
from common.dashboards import dash_constants, dash_utils

import base64
import io

app = DjangoDash('ForecastAccuracyTest', add_bootstrap_links=True)

genr_l = pd.DataFrame({"Genre": range(5), "value": range(5, 10)})



app.layout = html.Div([
    html.Div([
        html.Div([
            html.Button('Select All', id='all-button-genre', className='all-button')
        ]),
        html.Div([
            html.Button('Select None', id='none-button-genre', className='none-button')
        ]),
    ], className="multi-filter"),
    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity-genre',
            columns=[
                {"name": 'Genre', "id": 'value'}
            ],
            data=genr_l.to_dict('records'), #table that I defined at start
            # n_fixed_rows=1,
            # filtering=True,
            row_selectable="multi",
            virtualization=True,
            # pagination_mode=False,
            style_table={
                'minHeight': '200px',
                'maxHeight': '200px',
            },
            css=[{
                'selector': '.dash-cell div.dash-cell-value',
                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
            }],
            style_header={
                'backgroundColor': 'green',
                'color': 'white',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'textAlign': 'center',
            },
            style_cell={
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
                'textAlign': 'left',
            },
            style_cell_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(232, 232, 232)'
                }
            ],
            style_as_list_view=True,
        ),
    ], className='individual-filter')
])
        


@app.callback(
    [
    Output('datatable-interactivity-genre', "selected_rows"),
    ],
    [
    Input('all-button-genre', 'n_clicks'),
    Input('none-button-genre', 'n_clicks'),
    ],
    [
    State('datatable-interactivity-genre', "derived_virtual_data"),
    ]
)
def select_all_genre(all_clicks,none_clicks, selected_rows):
    if selected_rows is None:
        return [[]]
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]


    
    if button_id == 'all-button-genre':
        return [[i for i in range(len(selected_rows))]]
    else:
        return [[]]

@app.callback(
    Output('intermediate-value', 'children'),
    [
    Input('refresh-button', 'n_clicks'),
    Input('interval-component', 'n_intervals')
    ],
    [
    State('datatable-interactivity-genre', "derived_virtual_data"),
    State('datatable-interactivity-genre', "derived_virtual_selected_rows"),
    ]
)
def clean_data(n_clicks,n, genre_rows, genre_selected_rows):

    df = pd.read_pickle('table.pkl')

    ############
    # filtering
    if genre_selected_rows is not None and genre_selected_rows != []:
        df = df[df['genre'].isin([genre_rows[i]['value'] for i in genre_selected_rows])]
    

    ############
    

    datasets = {
        'df': df.to_json(orient='split')
    }

    return json.dumps(datasets)




