import time
from fbprophet import Prophet
from django_pandas.io import read_frame
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from forecasting.models import Version, VersionDetail, Forecast
from stock.models import OrderDetail
from datetime import date, datetime, timedelta


class Command(BaseCommand):
    help = "Generate auto forecast for all {product, day, customer} or for a specific {product, day, customer} as argument"

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--product',
            type=int,
            help='Manually select the product to which the forecast should be generated.',
        )
        parser.add_argument(
            '-c', '--circuit',
            type=int,
            help='Manually select the circuit to which the forecast should be generated.',
        )
        parser.add_argument(
            '-d', '--version_date',
            type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
            help='Manually specify the version date.',
        )


    def handle(self, *args, **kwargs):
        def _get_forecasts(df, holidays=None, add_country_holidays=None, forecast_periods=30*1,
                          freq='D', include_history=False, floor=None, cap=None,
                          forecast_fig=False, components_fig=False):
            ''' return trained model and forecasted data. Adds charts to the results if figures flags are true '''
            # Model settings
            # m = Prophet(holidays=holidays, growth='logistic',
            #             seasonality_mode='multiplicative')
            m = Prophet() # TODO use the abbove commented version

            # Add default holidays of a country to the model
            if add_country_holidays:
                m.add_country_holidays(country_name=add_country_holidays)
                # print('Holidays taking into conciderations are:')
                # print(m.train_holiday_names)
            
            m.fit(df)

            # Make dataframe with future dates for forecasting
            future = m.make_future_dataframe(
                periods=forecast_periods, freq=freq, include_history=include_history)
            # future['cap'] = cap
            # future['floor'] = floor

            forecast = m.predict(future)
            # Clip values to zero
            forecast['yhat'] = forecast['yhat'].clip(0)
            # forecast['yhat_lower'] = forecast['yhat_lower'].clip(floor)
            # Round values to get integers
            forecast['yhat'] = forecast['yhat'].round()
            # forecast = forecast.astype({'yhat': int})
            return forecast
        
        start_time = time.time()
        # Parameters
        _delta_years = 2
        # _floor = 0
        # _cap = 1000000
        _forecast_periods = 30*3
        _freq = 'D'

        # Date range to consider for calculation (last delta years)
        start_date = datetime.today() - timedelta(days=_delta_years*365)

        # Get the queryset
        qs = OrderDetail.objects.filter(
            order__ordered_at__gte=start_date,
        )
        qs = qs.values('product__id', 'customer__id', 'customer__circuit__id',
                        'order__ordered_at', 'ordered_quantity')
        
        # Convert qs to dataframe
        df = read_frame(qs)

        # # Format
        # df = df.astype({'ordered_quantity': int})

        # Rename columns and match Prophet input
        df = df.rename(columns={
            'product__id': 'product', 
            'customer__id': 'customer',
            'customer__circuit__id': 'circuit',
            'order__ordered_at': 'ds',
            'ordered_quantity': 'y',
        })
        print('original df', df)

        # Get all products & customers
        _all_products = df['product'].unique()
        _all_customers = df['customer'].unique()
        _all_circuits = df['circuit'].unique()

        # TODO The following line is used to filter the df and keep 1 selected circuit
        # FIXME DELETE
        # top_customer_df = df.groupby(
        #     by=['customer', 'product', 'ds'],
        #     as_index=False
        # ).agg({
        #     'y': 'count',
        # }).reset_index(
        # ).sort_values(
        #     by=['y'],
        #     ascending = True,
        #     # na_position = 'first',
        # )
        # top_customer_df = top_customer_df['customer'].unique()[:2000]


        # top_customer_df = df[].groupby(
        #     ['customer', 'product', 'ds'])['customer']
        # top_customer_df = top_customer_df.size().nlargest(200).reset_index(name='top_customer')
        # top_customer_df = top_customer_df['top_customer'].unique()
        top_customer_list = df['customer'].value_counts()[:10000].index.tolist()

        print('top_customer_df\n', top_customer_list)

        selected_products = [
            263667938973738,
            258791003609130,
            267997250279466,
            258786675087402,
            250062489212970,
            254457348053034,
            276859897468970,
            259201172985898,
            245808374437930,
            263469279959082,
            263810798016554,
            272053829064746,
            254873993435178,
            258796355541034,
            245670935484458,
            250266601610023,
            245868471998506,
            276791177992234,
            259412751505450,
        ]

        df = df[(
            # (df['circuit'] == 4686550636307245) &
            # (df['customer'].isin(top_customer_list)) &
            (df['product'].isin(selected_products)) 
            # (df['ds'] < date(2020, 11, 11))
        )]
        print('df length', df)


        # Create a version for this forecast
        if kwargs['version_date']:
            version_date = kwargs['version_date']
        else:
            version_date = datetime.today()

        version_date = version_date.replace(day=1)
        _forecast_types = Version._meta.get_field('forecast_type').choices
        _reference = version_date.strftime(
            '%Y%m%d') + '_' + _forecast_types[0][0]

        self.stdout.write('Creating version %s...' % (_reference))
        version_obj, _ = Version.objects.get_or_create(
            reference=_reference,
            forecast_type=_forecast_types[0][0],  # forecast_type = 'Automatic'
            version_date=version_date,
            description='TST product=259201172985898 circuit=89146453190069900 all customers (min_data>3)',
            # defaults={

            # },
        )
        self.stdout.write(self.style.SUCCESS(
            'Version %s created' % (version_obj.reference)))

        # Add created version to dataframe
        version_id = version_obj.pk

        products_with_existing_forecast = Forecast.objects.filter(
            version=version_obj).order_by().values_list('product__id', flat=True).distinct()
        self.stdout.write(self.style.NOTICE(
            'Forecasts for the following products already exist: %s' % (products_with_existing_forecast)))

        # Init counters
        _added_forecasts = 0
        _skipped_forecasts = 0
        # Run Prophet model on all {product, customer} combinaison
        for p in list(set(_all_products) - set(products_with_existing_forecast)):
            _bulk_forecast = []
            _forecasted_circuit_id = []

            customer_list_df = df.loc[(df['product'] = p) & (df['y'] > 0)]
            customer_list_df['count_days'] = 0
            customer_list_df = customer_list_df.groupby(
                by=['customer', 'ds'],
                as_index=False
            ).agg({
                'count_days': 'sum',
                'product': 'first',
                'circuit': 'first',
            }).reset_index().sort_values(
                by=['ds'],
                ascending=False,
            )
            customer_list_df = customer_list_df.groupby(
                by=['customer'],
                as_index=False
            ).agg({
                'count_days': 'count',
                'product': 'first',
                'circuit': 'first',
            }).reset_index().sort_values(
                by=['customer'],
                ascending=False,
            )

            customer_list_df = customer_list_df.loc[(
                customer_list_df['count_days'] > 2)]

            customer_positive_list = customer_list_df['customer'].tolist()
            print('List of customers with data > 2: \n', customer_positive_list)

            # [:min(len(_all_customers), 200)]:
            for c in list(set(_all_customers) & set(customer_positive_list)):
                # Extract filtered data as dataframe
                sub_df = df.loc[(df['product'] == p) & (df['customer'] == c)]
                # Group df by date and aggreate values (sum)
                sub_df = sub_df.groupby(
                    by='ds',
                    as_index=False
                ).agg({
                    'y': 'sum',
                    'product': 'first',
                    'customer': 'first',
                    'circuit': 'first',
                }).reset_index()

                # Fit the model if dataframe length > future forecast dates
                if len(sub_df.index) >= 2:#_forecast_periods:
                    print('sub_df\n', sub_df)
                    # Get circuit id
                    circuit_id = sub_df['circuit'].iloc[0] # TODO you can simply use 'c' variable instead if customer classification won't be used
                    # # Add floor and cap values (NOTE assuming it is a fixed value)
                    # sub_df['floor'] = _floor
                    # sub_df['cap'] = _cap

                    # Get the forecasts
                    # TODO change forecast to forecast_df
                    forecast = _get_forecasts(sub_df[['ds', 'y']], holidays=None, add_country_holidays='MA', forecast_periods=_forecast_periods,
                                   freq=_freq, include_history=False, floor=None, cap=None,
                                    forecast_fig=False, components_fig=False)
                    # Bulk update classification in database
                    forecasts = [
                        Forecast(
                            version_id=version_id,
                            product_id=p,
                            customer_id=c,
                            circuit_id=circuit_id,
                            forecast_date=row['ds'],
                            forecasted_quantity=row['yhat'],
                            edited_forecasted_quantity=row['yhat'],
                        )
                        for i, row in forecast.iterrows()
                    ]
                    _bulk_forecast.extend(forecasts)
                    
                    # Count up
                    _added_forecasts += 1

                    # Append circuit
                    if circuit_id not in _forecasted_circuit_id:
                        _forecasted_circuit_id.append(circuit_id)


                    self.stdout.write(
                        'Forecasts for [product: %s, customer: %s] is added to the batch with version %s' % (p, c, version_id))

                else:
                    # Count up
                    _skipped_forecasts += 1

                    self.stdout.write(self.style.WARNING(
                        'Forecasts for [product: %s, customer: %s] is skipped because of insufficient data' %(p, c)))
                
                self.stdout.write(
                    'Total added forecasts so far = %s' % (_added_forecasts))
                self.stdout.write(
                    'Total skipped forecasts so far = %s' % (_skipped_forecasts))

        
            # Bulk create for the product
            self.stdout.write('Runing bulk creation of forecasts for product %s' % (p))
            Forecast.objects.bulk_create(_bulk_forecast)

            # Bulk create version detail
            self.stdout.write(
                'Runing bulk creation of version detail for version: %s, product: %s, circuits %s' % (version_id, p, ','.join(str(x) for x in _forecasted_circuit_id)))
            _version_detail_objects = [
                VersionDetail(
                    version_id=version_id,
                    product_id=p,
                    circuit_id=c,
                )
                for c in _forecasted_circuit_id
            ]
            VersionDetail.objects.bulk_create(_version_detail_objects)
        
        self.stdout.write(self.style.SUCCESS(
            '%s forecasts are saved successfully in %s sec . %s forecasts skipped cause of insufficient data' % (_added_forecasts, time.time()-start_time, _skipped_forecasts)))


