import os
import pandas as pd
import datetime
from fbprophet import Prophet
from fbprophet.plot import plot_plotly, plot_components_plotly
import plotly.offline
import plotly.graph_objects as go
import cufflinks as cf
cf.offline.py_offline.__PLOTLY_OFFLINE_INITIALIZED = True

# Returns the Path your .py file is in
workpath = os.path.dirname(os.path.abspath(__file__))
csv_filename = os.path.join(workpath, 'forchest_test_data/CA_COM_gcl1.csv')
_cap = 100000
_floor = 0


def get_forchest_demo_data(csv_filename=csv_filename, _date_group='D', _floor=_floor, _cap=_cap, _product_reference='PF002079'):
    ''' Use demo data to make predections '''
    # Read data from csv file
    df = pd.read_csv(csv_filename)
    # Rename columns
    df.columns = ['warehouse', 'ordered_at', 'supplier', 'order_reference', 'tour', 'customer', 'order_line',
                        'product_reference', 'ordered_quantity', 'retour_conf', 'retour_non_conf', 'unit_price',
                        'discount', 'tva', 'month', 'day']
    # Format columns
    df['ordered_at'] = pd.to_datetime(df['ordered_at'])


    # Copy original df
    orders_original_df = df.loc[(df['product_reference'] == _product_reference),
                                    ['ordered_at', 'ordered_quantity']]
    orders_original_df = orders_original_df.resample(
        _date_group, on='ordered_at').sum().reset_index()

    # Split df and get train data
    orders_forecast_df = df.loc[(df['product_reference'] == _product_reference) &
                                    #                                    (df['warehouse'] == _warehouse_reference) &
                                    (df['ordered_at'] < '2020-10-01'),
                                    ['ordered_at', 'ordered_quantity']]
    orders_forecast_df = orders_forecast_df.resample(
        _date_group, on='ordered_at').sum().reset_index()
    orders_forecast_df.columns = ['ds', 'y']
    orders_forecast_df['cap'] = _cap
    orders_forecast_df['floor'] = _floor
    return orders_forecast_df, orders_original_df



def get_forecasts(df, holidays=None, add_country_holidays=None, forecast_periods=30*1,
                  freq='D', include_history=False, floor=_floor, cap=_cap,
                  forecast_fig=True, components_fig=True):
    ''' return trained model and forecasted data. Adds charts to the results if figures flags are true '''
    # Model settings
    m = Prophet(holidays=holidays, growth='logistic',
                seasonality_mode='multiplicative')
    # Add default holidays of a country to the model
    if add_country_holidays:
        m.add_country_holidays(country_name=add_country_holidays)
        # print('Holidays taking into conciderations are:')
        # print(m.train_holiday_names)
    m.fit(df)

    # Make dataframe with future dates for forecasting
    future = m.make_future_dataframe(
        periods=forecast_periods, freq=freq, include_history=include_history)
    future['cap'] = cap
    future['floor'] = floor

    forecast = m.predict(future)
    # Clip values to zero
    forecast['yhat'] = forecast['yhat'].clip(0)
    # Round values to get integers
    forecast['yhat'] = forecast['yhat'].round()

    results = (m, forecast)

    # Plot graphs
    if forecast_fig:
        # Forecast
        fig_forecast = plot_plotly(m, forecast)
        fig_forecast.add_trace(
            go.Scatter(
                x=df['ds'],
                y=df['y'],
                mode='lines',
                line=go.scatter.Line(color='green'),
                showlegend=True,
                name='original',
            )
        )
        fig_forecast.update_layout(
            # legend=dict(
            #     orientation="h",
            #     # yanchor="bottom",
            #     # y=1.02,
            #     # xanchor="right",
            #     # x=1
            # ),
            showlegend=True, autosize=True, height=None, width=None)
        # fig_forecast.show()
        results = results + (fig_forecast,)

    # Components
    if components_fig:
        fig_components = plot_components_plotly(m, forecast)
        fig_components.update_layout(autosize=True, height=None, width=None)
        # fig_components.show()
        results = results + (fig_components,)


    return results
