import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from django_plotly_dash import DjangoDash
import dash_table


app = DjangoDash('StockImage')


# app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True

DF_GAPMINDER = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv'
)
DF_GAPMINDER = DF_GAPMINDER[DF_GAPMINDER['year'] == 2007]
DF_GAPMINDER.loc[0:20]

DF_SIMPLE = pd.DataFrame({
    'x': ['A', 'B', 'C', 'D', 'E', 'F'],
    'y': [4, 3, 1, 2, 3, 6],
    'z': ['a', 'b', 'c', 'a', 'b', 'c']
})


dataframes = {'DF_GAPMINDER': DF_GAPMINDER,
              'DF_SIMPLE': DF_SIMPLE}


def get_data_object(user_selection):
    """
    For user selections, return the relevant in-memory data frame.
    """
    return dataframes[user_selection]
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

app.layout = html.Div([
    html.H4('DataTable'),
    html.Label('Report type:', style={'font-weight': 'bold'}),

    html.Div([
        dcc.Input(
            id='adding-rows-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10},
        ),
        html.Button('Add Column', id='adding-c-button', n_clicks=0)
    ], style={'height': 50}),



     dash_table.DataTable(
         id='adding-rows-table',
         columns=[{"name": i, "id": i} for i in df.columns],
         data = df.to_dict('rows'),
         row_selectable="multi",
         row_deletable=True,
         selected_rows=[],
         style_cell_conditional=[
         {
             'if': {'row_index': 'odd'},
             'backgroundColor': 'rgb(230, 255, 230)'
         }
     ] + [
         {
             'if': {'column_id': c},
             'textAlign': 'left'
        } for c in ['Date', 'Region']
    ],
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold'
    }
    ),

    html.Button('Add Row', id='editing-rows-button', n_clicks=0),
    html.Button('Button 1', id='all-button', n_clicks=0),
    dcc.Dropdown(
        id='field-dropdown',
        options=[{'label': df, 'value': df} for df in dataframes],
        value='DF_GAPMINDER',
        clearable=False
    ),
        dash_table.DataTable(

            id='datatable-interactivity-channel',

            columns=[{"name": i, "id": i} for i in df.columns],
            row_selectable='multi',
            sort_action='native',
            # editable=True,
            row_deletable=True,
            # rows=[{}],
            selected_rows=[],

            css=[{'selector': 'tr:hover',
            'rule': 'background-color:  #80FF80',
                # 'font-family': 'Times New Roman',

                        }]),
    html.Div(id='hidden-div', style={'display': 'none'}),

    html.Div(id='selected-indexes')
], className='container')

@app.callback(
    Output('adding-rows-table', 'selected_rows'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('adding-rows-table', 'data'),
     State('adding-rows-table', 'columns')])
def add_row(n_clicks, rows, columns):
    index=[]
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})

        print(rows)

        index = []

        for i in range(0,len(rows)):
            index.append(i)
    return index

@app.callback(
    Output('adding-rows-table', 'columns'),
    [Input('adding-rows-table', 'selected_rows'),
    Input('editing-c-button', 'n_clicks')],)
def update_columns(selected_rows,n_clicks):
    if n_clicks > 0:
        print(selected_rows)
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
