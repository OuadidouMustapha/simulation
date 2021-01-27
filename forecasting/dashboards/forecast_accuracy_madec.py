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
from django.db.models import OuterRef
from django_pandas.io import read_frame
from django_plotly_dash import DjangoDash

from common import utils as common_utils
from common.dashboards import dash_constants, dash_utils
from ..models import Forecast

import base64
import io


app = DjangoDash('ForecastAccuracyMadec', add_bootstrap_links=True)

### Used IDs ###
prefix = 'stock-forecast-accuracy-madec-'
# Filter IDs
dropdown_group_by_product_field_id = prefix + '-dropdown-group-by-product-field'
dropdown_group_by_distribution_field_id = prefix + '-dropdown-group-by-distribution-field'
dropdown_kind_id = prefix + '-dropdown-kind'
dropdown_show_by_id = prefix + '-dropdown-show-by'
input_date_range_id = prefix + '-input-date-range'
dropdown_forecast_version_id = prefix + '-dropdown-forecast-version'
# Mini-cards IDs
mini_card_subtitle_bias_percent_id = prefix + 'mini-card-subtitle-bias-percent'
mini_card_subtitle_mad_id = prefix + 'mini-card-subtitle-mad'
mini_card_subtitle_mape_id = prefix + 'mini-card-subtitle-mape'
# Charts IDs
chart_by_date_by_group_id = prefix + 'chart-by-date-by-group'
chart_dropdown_y_axis_id = prefix + 'chart-filter-y-axis'
chart_by_group_id = prefix + 'chart-by-group'
madec_chart1_id = prefix + 'chart1'
madec_chart2_id = prefix + 'chart2'
madec_chart3_id = prefix + 'chart3'
madec_chart4_id = prefix + 'chart4'
madec_chart5_id = prefix + 'chart5'
madec_chart6_id = prefix + 'chart6'
madec_chart7_id = prefix + 'chart7'
madec_chart8_id = prefix + 'chart8'
# Dataframe ID
table_forecast_dataframe_id = prefix + '-table-forecast-dataframe'
# Fiel upload
file_upload_id = prefix + '-file-upload'
datatable_data_upload_id = prefix + '-datatable-data-upload'

# filter
dropdown_warehouse_list_id = prefix + '-dropdown-warehouse-list'
dropdown_product_list_id = prefix + '-dropdown-product-list'
dropdown_circuit_list_id = prefix + '-dropdown-circuit-list'
dropdown_product_range_list_id = prefix + '-dropdown-product-range-list'
div_warehouse_list_id = prefix + '-div-warehouse-list'
div_product_list_id = prefix + '-div-product-list'
div_circuit_list_id = prefix + '-div-circuit-list'
div_product_range_list_id = prefix + '-div-product-range-list'
checkbox_warehouse_list_id = prefix + '-checkbox-warehouse-list'
checkbox_product_list_id = prefix + '-checkbox-product-list'
checkbox_circuit_list_id = prefix + '-checkbox-circuit-list'
checkbox_product_range_list_id = prefix + '-checkbox-product-range-list'

### Global variable ###

def filter_container():
    filter_container = html.Div([
        dbc.Row([
            

            dbc.Col([
                dcc.Upload(
                    id=file_upload_id,
                    children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select File')
                                ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                
            ], sm=12, md=12, lg=12),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id, [], 'Warehouses')

            ], sm=12, md=4, lg=4),
            # dbc.Col([
            #     dash_utils.get_filter_dropdown(
            #         dropdown_product_list_id, div_product_list_id, checkbox_product_list_id, [], 'Product')

            # ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_circuit_list_id, div_circuit_list_id, checkbox_circuit_list_id, [], 'Circuits')

            ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_filter_dropdown(
                    dropdown_product_range_list_id, div_product_range_list_id, checkbox_product_range_list_id, [], 'Product range')

            ], sm=12, md=4, lg=4),
            dbc.Col([
                dbc.Label('Show by'),
                dcc.Dropdown(
                    id=dropdown_show_by_id,
                    options=[
                        {'label': 'Quantity (Unit)', 'value': 'quantity'},
                        # {'label': 'Quantity (Package)', 'value': 'package'},
                        # {'label': 'Quantity (Pallet)', 'value': 'pallet'},
                        {'label': 'Turnover (DH)', 'value': 'cost'},
                        # {'label': 'Weight (Kg)', 'value': 'weight'},
                        {'label': 'Volume (m3)', 'value': 'volume'},
                    ],
                    value='quantity',
                ),

            ], sm=12, md=4, lg=4),
        ])
    ])
    return filter_container


