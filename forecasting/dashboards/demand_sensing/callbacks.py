from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
from . import ids
from .app import app
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from django.utils.translation import gettext as _

import pandas as pd
import numpy as np

# from .app import app

from stock.models import OrderDetail
from forecasting.models import Version, Forecast


import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

@app.expanded_callback(
    # [
        Output(ids.DIV_CHART, 'children'),
        # Output(ids.DATABLE_FORECAST, 'columns'),
        # Output(ids.DATABLE_FORECAST, 'data'),
    # ],
    [
        Input(ids.DUMMY_DIV_TRIGGER, 'n_clicks'),
    ]
)
def init_graph_and_dataframe(n_clicks, *args, **kwargs):
    ''' Plot initial graph and initiate the dataframe ''' 
    _plot_freq = 'M'
    version_id = kwargs['session_state']['dash_context']['version_id']
    product_id = kwargs['session_state']['dash_context']['product_id']
    circuit_id = kwargs['session_state']['dash_context']['circuit_id']

    def get_order_history_qs(version_id, product_id, circuit_id):
        ''' Get last 2 years (based on version date) of orders data for the selected product & circuit '''
        _delta_year = 2

        # print('product_id ',product_id)
        # print('circuit_id ',circuit_id)
        version_obj = Version.objects.get(id=version_id) 
        qs = OrderDetail.objects.filter(
            product__id=product_id,
            circuit__id=circuit_id,
            order__ordered_at__lte=version_obj.version_date,
            order__ordered_at__gte=version_obj.version_date -
                                    timedelta(days=365*_delta_year),
        )
        qs = qs.values('order__ordered_at', 'ordered_quantity')
        # print(min(list(qs.values_list('order__ordered_at', flat=True))))
        # print(max(list(qs.values_list('order__ordered_at', flat=True))))
        return qs
    
    def get_forecast_qs(version_id, product_id, circuit_id):
        ''' Get forecasts of selected version '''
        qs = Forecast.objects.filter(
            version=version_id,
            product=product_id,
            circuit=circuit_id,
        )
        qs = qs.values('forecast_date', 'forecasted_quantity',
                       'edited_forecasted_quantity')
        return qs

    # Get forecasts
    forecast_qs = get_forecast_qs(version_id, product_id, circuit_id)
    forecast_df = read_frame(forecast_qs)
    forecast_df['forecast_date'] = forecast_df['forecast_date'].astype(
        'datetime64[ns]')


    # Group data and prepare the dataframe for the plot
    forecast_df = forecast_df.groupby(
        pd.Grouper(key='forecast_date', freq=_plot_freq)
    ).agg({
        'forecasted_quantity': 'sum',
        'edited_forecasted_quantity': 'sum',
    }).reset_index(
    ).sort_values(
        by=['forecast_date'],
        ascending=True,
    )
    # Convert datetime to date
    forecast_df['forecast_date'] = forecast_df['forecast_date'].dt.date
    # Add column to editable forecasts
    # forecast_df['edited_forecasted_quantity'].apply(
    #     lambda row: row['forecasted_quantity'])#row['edited_forecasted_quantity'] if row['edited_forecasted_quantity'] >= 0 else row['forecasted_quantity'])


    # Get orders
    order_qs = get_order_history_qs(version_id, product_id, circuit_id)
    order_df = read_frame(order_qs)
    order_df['order__ordered_at'] = order_df['order__ordered_at'].astype(
        'datetime64[ns]')


    # Group data and prepare the dataframe for the plot
    order_df = order_df.groupby(
        pd.Grouper(key='order__ordered_at', freq=_plot_freq)
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index(
    ).sort_values(
        by=['order__ordered_at'],
        ascending=True,
    )
    # Convert datetime to date
    order_df['order__ordered_at'] = order_df['order__ordered_at'].dt.date

    # Merge the two dataframes
    merged_df = pd.merge(order_df, forecast_df,
                         how='outer', left_on='order__ordered_at', right_on='forecast_date')
    # Merge date columns
    merged_df['date'] = merged_df.apply(lambda row: row['order__ordered_at']
                                        if not pd.isna(row['order__ordered_at']) else row['forecast_date'], axis=1)
    merged_df = merged_df[['date', 'ordered_quantity',
                         'forecasted_quantity', 'edited_forecasted_quantity']]
    
    # Plot the figure
    figure = merged_df.iplot(
        asFigure=True,
        kind='scatter',
        mode='lines+markers',
        size=4,
        x='date',
        y=['ordered_quantity', 'edited_forecasted_quantity'],
        theme='white',
        title=_('Orders & forecasts'),
        xTitle=_('date (monthly)'),
        yTitle=_('Quantity'),
    )
    # Add dashed forecasts to graph
    figure.add_trace(
        go.Scatter(
            x=merged_df['date'],
            y=merged_df['forecasted_quantity'],
            line=dict(color='red', width=2, dash='dash'),
            showlegend=True,
            name='forecasted_quantity',
        )
    )

    # Output datatable
    columns = [
        {
            'name': i,
            'id': i,
            'editable': True if i == 'edited_forecasted_quantity' else False
        } for i in merged_df.columns
    ]
    data = merged_df.to_dict('records')

    div = html.Div([
        # Chart
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    dcc.Graph(
                        id=ids.CHART_ORDER_FORECAST, 
                        figure=figure,
                        config=dict(displaylogo=False, showLink=False, showTips=True)
                    ),
                ),
            ], sm=12, md=12, lg=12),
        ]),
    
        # Datatable
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    dash_table.DataTable(
                        id=ids.DATABLE_FORECAST,
                        columns=columns,
                        data=data,
                        page_action='native',
                        filter_action='native',
                        sort_action='native',
                        sort_mode='multi',
                        page_size=50,
                        style_data_conditional=[{
                            'if': {'column_editable': True},
                            'backgroundColor': 'WhiteSmoke',
                        }],
                    )
                )
            ], sm=12, md=12, lg=12),
        ]),
    ])

    return div


