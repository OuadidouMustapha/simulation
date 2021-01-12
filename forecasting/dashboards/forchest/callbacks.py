from django_pandas.io import read_frame
from .components.forchest_model import get_forecasts, get_forchest_demo_data
from . import ids
from .app import app
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import pandas as pd
# from .app import app

from stock.models import Order
from forecasting.models import Event, EventDetail
# from stock.models import Product, Warehouse, Circuit, Customer
# from common.dashboards import dash_constants, dash_utils
# from common import utils as common_utils
# from django_plotly_dash import DjangoDash
# from django_pandas.io import read_frame
# from django.db.models import OuterRef
# from dash.exceptions import PreventUpdate
# from dash.dependencies import Input, Output, State
# from django.utils.translation import gettext as _
# import copy
# import datetime

# import dash_bootstrap_components as dbc
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_table
# import pandas as pd
# import numpy as np
# import plotly.graph_objs as go

# import cufflinks as cf
# cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True


@app.callback(
    [
        Output(ids.CHART_ORDER_FORECAST, 'figure'),
        Output(ids.CHART_ORDER_FORECAST_COMPONENTS, 'figure'),
        Output(ids.DATABLE_HISTORY, 'columns'),
        Output(ids.DATABLE_HISTORY, 'data'),
        Output(ids.DATABLE_FORECAST, 'columns'),
        Output(ids.DATABLE_FORECAST, 'data'),
    ],
    [
        Input(ids.DROPDOWN_PRODUCT, 'value'),
        Input(ids.DROPDOWN_CIRCUIT, 'value'),
    ]
)
def update_graph(product_id, circuit_id):
    ''' Plot and update forecasts chart '''

    '''
    # THIS BLOC IS USED FOR TESTING PURPOSE
    # Get demo data TODO get data from DB
    order_df, orders_original_df = get_forchest_demo_data()
    # Create Holidays df TODO Create holiday table in the model
    holidays = pd.DataFrame({
        'holiday': 'discount',
        'ds': pd.to_datetime(['2020-03-12', '2020-09-20']),
        'lower_window': 0,
        'upper_window': 10,
    })
    m, forecast_df, forecast_fig, components_fig = get_forecasts(order_df, holidays=holidays, add_country_holidays='MA', forecast_periods=30*3,
                                                                 freq='D', include_history=False, floor=0, cap=100000,
                                                                 forecast_fig=True, components_fig=True)
    '''
    product_id = 7664
    circuit_id = 6
    floor = 0
    cap = 100000
    _forecast_period = 8#2*30
    _freq = 'M'
    # Get filtered orders
    
    order_df = read_frame(Order.objects.get_orders_for_prophet(product_id, circuit_id))
    order_df['cap'] = cap
    order_df['floor'] = floor

    holidays_df = read_frame(EventDetail.objects.get_events(product_id, circuit_id))
    
    # Create the forecast model and get the graphs
    m, forecast_df, forecast_fig, components_fig = get_forecasts(order_df, holidays=holidays_df, add_country_holidays='MA', forecast_periods=_forecast_period,
                                                              freq=_freq, include_history=False, floor=floor, cap=cap,
                                                              forecast_fig=True, components_fig=True)
    
    order_column = [{"name": i, "id": i} for i in order_df[['ds', 'y']].columns]
    order_data = order_df[['ds', 'y']].to_dict('records')

    forecast_column = [{"name": i, "id": i}
                       for i in forecast_df[['ds', 'yhat']].columns]
    forecast_data = forecast_df[['ds', 'yhat']].to_dict('records')


    '''
    # # Add original data to the graph
    # forecast_fig.add_trace(
    #     go.Scatter(
    #         x=orders_original_df['ordered_at'],
    #         y=orders_original_df['ordered_quantity'],
    #         mode='lines',
    #         line=go.scatter.Line(color='orange'),
    #         showlegend=True,
    #         name='original & real future data',
    #     )
    # )
    '''
 
    return forecast_fig, components_fig, order_column, order_data, forecast_column, forecast_data


# @app.callback(
#     [
#         Output(mini_card_subtitle_bias_percent_id, 'children'),
#         Output(mini_card_datatable_bias_percent_id, 'data'),
#         Output(mini_card_datatable_bias_percent_id, 'columns'),
#     ],
#     [
#         Input(table_forecast_dataframe_id, 'data'),
#         Input(mini_card_dropdown_bias_percent_id, 'value'),
#     ]
# )
# def fill_cards(
#     input_data,
#     group_by,
# ):
#     # Get dataframe
#     df = pd.DataFrame.from_dict(input_data)
#     # Group by selected field
#     df = df.groupby(
#         by=group_by,
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#     }).reset_index()