def body_container():
    body_container = html.Div([
        dbc.Row([
            dbc.Col([
                dash_utils.get_mini_card(mini_card_subtitle_bias_percent_id, title='Forecast bias %',
                                    subtitle='', icon='')
            ], sm=12, md=6, lg=6),
            # dbc.Col([
            #     dash_utils.get_mini_card(mini_card_subtitle_mad_id, title='Mean absolute deviation (MAD)',
            #                         subtitle='', icon='')
            # ], sm=12, md=4, lg=4),
            dbc.Col([
                dash_utils.get_mini_card(mini_card_subtitle_mape_id, title='Mean absolute percentage error % (MAPE)',
                                    subtitle='', icon='')
            ], sm=12, md=6, lg=6),
        ]),
        dbc.Row([

            dbc.Col([
                dash_utils.get_chart_card(madec_chart1_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart2_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart3_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart4_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart5_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart6_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart7_id)
            ], sm=12, md=6, lg=6),
            dbc.Col([
                dash_utils.get_chart_card(madec_chart8_id)
            ], sm=12, md=6, lg=6),
        ]),
        dbc.Row([
            dbc.Col([
                dash_utils.get_datatable_card(datatable_data_upload_id),
            ], sm=12, md=12, lg=12),
            
        ]),
    ])
    return body_container


app.layout = dash_utils.get_dash_layout(filter_container(), body_container())


# def chart_1(df, kind, group_by_query_column, group_by_label, dropdown_y_axis):
#     df_chart = df.groupby([group_by_query_column, 'forecast_date_truncated'])[
#         'total_forecasted_value', 'total_ordered_value', 'forecast_bias'].sum().reset_index()
#     df_chart = df_chart.to_dict('records')

#     df_chart_grouped = common_utils.group_data_by_category(
#         df_chart,
#         category_key=group_by_query_column,
#         x_key='forecast_date_truncated',
#         y_key=dropdown_y_axis
#     )

#     chartdata = common_utils.build_chart_series(df_chart_grouped, chart_type='Scatter')

#     chart_layout = copy.deepcopy(dash_constants.layout)
#     chart_layout['title'] = 'Forecast Bias by Date by {}'.format(
#         group_by_label.capitalize())
#     chart_layout['xaxis'] = dict(
#         title='Date in {}s'.format(kind.capitalize()))
#     chart_layout['yaxis'] = dict(title='Forecast Bias')

#     figure = {'data': chartdata, 'layout': chart_layout}
#     return figure

# def chart_2(df, show_by, group_by_query_column, group_by_label):
#     df_chart = df.groupby([group_by_query_column])[
#         'total_forecasted_value', 'total_ordered_value', 'forecast_bias'].sum().reset_index()

#     chartdata = [
#         go.Scatter(
#             x=df_chart[group_by_query_column],
#             y=df_chart['total_forecasted_value'],
#             name='Forecasted value ({})'.format(show_by),
#         ),
#         go.Scatter(
#             x=df_chart[group_by_query_column],
#             y=df_chart['total_ordered_value'],
#             name='Ordered value ({})'.format(show_by),
#         ),
#         go.Bar(
#             x=df_chart[group_by_query_column],
#             y=df_chart['forecast_bias'],
#             name='Forecast bias',
#         ),
#     ]
#     chart_layout = copy.deepcopy(dash_constants.layout)
#     chart_layout['title'] = 'Forecast VS. Order Values by {}'.format(
#         group_by_label.capitalize())
#     chart_layout['xaxis'] = dict(
#         title='{}s'.format(group_by_label.capitalize()))
#     chart_layout['yaxis'] = dict(title='Values')

#     figure = {'data': chartdata, 'layout': chart_layout}
#     return figure

