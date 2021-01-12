import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table


def generate_html_id(prefix, id_variable):
    ''' Add prefix to string and return a html id '''
    id_variable = id_variable.lower()
    generated_id = prefix + '-' + id_variable.replace('_', '-')
    return generated_id


def get_mini_card(data_value_id, title=None, data_value=None, subtitle=None, icon=None, dropdown_div=None, datatable_div=None):
    ''' Build div representing mini card '''
    # if datatable_id:
    #     datatable_div = dash_table.DataTable(id=datatable_id)
    # else:
    #     datatable_div = ''
    div = html.Div([
        dbc.Row([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        title,
                    ], sm=12, md=10, lg=10, className='font-weight-bold text-primary mb-1'),
                    dcc.Loading(
                        html.Div([
                            data_value,
                        ], id=data_value_id, className='font-weight-bold text-primary mb-1 float-right'),
                    ),
                ]),
                dcc.Loading(
                    html.Div([
                        subtitle,
                        html.Br(),
                        dropdown_div,
                        html.Br(),
                        datatable_div,
                    ],
                        # id=subtitle_id,
                        # className='text-primary'
                    ),
                )
            ], className='col mr-2'),
            html.Div([
                html.Div([
                ], className='fas {icon} fa-3x text-gray-300')
            ], className='col-auto')
        ]),
    ], className='card border-left-primary shadow card-body mb-4')
    return div

def get_chart_card(div_id, filter_div=None, footer_div=None):
    ''' Build div representing the chart card '''
    div = html.Div([
        html.Div([
            filter_div,
            dcc.Loading(
                dcc.Graph(id=div_id, config=dict(displaylogo=False, showLink=False, responsive=True, showTips=True)),
            ),
            footer_div,
        ], className='card-body')
    ], className='card shadow mb-4 py-3')
    return div

def get_datatable_card(div_id, style_data_conditional=None, **kwargs):
    ''' Build div representing the datatable card '''
    div = html.Div([
        html.Div([
            dcc.Loading(
                dash_table.DataTable(
                    id=div_id,
                    page_action='native',
                    filter_action='native',
                    sort_action='native',
                    sort_mode='multi',
                    page_size=20,
                    style_data_conditional=style_data_conditional,
                    # editable=editable,
                    **kwargs,
                    # style_data_conditional=[
                    # {
                    #     'if': {
                    #         'column_id': 'Region',
                    #     },
                    #     'backgroundColor': 'dodgerblue',
                    #     'color': 'white'
                    # },
                    # {
                    #     'if': {
                    #         'column_id': 'Pressure',

                    #         # since using .format, escape { with {{
                    #         'filter_query': '{{Pressure}} = {}'.format(df['Pressure'].max())
                    #     },
                    #     'backgroundColor': '#85144b',
                    #     'color': 'white'
                    # },
                    # {
                    #     'if': {
                    #         # comparing columns to each other
                    #         'filter_query': '{total_forecasted_quantity} < {total_ordered_quantity}',
                    #         'column_id': 'total_forecasted_quantity'
                    #     },
                    #     'backgroundColor': '#3D9970'
                    # },
                    # ]
                )
            )
        ], className='card-body')
    ], className='card shadow mb-4 py-3')

    return div

def get_dash_layout(filter_div, body_div):
    ''' Return the dashboard page with defined html elements separated into two parts, filter and body '''
    div = html.Div(
        [
            html.Div(
                [
                    html.Div([
                        filter_div,
                    ], className='card-body')
                ], className='card bg-light shadow mb-4 py-3'
            ),

            html.Div([
                body_div,
            ]),
        ], style={'background-color': '#f8f9fc'}
    )
    return div