#     # Add metrics columns
#     df['forecast_bias_percent'] = round(
#         100 * df['forecasted_quantity'] / df['ordered_quantity'], 2)

#     # Compute metrics
#     card_value = round(
#         100 * df['forecasted_quantity'].sum() / df['ordered_quantity'].sum(), 2)

#     # Prepare & sort & trunck data to be returned
#     df = df[
#         [group_by, 'forecast_bias_percent']
#     ].replace(
#         [np.inf, -np.inf], np.nan
#     ).sort_values(
#         'forecast_bias_percent',
#         # ascending=False,
#     ).head(10)

#     # Output datatable
#     column = [{"name": i, "id": i} for i in df.columns]
#     data = df.to_dict('records')

#     return (
#         card_value,
#         data,
#         column
#     )


# @app.callback(
#     [
#         Output(mini_card_subtitle_mad_id, 'children'),
#         Output(mini_card_datatable_mad_id, 'data'),
#         Output(mini_card_datatable_mad_id, 'columns'),
#     ],
#     [
#         Input(table_forecast_dataframe_id, 'data'),
#         Input(mini_card_dropdown_mad_id, 'value'),
#     ]
# )
# def fill_cards(
#     input_data,
#     group_by,
# ):
#     # Get dataframe
#     df = pd.DataFrame.from_dict(input_data)
#     # Group by selected field
#     df = df.groupby(
#         by=group_by,
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#     }).reset_index()

#     # Add metrics columns
#     df['forecast_mad_single'] = round(abs(
#         df['forecasted_quantity'] - df['ordered_quantity']), 2)

#     # Compute metrics
#     card_value = df['forecast_mad_single'].mean().round(2)
#     # forecast_mape_avg = df['forecast_mape_single'].mean().round(2)

#     # Prepare & sort & trunck data to be returned
#     df = df[
#         [group_by, 'forecast_mad_single']
#     ].replace(
#         [np.inf, -np.inf], np.nan
#     ).sort_values(
#         'forecast_mad_single',
#         ascending=False,
#     ).head(10)

#     # Output datatable
#     column = [{"name": i, "id": i} for i in df.columns]
#     data = df.to_dict('records')

#     return (
#         card_value,
#         data,
#         column
#     )


# @app.callback(
#     [
#         Output(mini_card_subtitle_mape_id, 'children'),
#         Output(mini_card_datatable_mape_id, 'data'),
#         Output(mini_card_datatable_mape_id, 'columns'),
#     ],
#     [
#         Input(table_forecast_dataframe_id, 'data'),
#         Input(mini_card_dropdown_mape_id, 'value'),
#     ]
# )
# def fill_cards(
#     input_data,
#     group_by,
# ):
#     # Get dataframe
#     df = pd.DataFrame.from_dict(input_data)
#     # Group by selected field
#     df = df.groupby(
#         by=group_by,
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#     }).reset_index()

#     # Add metrics columns
#     df['forecast_mape_single'] = round(100 * abs(
#         df['forecasted_quantity'] - df['ordered_quantity']) / df['ordered_quantity'], 2)

#     # Compute metrics
#     card_value = df['forecast_mape_single'].mean().round(2)

#     # Prepare & sort & trunck data to be returned
#     df = df[
#         [group_by, 'forecast_mape_single']
#     ].replace(
#         [np.inf, -np.inf], np.nan
#     ).sort_values(
#         'forecast_mape_single',
#         ascending=False,
#     ).head(10)

#     # Output datatable
#     column = [{"name": i, "id": i} for i in df.columns]
#     data = df.to_dict('records')

#     return (
#         card_value,
#         data,
#         column
#     )


# @app.callback(
#     [
#         # Dataframe
#         Output(table_forecast_dataframe_id, 'data'),
#         Output(table_forecast_dataframe_id, 'columns'),
#     ],
#     [
#         Input(dropdown_product_list_id, 'value'),
#         Input(dropdown_warehouse_list_id, 'value'),
#         Input(dropdown_circuit_list_id, 'value'),
#         Input(dropdown_customer_list_id, 'value'),
#         Input(input_date_range_id, 'start_date'),
#         Input(input_date_range_id, 'end_date'),
#     ]
# )
# def dataframe_date_filter(
#         selected_products,
#         selected_warehouses,
#         selected_circuits,
#         selected_customers,
#         start_date,
#         end_date,
#         # kind,
#         # show_by,
#         # forecast_version,
#         # dropdown_y_axis
# ):