@app.callback(
    Output(ids.CHART_ORDER_FORECAST, 'figure'),
    [
        Input(ids.DATABLE_FORECAST, 'data'),
    ],
    [
        State(ids.DATABLE_FORECAST, 'columns'),
        State(ids.CHART_ORDER_FORECAST, 'figure'),
    ],
)
def update_edited_forecast_chart(data, columns, figure, * args, **kwargs):
    ''' Update the chart once the dataframe is edited '''
    # Get the dataframe
    df = pd.DataFrame(data, columns=[c['name'] for c in columns])
    # Update the figure
    figure['data'][1]['x'] = df['date']
    figure['data'][1]['y'] = df['edited_forecasted_quantity']
    return figure


@app.expanded_callback(
    Output(ids.MESSAGE_SUCCESS_SAVE, 'is_open'),
    [
        Input(ids.BUTTON_SAVE, 'n_clicks'),
    ],
    [
        State(ids.DATABLE_FORECAST, 'columns'),
        State(ids.DATABLE_FORECAST, 'data'),
        # State(ids.MESSAGE_SUCCESS_SAVE, "is_open"),
    ],
)
def on_click_save_edited_forecast(n_clicks, columns, data, * args, **kwargs):
    ''' Save the edited version of the forecast on click. Data is parted by client '''
    # TODO disable after first click
    version_id = kwargs['session_state']['dash_context']['version_id']
    product_id = kwargs['session_state']['dash_context']['product_id']
    circuit_id = kwargs['session_state']['dash_context']['circuit_id']

    # Get the dataframe
    monthly_forecast_df = pd.DataFrame(data, columns=[c['name'] for c in columns])
    monthly_forecast_df['date'] = pd.to_datetime(
        monthly_forecast_df['date'], errors='coerce')

    
    # Get the query with dispatched data by product, customer, day
    qs = Forecast.objects.filter(
        version_id=version_id,
        product_id=product_id,
        circuit_id=circuit_id,
    )
    forecast_qs = qs.values('id', 'product__id', 'customer__id', 'circuit__id', 'version__id',
                            'forecast_date', 'forecasted_quantity', 'edited_forecasted_quantity')
    # Convert qs to df
    forecast_df = read_frame(forecast_qs)
    forecast_df['forecast_date'] = pd.to_datetime(forecast_df['forecast_date'], errors='coerce')


    def _get_forecasted_quantity_by_circuit_by_month(df, row):
        ''' Return aggregated values for the forecast column '''
        forecasted_quantity_sum = df.loc[
            # (df['circuit__id'] == row['circuit__id']) &
            (df['forecast_date'].dt.month == row['forecast_date'].month) & 
            (df['forecast_date'].dt.year == row['forecast_date'].year),
            'forecasted_quantity'
        ].sum()
        return forecasted_quantity_sum

    def _get_edited_forecasted_quantity_by_circuit_by_month(df, row):
        ''' Return aggregated values for the edited forecast column '''
        edited_forecasted_quantity_sum = df.loc[
            (df['date'].dt.month == row['forecast_date'].month) & 
            (df['date'].dt.year == row['forecast_date'].year),
            'edited_forecasted_quantity'
        ].sum()
        return int(edited_forecasted_quantity_sum)
    
    forecast_df['forecasted_quantity_by_circuit_by_month'] = forecast_df.apply(lambda row: _get_forecasted_quantity_by_circuit_by_month(forecast_df, row), axis=1)
    forecast_df['edited_forecasted_quantity_by_circuit_by_month'] = forecast_df.apply(lambda row: _get_edited_forecasted_quantity_by_circuit_by_month(monthly_forecast_df, row), axis=1)

    # FIXME edited forecast conversion to int makes the total value < original value 
    forecast_df['new_edited_forecasted_quantity'] = forecast_df['edited_forecasted_quantity_by_circuit_by_month'] * \
        forecast_df['forecasted_quantity'] / \
        forecast_df['forecasted_quantity_by_circuit_by_month']
    forecast_df['new_edited_forecasted_quantity'] = forecast_df['new_edited_forecasted_quantity'].astype(int)

    # Bulk update edited forecasts in database
    forecast_objs = [
        Forecast(
            id=row['id'],
            edited_forecasted_quantity=row['new_edited_forecasted_quantity'],
        )
        for i, row in forecast_df.iterrows()
    ]
    Forecast.objects.bulk_update(forecast_objs, fields=[
                                 'edited_forecasted_quantity'])

    return True