# @app.callback(
#     [
#         # Dataframe
#         Output(table_forecast_dataframe_id, 'data'),
#         Output(table_forecast_dataframe_id, 'columns'),
#         # Mini-cards
#         Output(mini_card_subtitle_bias_percent_id, 'children'),
#         Output(mini_card_subtitle_mad_id, 'children'),
#         Output(mini_card_subtitle_mape_id, 'children'),
#         # Charts
#         Output(chart_by_date_by_group_id, 'figure'),
#         Output(chart_by_group_id, 'figure'),
#     ],
#     [
#         Input(dropdown_group_by_product_field_id, 'value'),
#         Input(dropdown_group_by_distribution_field_id, 'value'),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#         Input(dropdown_kind_id, 'value'),
#         Input(dropdown_show_by_id, 'value'),
#         Input(dropdown_forecast_version_id, 'value'),
#         Input(chart_dropdown_y_axis_id, 'value'),
#     ]
# )
# def dataframe_date_filter(
#     group_by_product,
#     group_by_distribution,
#     forecast_start_date,
#     forecast_end_date,
#     kind,
#     show_by,
#     forecast_version,
#     dropdown_y_axis):
#     # Get queryset
#     qs = Forecast.objects.get_forecast_accuracy_main_queryset(
#         group_by_product, group_by_distribution, show_by, kind, 
#         forecast_start_date, forecast_end_date, forecast_version)
#     # Convert queryset to dataframe
#     df = read_frame(qs)

#     ### Dataframe ###
#     # Prepare data & columns to be returned
#     data = df.round(2).to_dict('records')
#     columns = [{"name": i, "id": i} for i in df.columns]

#     ### Charts ###
#     # Get group_by column
#     group_by_query_column = qs.get_group_by_column(
#         group_by_distribution, group_by_product)
#     # Get the label of group_by
#     group_by_label = group_by_distribution if group_by_distribution else group_by_product
#     # Chart 1
#     figure_1 = chart_1(
#         df, kind, group_by_query_column[0], group_by_label, dropdown_y_axis)
#     # Chart 2
#     figure_2 = chart_2(df, show_by, group_by_query_column[0], group_by_label)
    


#     ### Mini-cards ###
#     # Compute forecast bias
#     forecast_bias_avg = round(
#         100 * df['total_forecasted_value'].sum() / df['total_ordered_value'].sum(), 2)
#     # Compute forecast MAD
#     forecast_mad_avg = df['forecast_mad_single'].mean().round(2)
#     # Compute forecast MAPE
#     forecast_mape_avg = df['forecast_mape_single'].mean().round(2)

#     return (data, columns, forecast_bias_avg, forecast_mad_avg,
#             forecast_mape_avg, figure_1, figure_2)


# File uploader

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