#     # # Define group_by
#     # group_by = []
#     # if group_by_product:
#     #     group_by.append(group_by_product)
#     # if group_by_distribution:
#     #     group_by.append(group_by_distribution)

#     # # Define kind
#     # if kind = 'year':
#     #     kind_format = '%Y'
#     # elif kind = 'month':
#     #     kind_format = '%Y'

#     # group_by = {
#     #     0: ['product'],
#     #     1: ['warehouse'],
#     #     2: ['circuit'],
#     #     3: ['customer'],
#     #     4: ['product__type'],
#     #     5: ['product__type', 'warehouse'],
#     #     6: ['product__type', 'circuit'],
#     #     7: ['product__type', 'customer'],
#     # }

#     # Get queryset
#     forecast_qs = Forecast.objects.get_forecasting(
#         product_filter=selected_products, warehouse_filter=selected_warehouses, circuit_filter=selected_circuits, customer_filter=selected_customers, start_date=start_date, end_date=end_date)

#     order_qs = Order.objects.get_forecasting(
#         product_filter=selected_products, warehouse_filter=selected_warehouses, circuit_filter=selected_circuits, customer_filter=selected_customers, start_date=start_date, end_date=end_date)

#     # Convert queryset to dataframe and assign the right column type
#     forecast_df = read_frame(forecast_qs)
#     forecast_df['forecast_date'] = forecast_df['forecast_date'].astype(
#         'datetime64[ns]')

#     order_df = read_frame(order_qs)
#     order_df['ordered_at'] = order_df['ordered_at'].astype('datetime64[ns]')

#     # TODO I'm HERE. Check tmp issue and maybe think to fill empty data by a default value "undefined". Do that to all columns (check graph to understand)
#     # Fill empty values to avoid issues when filtering
#     # forecast_df = forecast_df.fillna(forecast_df.dtypes.replace({'O': 'Undifined'})) # 'float64': 0.0,
#     # order_df = order_df.fillna(order_df.dtypes.replace({'O': 'Undifined'}))
#     # forecast_df = forecast_df.replace('', np.nan)
#     # order_df = order_df.replace('', np.nan)
#     forecast_df['customer'] = forecast_df['customer'].fillna('undefined')
#     order_df['customer'] = order_df['customer'].fillna('undefined')
#     # default grouping
#     _group_by_default = ['product', 'warehouse', 'circuit', 'customer']

#     # Group by order_date and aggregate
#     # forecast_df['forecast_date'] = forecast_df['forecast_date'].dt.strftime(kind)
#     forecast_df = forecast_df.groupby([*_group_by_default, 'forecast_date'], as_index=False).agg(
#         {'forecasted_quantity': 'sum', 'product__product_type': 'first'})

#     # order_df['ordered_at'] = order_df['ordered_at'].dt.strftime(kind)
#     order_df = order_df.groupby([*_group_by_default, 'ordered_at'], as_index=False).agg(
#         {'ordered_quantity': 'sum'})

#     merged_df = pd.merge(forecast_df, order_df, how='left', left_on=[
#         *_group_by_default, 'forecast_date'], right_on=[
#         *_group_by_default, 'ordered_at'])  # .dropna()

#     # Prepare data & columns to be returned
#     data = merged_df.to_dict('records')
#     columns = [{"name": i, "id": i} for i in merged_df.columns]

#     return data, columns



# @app.callback(
#     [
#         Output(chart_2_1_id, 'figure'),
#         Output(chart_2_2_id, 'figure'),
#         Output(chart_2_3_id, 'figure'),
#     ],

#     [
#         # Input(datatable_data_upload_id, 'column'),
#         Input(table_forecast_dataframe_id, 'data'),
#         Input(dropdown_chart_2_group_by_product_id, 'value'),
#         Input(dropdown_chart_2_group_by_distribution_id, 'value'),
#         Input(dropdown_chart_2_kind_id, 'value'),
#         Input(dropdown_chart_2_show_by_id, 'value'),
#         Input(dropdown_chart_2_2_y_column_id, 'value'),
#         Input(dropdown_chart_2_3_metric_id, 'value'),
#     ]
# )
# def update_graph(
#         data,
#         group_by_product,
#         group_by_distribution,
#         kind,
#         show_by,
#         selected_y_column,
#         selected_metric):
#     # Define group_by
#     group_by = []
#     if group_by_distribution:
#         group_by.append(group_by_distribution)
#     if group_by_product:
#         group_by.append(group_by_product)

