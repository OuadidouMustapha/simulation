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

from account.models import CustomUser

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from .components import helpers
from .components import deployment_alg


@app.callback(
    [
        Output(ids.DATATABLE_DEPLOYMENT, 'data'),
        Output(ids.DATATABLE_DEPLOYMENT, 'columns'),
        Output(ids.MESSAGE_SUCCESS, 'is_open'),
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
        # truckavailability_df, truck_assignment_df = deployment_alg.run_deployment(
        #     show_by, start_date, end_date)
        # truckavailability_df.to_csv('tmp/truckavailability_df.csv')
        # truck_assignment_df.to_csv('tmp/truck_assignment_df.csv')
        truckavailability_df = pd.read_csv('tmp/truckavailability_df.csv')
        truck_assignment_df = pd.read_csv('tmp/truck_assignment_df.csv')

        data = truck_assignment_df.to_dict('records')
        columns = [{"name": i, "id": i} for i in truck_assignment_df.columns]

        # Show success message
        is_open = True
        return data, columns, is_open