@app.callback(
    [
        Output(madec_chart1_id, 'figure'),
        Output(madec_chart2_id, 'figure'), 
        Output(madec_chart3_id, 'figure'), 
        Output(madec_chart4_id, 'figure'), 
        Output(madec_chart5_id, 'figure'),
        Output(madec_chart6_id, 'figure'),
        Output(madec_chart7_id, 'figure'),
        Output(madec_chart8_id, 'figure'),

        # Output(dropdown_warehouse_list_id, 'options'),
        # Output(dropdown_product_list_id, 'options'),
        # Output(dropdown_circuit_list_id, 'options'),
        # Output(dropdown_product_range_list_id, 'options'),

        # Output(dropdown_warehouse_list_id, 'value'),
        # Output(dropdown_product_list_id, 'value'),
        # Output(dropdown_circuit_list_id, 'value'),
        # Output(dropdown_product_range_list_id, 'value'),

    ],
    [
        # Input(file_upload_id, 'contents'),
        # Input(file_upload_id, 'filename'),
        Input(datatable_data_upload_id, 'data'),
        Input(dropdown_show_by_id, 'value'),
        Input(dropdown_warehouse_list_id, 'value'),
        # Input(dropdown_product_list_id, 'value'),
        Input(dropdown_circuit_list_id, 'value'),
        Input(dropdown_product_range_list_id, 'value'),
    ]
)
def update_graphs(data, show_by, warehouse_list, circuit_list, product_range_list):    
    # Get dataframe
    df = pd.DataFrame.from_dict(data)

    # # Create list of variables for filter
    # warehouse_list = df['warehouse'].unique().tolist()
    # product_list = df['product'].unique().tolist()
    # circuit_list = df['circuit'].unique().tolist()
    # product_range_list = df['product_range'].unique().tolist()
    # # Options of drapdown
    # dropdown_warehouse_option = [{'label': i, 'value': i} for i in warehouse_list]
    # dropdown_product_option = [{'label': i, 'value': i} for i in product_list]
    # dropdown_circuit_option = [{'label': i, 'value': i} for i in circuit_list]
    # dropdown_product_range_option = [{'label': i, 'value': i} for i in product_range_list]
    # dropdown_option = [
    #     dropdown_warehouse_option,
    #     dropdown_product_option,
    #     dropdown_circuit_option,
    #     dropdown_product_range_option
    # ]
    # # Values of drapdown
    # dropdown_warehouse_value = [i['value'] for i in dropdown_warehouse_option]
    # dropdown_product_value = [i['value'] for i in dropdown_product_option]
    # dropdown_circuit_value = [i['value'] for i in dropdown_circuit_option]
    # dropdown_product_range_value = [i['value'] for i in dropdown_product_range_option]
    # dropdown_value = [
    #     dropdown_warehouse_value,
    #     dropdown_product_value,
    #     dropdown_circuit_value,
    #     dropdown_product_range_value
    # ]
    
    df = df[(df['warehouse'].isin(warehouse_list)) & (df['circuit'].isin(
        circuit_list)) & (df['product_range'].isin(product_range_list))]
    # df = df.loc[(df['warehouse'].isin(['Casablanca'])) & (df['product'].isin(product_list)) & (df['circuit'].isin(circuit_list)) & (df['product_range'].isin(product_range_list))]
    group_by_list = ['warehouse', 'circuit', 'product', 'product_range']

    show_by_axis = {
        'quantity': ['forecasted_by_quantity', 'sold_by_quantity', 'bias_quantity'],
        'cost': ['forecasted_by_cost', 'sold_by_cost', 'bias_cost'],
        'volume': ['forecasted_by_volume', 'sold_by_volume', 'bias_volume'],
    }

    figures = []
    for group_by in group_by_list:
        df_copy = df.groupby([group_by], as_index=False).agg(
            {show_by_axis[show_by][0]: 'sum', show_by_axis[show_by][1]: 'sum', show_by_axis[show_by][2]: 'sum'})
        df_copy['mape'] = abs(
            df_copy[show_by_axis[show_by][1]] - df_copy[show_by_axis[show_by][0]]) / df_copy[show_by_axis[show_by][1]]
        fig1 = df_copy.sort_values(by=[show_by_axis[show_by][2]], ascending=False).iplot(asFigure=True, kind='bar', x=group_by, y=[show_by_axis[show_by][0], show_by_axis[show_by][1], show_by_axis[show_by][2]], theme='white', title='Précision de la prévision par {}: Prévision, vente, bias'.format(group_by.capitalize()),
                            xTitle=group_by.capitalize(), yTitle=show_by.capitalize())
        fig2 = df_copy.sort_values(by=['mape'], ascending=False).iplot(asFigure=True, kind='bar', x=group_by, y='mape', theme='white', title='Précision de la prévision par {}: MAPE'.format(group_by.capitalize()),
                            xTitle=group_by.capitalize(), yTitle='MAPE')
        figures.append(fig1)
        figures.append(fig2)

        # df['female_age'] = df[df['Sex'] == 'female']['Age']
        

        # fig.data[0].update(
        #     text=df2007['gdpPercap'],
        #     textposition=’inside’,
        #     textfont=dict(size=10)
        # )

        # fig = df.iplot(asFigure=True, kind="scatter", theme="white", x="forecast_date", y=" forecasted_by_quantity ",
                    #    categories="profuct_range", title='My Chart Title', xTitle='Dates', yTitle='Returns', filename='Tutorial Metadata')
    return tuple(figures)

