from django.shortcuts import get_object_or_404
from datetime import date, datetime, timedelta
from django_pandas.io import read_frame
from . import ids
from .app import app
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from django.utils.translation import gettext as _

from django.db.models import F
import pandas as pd
import numpy as np

# from .app import app

from stock.models import OrderDetail
from forecasting.models import Version, VersionDetail, Forecast, Target, PlannedOrder, EventDetail, Event
from account.models import CustomUser
from ...views import VersionDetailView

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

@app.expanded_callback(
    [
        Output(ids.DIV_CHART, 'children'),
        Output(ids.BUTTON_APPROVE, 'hidden'),
        Output(ids.BUTTON_REJECT, 'hidden'),
        Output(ids.BUTTON_SUBMIT_REVIEW, 'hidden'),
        Output(ids.BUTTON_SAVE, 'hidden'),
    ],
    [
        Input(ids.DUMMY_DIV_TRIGGER, 'n_clicks'),
    ]
)
def init_graph_and_dataframe(n_clicks, *args, **kwargs):
    ''' Plot initial graph and initiate the dataframe ''' 
    _plot_freq = 'M'
    # Get version detail object
    versiondetail_id = kwargs['session_state']['dash_context']['versiondetail_id']
    versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)

    # Get the user object
    user = kwargs['user']

    # Buttons layout definition
    hide_btn_approve = True
    hide_btn_reject = True
    hide_btn_event_save = True
    hide_btn_event_update = True
    hide_btn_review = True
    hide_btn_save = True
    if user.has_perm('forecasting.can_request_review'):
        hide_btn_event_save = False
        hide_btn_event_update = False
        hide_btn_review = False
        hide_btn_save = False
    if user.has_perm('forecasting.can_validate_version') and (versiondetail_obj.approved_by != None and user.id == versiondetail_obj.approved_by.id):
        hide_btn_approve = False
        hide_btn_reject = False

    # Get event data
    def get_eventdetail_qs(versiondetail_id):
        ''' Return events for selected {product, circuit} '''
        # Get version detail object
        _delta_year = 2
        versiondetail_id = kwargs['session_state']['dash_context']['versiondetail_id']
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)

        qs = EventDetail.objects.filter(
            product=versiondetail_obj.product,
            circuit=versiondetail_obj.circuit,
            start_date__gte=versiondetail_obj.version.version_date -
                timedelta(days=365*_delta_year),
        )
        qs = qs.values('id', 'product', 'circuit', 'event__id',
                       'start_date', 'lower_window', 'upper_window')
        return qs

    eventdetail_qs = get_eventdetail_qs(versiondetail_id)
    eventdetail_df = read_frame(eventdetail_qs)
    # Hide first 3 columns
    eventdetail_columns = [{
        'name': i, 
        'id': i,
        'presentation': 'dropdown' if i == 'event__id' else None,
        'editable': True if (user.has_perm('forecasting.can_request_review')) else False,
        'type': 'datetime' if i == 'start_date' else 'any'
    } for i in eventdetail_df.columns[3:]]
    eventdetail_data = eventdetail_df.to_dict('records')
    # Get all events for the dropdown
    _all_events_dropdown = list(Event.objects.annotate(label=F('category'), value=F('id')).values('label', 'value').distinct())


    def get_order_history_qs(versiondetail_id):
        ''' Get last 2 years (based on version date) of orders data for the selected product & circuit '''
        _delta_year = 2
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)
        qs = OrderDetail.objects.filter(
            product=versiondetail_obj.product,
            circuit=versiondetail_obj.circuit,
            order__ordered_at__gte=versiondetail_obj.version.version_date -
                                    timedelta(days=365*_delta_year),
            order__ordered_at__lte=versiondetail_obj.version.version_date,
        )
        qs = qs.values('order__ordered_at', 'ordered_quantity')
        qs = qs.order_by('order__ordered_at')
        return qs
    
    def get_forecast_qs(versiondetail_id):
        ''' Get forecasts of selected version '''
        versiondetail_obj = get_object_or_404(
            VersionDetail, pk=versiondetail_id)

        qs = Forecast.objects.filter(
            version=versiondetail_obj.version,
            product=versiondetail_obj.product,
            circuit=versiondetail_obj.circuit,
        )
        qs = qs.values('forecast_date', 'forecasted_quantity',
                       'edited_forecasted_quantity')
        qs = qs.order_by('forecast_date')

        return qs

    def get_target_qs(versiondetail_id):
        _delta_year = 2
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)

        qs = Target.objects.filter(
            product=versiondetail_obj.product,
            circuit=versiondetail_obj.circuit,
            targeted_date__lte=versiondetail_obj.version.version_date,
            targeted_date__gte=versiondetail_obj.version.version_date -
            timedelta(days=365*_delta_year),
        )
        qs = qs.values('targeted_date', 'targeted_quantity')
        qs = qs.order_by('targeted_date')
        return qs

    def get_plannedorder_qs(versiondetail_id):
        _delta_year = 2
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)

        qs = PlannedOrder.objects.filter(
            product=versiondetail_obj.product,
            # customer__circuit=versiondetail_obj.circuit,
            circuit=versiondetail_obj.circuit,
            # planned_at__lte=versiondetail_obj.version.version_date,
            # planned_at__gte=versiondetail_obj.version.version_date -
            # timedelta(days=365*_delta_year),
        )
        qs = qs.values('planned_at', 'planned_quantity')
        qs = qs.order_by('planned_at')
        return qs


    # Get forecasts
    forecast_qs = get_forecast_qs(versiondetail_id)
    forecast_df = read_frame(forecast_qs)

    # forecast_df['event__id'] = forecast_df['event__id'].astype('int32')
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

    # Get planned orders
    plannedorder_qs = get_plannedorder_qs(versiondetail_id)
    plannedorder_df = read_frame(plannedorder_qs)
    plannedorder_df['planned_at'] = plannedorder_df['planned_at'].astype(
        'datetime64[ns]')
        
    # Group data and prepare the dataframe for the plot
    plannedorder_df = plannedorder_df.groupby(
        pd.Grouper(key='planned_at', freq=_plot_freq)
    ).agg({
        'planned_quantity': 'sum',
    }).reset_index(
    ).sort_values(
        by=['planned_at'],
        ascending=True,
    )
    # Convert datetime to date
    plannedorder_df['planned_at'] = plannedorder_df['planned_at'].dt.date


    # Add planned orders to the forecasted df
    forecast_df = pd.merge(forecast_df, plannedorder_df,
                           how='left', left_on='forecast_date', right_on='planned_at')
    # # Sum planned & forecasted quantity
    # forecast_df['planned_quantity'] = forecast_df['planned_quantity'].fillna(0)

    # Get orders
    order_qs = get_order_history_qs(versiondetail_id)
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

    # Get target
    target_qs = get_target_qs(versiondetail_id)
    target_df = read_frame(target_qs)
    target_df['targeted_date'] = target_df['targeted_date'].astype(
        'datetime64[ns]')
    # Group data and prepare the dataframe for the plot
    target_df = target_df.groupby(
        pd.Grouper(key='targeted_date', freq=_plot_freq)
    ).agg({
        'targeted_quantity': 'sum',
    }).reset_index(
    ).sort_values(
        by=['targeted_date'],
        ascending=True,
    )
    # Convert datetime to date
    target_df['targeted_date'] = target_df['targeted_date'].dt.date

    # Merge the two dataframes
    merged_df = pd.merge(order_df, forecast_df,
                         how='outer', left_on='order__ordered_at', right_on='forecast_date')

    # Merge date columns
    merged_df['date'] = merged_df.apply(lambda row: row['order__ordered_at']
                                        if not pd.isna(row['order__ordered_at']) else row['forecast_date'], axis=1)
    # Merge with target df
    merged_df = pd.merge(merged_df, target_df,
                         how='left', left_on='date', right_on='targeted_date')
    merged_df = merged_df[['date', 'targeted_quantity', 'ordered_quantity', 'planned_quantity',
                         'forecasted_quantity', 'edited_forecasted_quantity']]
    merged_df = merged_df.sort_values('date')
    
    # Plot the figure
    figure = merged_df.iplot(
        asFigure=True,
        kind='scatter',
        mode='lines+markers',
        size=4,
        x='date',
        y=['edited_forecasted_quantity'],
        theme='white',
        title=_('Targets, orders & forecasts'),
        xTitle=_('date (monthly)'),
        yTitle=_('Quantity'),
    )
    # Add targeted_quantity to graph
    figure.add_trace(
        go.Bar(
            x=merged_df['date'].tolist(),
            y=merged_df['targeted_quantity'].tolist(),
            width=2,
            # line=dict(color='red', width=2, dash='dash'),
            showlegend=True,
            name='targeted_quantity',
        )
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
    # Add ordered_quantity to graph
    figure.add_trace(
        go.Scatter(
            x=merged_df['date'],
            y=merged_df['ordered_quantity'],
            # line=dict(color='red', width=2, dash='dash'),
            showlegend=True,
            name='ordered_quantity',
        )
    )

    # Output datatable
    forecast_columns = [
        {
            'name': i,
            'id': i,
            'editable': True if (i == 'edited_forecasted_quantity' and user.has_perm('forecasting.can_request_review')) else False,
        } for i in merged_df.columns
    ]
    forecast_data = merged_df.to_dict('records')

    div = html.Div([
        # Chart
        dbc.Row([
            dbc.Col([
                html.P(
                    [
                        html.I(className="fas fa-chevron-right mr-2"),
                        _('Graph of order history and forecasts for (product: '),
                        versiondetail_obj.product.reference,
                        ', circuit: ',
                        versiondetail_obj.circuit.reference,
                        ')',
                    ],
                    className='font-weight-bold text-primary my-3'
                ),
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
                html.P(
                    [html.I(className="fas fa-chevron-right mr-2"),
                     _('List of events')],
                    className='font-weight-bold text-primary my-3'
                ),

                dcc.Loading(
                    dash_table.DataTable(
                        id=ids.DATABLE_EVENTS,
                        columns=eventdetail_columns,
                        data=eventdetail_data,
                        page_action='native',
                        filter_action='native',
                        sort_action='native',
                        sort_mode='multi',
                        page_size=50,
                        dropdown={
                            'event__id': {
                                'options': _all_events_dropdown
                            },
                        },

                        style_data_conditional=[{
                            'if': {'column_editable': True},
                            'backgroundColor': 'WhiteSmoke',
                        }],
                        # NOTE custom css added to avoid hidden dropdown issue
                        css=[{"selector": ".Select-menu-outer",
                              "rule": "display: block !important"}],
                    )
                ),
                html.Button(
                    [html.I(className="fas fa-plus mr-2"), _('Add event')],
                    id=ids.BUTTON_EVENT_ADD,
                    className="btn btn-xs btn-success my-3",
                    hidden=hide_btn_event_save
                ),
                html.Button(
                    [html.I(className="fas fa-sync mr-2"), _('Save & update')],
                    id=ids.BUTTON_EVENT_UPDATE,
                    className="btn btn-xs btn-primary my-3 mx-3",
                    hidden=hide_btn_event_update
                ),
            ], sm=12, md=12, lg=12),

            html.P(
                [html.I(className="fas fa-chevron-right mr-2"),
                 _('Order history and forecasts')],
                className='font-weight-bold text-primary my-3'
            ),

            dbc.Col([
                dcc.Loading(
                    dash_table.DataTable(
                        id=ids.DATABLE_FORECAST,
                        columns=forecast_columns,
                        data=forecast_data,
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

    return div, hide_btn_approve, hide_btn_reject, hide_btn_review, hide_btn_save


@app.callback(
    Output(ids.DATABLE_EVENTS, 'data'),
    [
        Input(ids.BUTTON_EVENT_ADD, 'n_clicks'),
    ],
    [
        State(ids.DATABLE_EVENTS, 'data'),
        State(ids.DATABLE_EVENTS, 'columns')
    ]
)
def add_row(n_clicks, rows, columns, * args, **kwargs):
    ''' Append new row to the datatable '''
    if n_clicks is not None:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    # [
    Output(ids.MODAL_DIV, 'is_open'),
    # ],   
    [
        Input(ids.BUTTON_SUBMIT_REVIEW, 'n_clicks'),
        Input(ids.MODAL_BUTTON_CLOSE, 'n_clicks')
    ],
    [
        State(ids.MODAL_DIV, 'is_open')
    ],
)
def toggle_modal(n_clicks_submit, n_clicks_close, is_open, * args, **kwargs):
    ''' Return the state of the modal '''
    
    body_div = html.Embed(
        src=VersionDetailView.as_view()),

    if n_clicks_submit or n_clicks_close:
        return not is_open
    return is_open


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


@app.callback(
    Output(ids.MESSAGE_SUCCESS_SENT_FOR_REVIEW, 'is_open'),
    [
        Input(ids.MODAL_BUTTON_SUBMIT, 'n_clicks'),
    ],
    [
        State(ids.MODAL_DROPDOWN_USER, 'value'),
    ],
)
def sent_for_review(n_clicks, value, * args, **kwargs):
    ''' Notify a user to approve the review request '''
    if n_clicks is not None:
        # Get version detail object
        versiondetail_id = kwargs['session_state']['dash_context']['versiondetail_id']
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)
        
        # Update the object
        approved_by_obj = get_object_or_404(CustomUser, pk=value)
        versiondetail_obj.created_by = kwargs['user']

        versiondetail_obj.approved_by = approved_by_obj
        versiondetail_obj.status = VersionDetail.SENT_FOR_REVIEW
        versiondetail_obj.save()
        
        
        return True
    return False
    
@app.callback(
    Output(ids.MESSAGE_APPROVE, 'is_open'),
    [
        Input(ids.BUTTON_APPROVE, 'n_clicks'),
    ],
)
def approve_review_request(approve_n_clicks, * args, **kwargs):
    ''' Approve the review request and change version detail status '''
    if approve_n_clicks is not None:
        # Get version detail object
        versiondetail_id = kwargs['session_state']['dash_context']['versiondetail_id']
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)
        # Update the object
        versiondetail_obj.status = VersionDetail.APPROVED
        versiondetail_obj.save()
        return True
    return False

@app.callback(
    Output(ids.MESSAGE_REJECT, 'is_open'),
    [
        Input(ids.BUTTON_REJECT, 'n_clicks'),
    ],
)
def reject_review_request(reject_n_clicks, * args, **kwargs):
    ''' Reject the review request and change version detail status '''
    if reject_n_clicks is not None:
        # Get version detail object
        versiondetail_id = kwargs['session_state']['dash_context']['versiondetail_id']
        versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)
        # Update the object
        versiondetail_obj.status = VersionDetail.REJECTED
        versiondetail_obj.save()
        return True
    return False


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
    # Get version detail object
    versiondetail_id = kwargs['session_state']['dash_context']['versiondetail_id']
    versiondetail_obj = get_object_or_404(VersionDetail, pk=versiondetail_id)

    # Get the dataframe
    monthly_forecast_df = pd.DataFrame(data, columns=[c['name'] for c in columns])
    monthly_forecast_df['date'] = pd.to_datetime(
        monthly_forecast_df['date'], errors='coerce')

    # Get the query with dispatched data by product, customer, day
    qs = Forecast.objects.filter(
        version=versiondetail_obj.version,
        product=versiondetail_obj.product,
        circuit=versiondetail_obj.circuit,
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
    # update version detail status
    versiondetail_obj.status = VersionDetail.CONFIRMED
    versiondetail_obj.save()

    return True

