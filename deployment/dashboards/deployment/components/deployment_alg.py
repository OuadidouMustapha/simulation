import pandas as pd
import numpy as np
import random
import timeit
from datetime import datetime, timedelta
import math
from forecasting.models import Forecast
from stock.models import Product
from deployment.models import TruckAvailability
from inventory.models import StockCheck
from django_pandas.io import read_frame


def get_truck_type_by_product_type(product_type):
    table = {
        'Food': 1,
        'Non Food': 2,
    }
    return int(table[product_type])


def run_deployment(version_id, show_by, start_date, end_date):
    model_start = timeit.default_timer()


    PARAM_SAVE_DATA = False


    version_id = 22
    check_date = '2021-01-25'

    # Get queries
    product_qs = Product.objects.all()

    forecast_qs = Forecast.objects.filter(version__id=version_id)
    forecast_qs = forecast_qs.values(
        'id', 'forecast_date', 'forecasted_quantity', 'edited_forecasted_quantity', 'product', 'circuit', 'customer', 'customer__warehouse', 'version')
        
    stockcheck_qs = StockCheck.objects.filter(check_date=check_date).values(
        'id', 'product', 'check_date', 'warehouse', 'warehouse__warehouse_type', 'quantity')

    truckavailability_qs = TruckAvailability.objects.values(
        'id', 'warehouse', 'available_truck', 'category__capacity', 'category__cost', 'category__truck_type')
    # Get dataframes
    product_df = read_frame(product_qs)
    forecast_df = read_frame(forecast_qs)
    stockcheck_df = read_frame(stockcheck_qs)
    truckavailability_df = read_frame(
        truckavailability_qs)

    # Format
    truckavailability_df['category__truck_type'] = truckavailability_df['category__truck_type'].astype('int32')



    # Rename
    product_df = product_df.rename(columns={
        'id': 'product',
    })
    forecast_df = forecast_df.rename(columns={
        'forecast_date': 'date',
        'customer__warehouse': 'warehouse',
        # 'product': 'product',
    })
    stockcheck_df = stockcheck_df.rename(columns={
        # 'product': 'product',
        # 'warehouse': 'warehouse',
        'warehouse__warehouse_type': 'warehouse_type',
        'check_date': 'date',
    })
    truckavailability_df = truckavailability_df.rename(columns={
        'id': 'truckavailability_id',
        # 'warehouse': 'warehouse',
    })
    # Column type
    forecast_df['date'] = pd.to_datetime(forecast_df['date']).dt.date
    stockcheck_df['date'] = pd.to_datetime(stockcheck_df['date']).dt.date

    _cdc_warehouses = stockcheck_df[stockcheck_df['warehouse_type']
                                    == 'CDC']['warehouse'].unique()
    _all_dates = forecast_df['date'].unique()
    _check_date = _all_dates[0]
    _all_products = stockcheck_df['product'].unique()
    _all_warehouses_rdc = stockcheck_df[stockcheck_df['warehouse_type']
                                        == 'RDC']['warehouse'].unique()


    # init dataframe
    stock_warehouse_rdc_df = pd.DataFrame(
        columns=['warehouse', 'product', 'date', 'simulated_stock_quantity_rdc', 'required_quantity_rdc'])

    ##########################################################################
    # STEP 1 new:
    # Get a copy of forecasting data based on the selection filter
    # TODO Add filter to delete rows where no image de stock
    stock_warehouse_rdc_df = forecast_df[
        (forecast_df['forecasted_quantity'] != 0) &
        (forecast_df['warehouse'].isin(_all_warehouses_rdc)) &
        (forecast_df['product'].isin(_all_products)) &
        (forecast_df['date'].isin(_all_dates) &
         (forecast_df['date'] >= _check_date))
    ]

    stock_warehouse_rdc_df = pd.merge(
        stock_warehouse_rdc_df,
        stockcheck_df[['warehouse', 'product', 'quantity']],
        on=['warehouse', 'product'],
        how='left'
    )


    # Rename image de stock column
    stock_warehouse_rdc_df = stock_warehouse_rdc_df.rename(
        columns={'quantity': 'image_stock_rdc'})
    stock_warehouse_rdc_df.loc[stock_warehouse_rdc_df['date']
                            != _check_date, 'image_stock_rdc'] = 0

    # Add reception quantity column (null for now)
    stock_warehouse_rdc_df['reception_quantity'] = 0

    # Sort dataframe
    stock_warehouse_rdc_df = stock_warehouse_rdc_df.sort_values(
        by=['warehouse', 'product', 'date'], ascending=[True, True, True]).reset_index(drop=True)

    # Calculate data_value
    stock_warehouse_rdc_df['data_value'] = 0
    # TODO used for testing. To be deleted
    stock_warehouse_rdc_df['data_value_i-1'] = np.nan


    # Do the calculation
    # create empty dataframe
    concat_stock_warehouse_rdc_df = pd.DataFrame(
        columns=stock_warehouse_rdc_df.columns)
    for w in _all_warehouses_rdc:
        for p in _all_products:
            sub_stock_warehouse_rdc_df = stock_warehouse_rdc_df[
                (stock_warehouse_rdc_df['warehouse'] == w) &
                (stock_warehouse_rdc_df['product'] == p)
            ].reset_index()

            for i in sub_stock_warehouse_rdc_df.index:
                # Check if data_value is NaN (if not NaN this means that the date is d0)
                # FIXME maybe consider using a condition based on the date
                sub_stock_warehouse_rdc_df.at[i, 'data_value'] = sub_stock_warehouse_rdc_df.at[i, 'forecasted_quantity'] - \
                    sub_stock_warehouse_rdc_df.at[i, 'reception_quantity']
                if i == 0:
                    # NOTE image_stock_rdc=nan if date!=date[0]
                    sub_stock_warehouse_rdc_df.at[i, 'data_value'] += - \
                        sub_stock_warehouse_rdc_df.at[i, 'image_stock_rdc']
                else:
                    sub_stock_warehouse_rdc_df.at[i,
                                                'data_value_i-1'] = sub_stock_warehouse_rdc_df.at[i-1, 'data_value']
                    # If data_value(j-1) > 0 then
                    sub_stock_warehouse_rdc_df.at[i, 'data_value'] += min(
                        sub_stock_warehouse_rdc_df.at[i-1, 'data_value'], 0)

            # Append to dataframe

            concat_stock_warehouse_rdc_df = pd.concat(
                [concat_stock_warehouse_rdc_df, sub_stock_warehouse_rdc_df])


    # Get simulated stock & required quantity columns

    stock_warehouse_rdc_df = concat_stock_warehouse_rdc_df
    stock_warehouse_rdc_df['simulated_stock_quantity_rdc'] = abs(
        stock_warehouse_rdc_df['data_value'].clip(None, 0))
    stock_warehouse_rdc_df['required_quantity_rdc'] = stock_warehouse_rdc_df['data_value'].clip(
        0, None)


    model_stop = timeit.default_timer()
    print('Step 1.2 [Update dataframes] - Done in ', model_stop-model_start)

    # Save data
    time_save_date = timeit.default_timer()
    if PARAM_SAVE_DATA:
        writer = pd.ExcelWriter('step1.xlsx', engine='xlsxwriter')
        product_df.to_excel(writer, sheet_name='product_df')
        stockcheck_df.to_excel(writer, sheet_name='stockcheck_df')
        forecast_df.to_excel(writer, sheet_name='forecast_df')
        truckavailability_df.to_excel(writer, sheet_name='truckavailability_df')
        # reception_df.to_excel(writer, sheet_name='reception_df')
        stock_warehouse_rdc_df.to_excel(
            writer, sheet_name='stock_warehouse_rdc_df')
        writer.save()
        model_stop = timeit.default_timer()
        print('Step 1 - Done in {} including {} for saving the data'.format(model_stop -
                                                                            model_start, model_stop-time_save_date))


    ##########################################################################
    ############################# STEP 2:
    model_start = timeit.default_timer()

    # Get available quantity of cdc warehouse from stockcheck_df
    available_stock_cdc_df = stockcheck_df[(
        stockcheck_df['warehouse'].isin(_cdc_warehouses))]
    # Rename column
    available_stock_cdc_df = available_stock_cdc_df.rename(
        columns={'warehouse': 'cdc_warehouse', 'quantity': 'initial_cdc_quantity', 'date': 'check_date'})

    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.1 - Done in ', model_stop-model_start)
    ###########

    # Merge needed columns from other dataframes
    deployment_df = pd.merge(stock_warehouse_rdc_df, product_df[[
                            'product', 'product_type', 'profit_margin', 'pallet_size', 'unit_size']], on=['product'])

    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.2 - Done in ', model_stop-model_start)
    ###########

    deployment_df = pd.merge(deployment_df, available_stock_cdc_df, on=['product'])

    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.3 - Done in ', model_stop-model_start)
    ###########

    # Convert added columns to int
    deployment_df = deployment_df.astype(
        {'pallet_size': int, 'unit_size': int, 'initial_cdc_quantity': int, 'profit_margin': float})
    deployment_df['required_quantity_rdc'] = deployment_df['required_quantity_rdc'].astype(
        int)


    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.4 - Done in ', model_stop-model_start)
    ###########

    # Add sum_required_quantity_rdc column
    deployment_grouped_by_product_df = deployment_df[['product', 'required_quantity_rdc']].groupby(
        ['product']).agg({'required_quantity_rdc': 'sum'})
    # Rename column
    deployment_grouped_by_product_df = deployment_grouped_by_product_df.rename(
        columns={'required_quantity_rdc': 'sum_required_quantity_rdc'})
    # Merge dataframes to copy sum_required_quantity_rdc column
    deployment_df = pd.merge(deployment_df, deployment_grouped_by_product_df,
                            left_on='product', right_on='product', how='left')


    # for i in deployment_df.index:
    #     product_value = deployment_df.at[i, 'product']
    #     deployment_df.at[i, 'sum_required_quantity_rdc'] = 1500 #deployment_df.loc[deployment_df['product'] == product_value, 'required_quantity_rdc'].sum()

    model_stop = timeit.default_timer()
    print('Step 2.1 [before computation] - Done in ', model_stop-model_start)

    # Compute deployement by unit
    deployment_by_unit_1 = (
        (
            deployment_df['initial_cdc_quantity'] *
            deployment_df['required_quantity_rdc']
        ).div(
            deployment_df['unit_size'] * deployment_df['sum_required_quantity_rdc']
        )
    ).apply(np.floor)

    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.5 - Done in ', model_stop-model_start)
    ###########

    deployment_by_unit_2 = (
        (
            deployment_df['required_quantity_rdc']
        ).div(
            deployment_df['unit_size']
        )
    ).apply(np.ceil)

    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.6 - Done in ', model_stop-model_start)
    ###########
    deployment_df['deployment_by_unit'] = np.minimum(
        deployment_by_unit_1, deployment_by_unit_2)
    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.7 - Done in ', model_stop-model_start)
    ###########
    deployment_df['deployment_by_pallet'] = deployment_df['deployment_by_unit'] * \
        deployment_df['unit_size'] / deployment_df['pallet_size']
    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.8 - Done in ', model_stop-model_start)
    ###########
    deployment_df['required_quantity_rdc_after_deployment'] = deployment_df['required_quantity_rdc'] - \
        deployment_df['deployment_by_unit'] * deployment_df['unit_size']
    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.9 - Done in ', model_stop-model_start)
    ###########

    # Add sum_deployment_by_unit column
    deployment_by_unit_sum_df = deployment_df[['product', 'deployment_by_unit']].groupby(
        ['product']).agg({'deployment_by_unit': 'sum'})
    # Rename column
    deployment_by_unit_sum_df = deployment_by_unit_sum_df.rename(
        columns={'deployment_by_unit': 'sum_deployment_by_unit'})
    # Merge dataframes to copy the aggreagated column
    deployment_df = pd.merge(deployment_df, deployment_by_unit_sum_df,
                            left_on='product', right_on='product', how='left')

    # Get available quantity after deployment
    deployment_df['available_cdc_after_deployment'] = deployment_df['initial_cdc_quantity'] - \
        deployment_df['sum_deployment_by_unit'] * deployment_df['unit_size']


    # for i in deployment_df.index:
    #     product_value = deployment_df.at[i, 'product']
    #     deployment_df.at[i, 'available_cdc_after_deployment'] = deployment_df.at[i, 'initial_cdc_quantity'] - deployment_df.loc[deployment_df['product'] == product_value, 'deployment_by_unit'].sum() * deployment_df.at[i, 'unit_size']

    ###########
    model_stop = timeit.default_timer()
    print('Step TEST.10 - Done in ', model_stop-model_start)
    ###########
    # Replace infinity values with NaN
    deployment_df = deployment_df.replace([np.inf, -np.inf], np.nan)


    model_stop = timeit.default_timer()
    print('Step 2.1 [after computation] - Done in ', model_stop-model_start)


    # Save data
    PARAM_SAVE_DATA = False

    time_save_date = timeit.default_timer()
    if PARAM_SAVE_DATA:

        writer = pd.ExcelWriter('step2.xlsx', engine='xlsxwriter')
        product_df.to_excel(writer, sheet_name='product_df')
        stockcheck_df.to_excel(writer, sheet_name='stockcheck_df')
        forecast_df.to_excel(writer, sheet_name='forecast_df')
        truckavailability_df.to_excel(writer, sheet_name='truckavailability_df')
        # reception_df.to_excel(writer, sheet_name='reception_df')
        stock_warehouse_rdc_df.to_excel(
            writer, sheet_name='stock_warehouse_rdc_df')
        deployment_df.to_excel(writer, sheet_name='deployment_df')

        writer.save()

    model_stop = timeit.default_timer()
    print('Step 2 - Done in {} including {} for saving the data'.format(model_stop -
                                                                        model_start, model_stop-time_save_date))

    ##########################################################################
    ############################# STEP 3:
    model_start = timeit.default_timer()
    # Sort dataframe
    deployment_df = deployment_df.sort_values(by=['warehouse', 'date', 'profit_margin'], ascending=[
                                            True, True, False]).reset_index(drop=True)

    # Add usefull columns to dataframes
    deployment_df['remaining_quantity_pallet'] = deployment_df['deployment_by_pallet'].astype(
        float)  # TODO delete coefficient
    deployment_df['status'] = ''

    truckavailability_df['remaining_capacity'] = truckavailability_df['category__capacity'].astype(
        float)
    truckavailability_df['status'] = 'unused'
    truckavailability_df['product_type'] = ''

    # Init dataframes
    truck_assignment_df = pd.DataFrame()
    final_deployment_df = pd.DataFrame()
    final_truckavailability_df = pd.DataFrame()

    _all_warehouses_rdc = deployment_df['warehouse'].unique()
    # _all_products_type = deployment_df['product_type'].unique()
    _capacity_threshold = 98/100
    _min_truck_split = 1/100

    # Filter out rows with deployment quantity null or undefined
    deployment_df = deployment_df[(deployment_df['deployment_by_pallet'] > 0)]
    for w in _all_warehouses_rdc:
        print('w = ', w)
        # for pt in _all_products_type: # _random function
        #     prinabst('pt de truck = ', pt)

        for di in deployment_df[(deployment_df['warehouse'] == w)].index:
            product_type = deployment_df.at[di, 'product_type']
            # Get trucks from selected warehouse not full and compatible with the product type
            conditional_truckavailability_df = truckavailability_df[
                (truckavailability_df['warehouse'] == w) &
                (truckavailability_df['category__truck_type'] == get_truck_type_by_product_type(product_type)) &
                (truckavailability_df['status'] != 'full') &
                (truckavailability_df['product_type'].isin([product_type, None, '']))
            ]
            for ti in conditional_truckavailability_df.index:
                if truckavailability_df.at[ti, 'remaining_capacity'] >= deployment_df.at[di, 'remaining_quantity_pallet']:
                    # Update truck capacity
                    truckavailability_df.at[ti, 'remaining_capacity'] -= deployment_df.at[di,
                                                                                        'remaining_quantity_pallet']
                    # Update truck's product type if not already filled
                    truckavailability_df.at[ti, 'product_type'] = product_type if truckavailability_df.at[ti,
                                                                                                        'product_type'] else product_type
                    # Append row to truck_assignement
                    truck_assignment_columns = ['truckavailability_id', 'category__truck_type', 'warehouse', 'product',
                                                'product_type', 'date', 'pallet_size', 'deployed_quantity', 'full_capacity', 'remaining_capacity']
                    truck_assignment_list = [
                        truckavailability_df.at[ti, 'truckavailability_id'],
                        truckavailability_df.at[ti, 'category__truck_type'],
                        deployment_df.at[di, 'warehouse'],
                        deployment_df.at[di, 'product'],
                        deployment_df.at[di, 'product_type'],
                        deployment_df.at[di, 'date'],
                        deployment_df.at[di, 'pallet_size'],
                        # In this case it is the quantity deployed
                        deployment_df.at[di, 'remaining_quantity_pallet'],
                        truckavailability_df.at[ti, 'category__capacity'],
                        # Capacity already updated
                        truckavailability_df.at[ti, 'remaining_capacity'],
                    ]
                    truck_assignment_row = pd.DataFrame(
                        [truck_assignment_list], columns=truck_assignment_columns)
                    truck_assignment_df = pd.concat(
                        [truck_assignment_df, truck_assignment_row])

                    # Update remaining quantity to deploy
                    deployment_df.at[di, 'remaining_quantity_pallet'] = 0

                    # Change status in dataframes
                    truckavailability_df.at[ti, 'status'] = 'used'
                    deployment_df.at[di, 'status'] = 'assigned'

                    # Go to next deployment_df row
                    break

                else:  # remaining_capacity < deployment_by_pallet
                    # Check if % of available/remaining capacity in the truck > x% total capacity
                    available_capacity_value = truckavailability_df.at[ti, 'remaining_capacity'] - \
                        truckavailability_df.at[ti, 'category__capacity'] * \
                        (1 - _capacity_threshold + _min_truck_split)

                    if available_capacity_value > 0:
                        # Update truck capacity
                        truckavailability_df.at[ti,
                                                'remaining_capacity'] -= available_capacity_value

                        # Update remaining quantity to deploy
                        deployment_df.at[di,
                                        'remaining_quantity_pallet'] -= available_capacity_value
                        # Update truck's product type if not already filled
                        truckavailability_df.at[ti, 'product_type'] = product_type if truckavailability_df.at[ti,
                                                                                                            'product_type'] else product_type
                        # Append row to truck_assignement
                        truck_assignment_columns = ['truckavailability_id', 'category__truck_type', 'warehouse', 'product',
                                                    'product_type', 'date', 'pallet_size', 'deployed_quantity', 'full_capacity', 'remaining_capacity']
                        truck_assignment_list = [
                            truckavailability_df.at[ti, 'truckavailability_id'],
                            truckavailability_df.at[ti, 'category__truck_type'],
                            deployment_df.at[di, 'warehouse'],
                            deployment_df.at[di, 'product'],
                            deployment_df.at[di, 'product_type'],
                            deployment_df.at[di, 'date'],
                            deployment_df.at[di, 'pallet_size'],
                            available_capacity_value,
                            truckavailability_df.at[ti, 'category__capacity'],
                            # Capacity already updated
                            truckavailability_df.at[ti, 'remaining_capacity'],
                        ]
                        truck_assignment_row = pd.DataFrame(
                            [truck_assignment_list], columns=truck_assignment_columns)
                        truck_assignment_df = pd.concat(
                            [truck_assignment_df, truck_assignment_row])

                        # Change status in dataframes
                        truckavailability_df.at[ti, 'status'] = 'full'
                        deployment_df.at[di, 'status'] = 'partially assigned'

                        # Go to next truckavailability_df row (for the same deployment_df row)
                        continue

                    else:  # available_capacity_value <= 0
                        # Change status in dataframes
                        truckavailability_df.at[ti, 'status'] = 'full'

                        # Go to next truckavailability_df row (for the same deployment_df row)
                        continue


    model_stop = timeit.default_timer()
    print('Step 3.1 [after computation] - Done in ', model_stop-model_start)
    print('truck_assignment_df\n', truck_assignment_df)

    # Save data
    time_save_date = timeit.default_timer()
    PARAM_SAVE_DATA = False
    if PARAM_SAVE_DATA:
        writer = pd.ExcelWriter('step3.xlsx', engine='xlsxwriter')
        deployment_df.to_excel(writer, sheet_name='deployment_df')
        truckavailability_df.to_excel(writer, sheet_name='truckavailability_df')
        truck_assignment_df.to_excel(writer, sheet_name='truck_assignment_df')
        writer.save()

    model_stop = timeit.default_timer()
    print('Step 3 - Done in {} including {} for saving the data'.format(model_stop -
                                                                        model_start, model_stop-time_save_date))

    return truckavailability_df, truck_assignment_df