@app.callback(
    [
        Output(dropdown_warehouse_list_id, 'options'),
        # Output(dropdown_product_list_id, 'options'),
        Output(dropdown_circuit_list_id, 'options'),
        Output(dropdown_product_range_list_id, 'options'),


    ],
    [
        Input(datatable_data_upload_id, 'data'),
        # Input(dropdown_warehouse_list_id, 'value'),
        # Input(dropdown_product_list_id, 'value'),
        # Input(dropdown_circuit_list_id, 'value'),
        # Input(dropdown_product_range_list_id, 'value'),
    ]
)
def get_dropdown_lists(data):
# def update_graphs(data, warehouse_list, product_list, circuit_list, product_range_list):
    # Get dataframe
    df = pd.DataFrame.from_dict(data)

    # Create list of variables for filter
    warehouse_list = df['warehouse'].unique().tolist()
    product_list = df['product'].unique().tolist()
    circuit_list = df['circuit'].unique().tolist()
    product_range_list = df['product_range'].unique().tolist()
    # Options of drapdown
    dropdown_warehouse_option = [{'label': i, 'value': i} for i in warehouse_list]
    # dropdown_product_option = [{'label': i, 'value': i} for i in product_list]
    dropdown_circuit_option = [{'label': i, 'value': i} for i in circuit_list]
    dropdown_product_range_option = [{'label': i, 'value': i} for i in product_range_list]
    # dropdown_option = [
    #     dropdown_warehouse_option,
    #     dropdown_product_option,
    #     dropdown_circuit_option,
    #     dropdown_product_range_option
    # ]
    # # Values of drapdown
    # dropdown_warehouse_value = [i['value'] for i in dropdown_warehouse_option]
    # dropdown_product_value = [i['value'] for i in dropdown_product_option]
    # dropdown_circuit_value = [i['value'] for i in dropdown_circuit_option]
    # dropdown_product_range_value = [i['value'] for i in dropdown_product_range_option]
    # dropdown_value = [
    #     dropdown_warehouse_value,
    #     dropdown_product_value,
    #     dropdown_circuit_value,
    #     dropdown_product_range_value
    # ]
    
    return dropdown_warehouse_option, dropdown_circuit_option, dropdown_product_range_option


@app.callback(
    [
        Output(datatable_data_upload_id, 'data'),
        Output(datatable_data_upload_id, 'columns'),
    ],
    [
        Input(file_upload_id, 'contents'),
        Input(file_upload_id, 'filename')
    ]
)
def update_table(contents, filename):
    # table = html.Div()


    data = []
    columns = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        # convert columns to right type
        show_by_axis = {
            'quantity': ['forecasted_by_quantity', 'sold_by_quantity', 'bias_quantity'],
            'cost': ['forecasted_by_cost', 'sold_by_cost', 'bias_cost'],
            'volume': ['forecasted_by_volume', 'sold_by_volume', 'bias_volume'],
        }

        df['forecasted_by_quantity'] = pd.to_numeric(
            df['forecasted_by_quantity'], errors='coerce')
        df['sold_by_quantity'] = pd.to_numeric(
            df['sold_by_quantity'], errors='coerce')
        df['forecasted_by_cost'] = pd.to_numeric(
            df['forecasted_by_cost'], errors='coerce')
        df['sold_by_cost'] = pd.to_numeric(
            df['sold_by_cost'], errors='coerce')
        df['forecasted_by_volume'] = pd.to_numeric(
            df['forecasted_by_volume'], errors='coerce')
        df['sold_by_volume'] = pd.to_numeric(
            df['sold_by_volume'], errors='coerce')

        df['bias_quantity'] = df['forecasted_by_quantity'] - df['sold_by_quantity']
        df['bias_cost'] = df['forecasted_by_cost'] - df['sold_by_cost']
        df['bias_volume'] = df['forecasted_by_volume'] - df['sold_by_volume']

        data = df.to_dict('rows')
        columns=[{'name': i, 'id': i} for i in df.columns]

    

        # table = html.Div([
        #     html.H5(filename),
        #     dash_table.DataTable(
        #         data=df.to_dict('rows'),
        #         columns=[{'name': i, 'id': i} for i in df.columns]
        #     ),
        #     html.Hr(),
        #     html.Div('Raw Content'),
        #     html.Pre(contents[0:200] + '...', style={
        #         'whiteSpace': 'pre-wrap',
        #         'wordBreak': 'break-all'
        #     })
        # ])

    return data, columns


# Select all checklist callbacks
dash_utils.select_all_callbacks(
    app, dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id)
# dash_utils.select_all_callbacks(
#     app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_circuit_list_id, div_circuit_list_id, checkbox_circuit_list_id)
dash_utils.select_all_callbacks(
    app, dropdown_product_range_list_id, div_product_range_list_id, checkbox_product_range_list_id)