#     # Get dataframe
#     df = pd.DataFrame.from_dict(data)

#     # Clear figure if empty data or no groupby field is provided
#     if df.empty or group_by == []:
#         return {}

#     # Convert datetime column to the correct kind (day, week, year..)
#     df['forecast_date'] = df['forecast_date'].astype(
#         'datetime64[ns]')
#     df['forecast_date'] = df['forecast_date'].dt.strftime(kind)
#     df['bias_quantity'] = df['forecasted_quantity'] - df['ordered_quantity']

#     # Figure settings
#     # Figure_1
#     df_1 = df.copy()

#     figure_1 = df_1.groupby(
#         by=[*group_by],
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#         'bias_quantity': 'sum'
#     }).reset_index(
#     ).sort_values(
#         by=['bias_quantity'],
#         ascending=False,
#         na_position='first',
#     ).iplot(
#         asFigure=True,
#         kind='bar',
#         # barmode='stack',
#         x=group_by,
#         y=['forecasted_quantity', 'ordered_quantity', 'bias_quantity'],
#         theme='white',
#         title=_('Forecast accuracy by {}: Forecasts, orders, bias').format(
#             [item.split('__')[-1] for item in group_by]
#         ),
#         xTitle=_('{}').format([item.split('__')[-1] for item in group_by]),
#         yTitle=show_by.capitalize(),
#     )

#     # Figure 2
#     df_2 = df.copy()

#     figure_2 = df_2.groupby(
#         by=['forecast_date', group_by[0]],
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#         'bias_quantity': 'sum'
#     }).reset_index(
#     ).sort_values(
#         by=['forecast_date', group_by[0]],
#         ascending=True
#     ).iplot(
#         asFigure=True,
#         kind='scatter',
#         mode='lines + markers',
#         size=5,
#         x='forecast_date',
#         y=selected_y_column,  # ['forecasted_quantity', 'ordered_quantity'],
#         # group_by[1] if len(group_by) > 1 else group_by[0], # Assuming the array is not empty (checked previousely)
#         categories=group_by[0],
#         theme='white',
#         title=_('{} by {}').format(
#             selected_y_column.capitalize(),
#             group_by[0],
#         ),
#         xTitle=_('date'),
#         yTitle=_('Quantity'),
#     )

#     # Figure 3
#     df_3 = df.copy().groupby(
#         by=[*group_by],
#         as_index=False
#     ).agg({
#         'forecasted_quantity': 'sum',
#         'ordered_quantity': 'sum',
#         'bias_quantity': 'sum'
#     }).reset_index()
#     # Add metrics to dataframe
#     df_3['forecast_bias_percent'] = round(
#         100 * df_3['forecasted_quantity'] / df_3['ordered_quantity'], 2)
#     df_3['forecast_mad_single'] = round(abs(
#         df_3['forecasted_quantity'] - df_3['ordered_quantity']), 2)
#     df_3['forecast_mape_single'] = round(100 * abs(
#         df_3['forecasted_quantity'] - df_3['ordered_quantity']) / df_3['ordered_quantity'], 2)

#     # Filter out rows with nan and inf
#     df_3 = df_3[~df_3[[selected_metric]].isin(
#         [np.nan, np.inf, -np.inf]).any(1)]
#     figure_3 = df_3.sort_values(
#         by=selected_metric,
#         ascending=False,
#         # na_position='last'
#     ).iplot(
#         asFigure=True,
#         kind='bar',
#         x=group_by,
#         y=selected_metric,
#         # categories=group_by[1] if len(group_by) > 1 else group_by[0],
#         theme='white',
#         title=_('Metric distribution by {}').format(
#             [item.split('__')[-1] for item in group_by]
#         ),
#         xTitle=_('{}').format([item.split('__')[-1] for item in group_by]),
#         yTitle=_('Metric'),
#     )

#     return figure_1, figure_2, figure_3


# # Select all checklist callbacks
# dash_utils.select_all_callbacks(
#     app, dropdown_warehouse_list_id, div_warehouse_list_id, checkbox_warehouse_list_id)
# dash_utils.select_all_callbacks(
#     app, dropdown_product_list_id, div_product_list_id, checkbox_product_list_id)
# dash_utils.select_all_callbacks(
#     app, dropdown_circuit_list_id, div_circuit_list_id, checkbox_circuit_list_id)
# dash_utils.select_all_callbacks(
#     app, dropdown_product_range_list_id, div_product_range_list_id, checkbox_product_range_list_id)
