# from ortools.sat.python import cp_model
from django.shortcuts import render
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic import TemplateView

import pandas as pd
import random

from django.utils.decorators import method_decorator
# from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect
from .forms import AddressForm


@method_decorator(login_required, name='dispatch')
class FormView(TemplateView):
    template_name = "deployment/form_test.html"


def form_handler(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddressForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/index/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddressForm()

    return render(request, 'deployment/form_test.html', {'form': form})



# Create your views here.
# def index(request):
#     df = read_frame(Product.objects.all())
#     return HttpResponse(df.to_html())


# decorators = [never_cache, login_required]

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = "deployment/deployment_dashboard.html"


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = "deployment/deployment_index.html"
    
    
    # def get_context_data(self, **kwargs):
    #     ############################

    #     def generate_data_array(label_prefix, length_unique, duplication_coefficient=1):
    #         data_array = []
    #         for i in range(length_unique):
    #             for n in range(duplication_coefficient):
    #                 data_array.append(f'{label_prefix}_{i}')
    #         return data_array

    #     def get_max_product_quantity(df, product):
    #         max_product_quantity = df.loc[df['product']
    #                                     == product, 'quantity'].to_numpy()

    #         # max_product_quantity = df.at[df['product'].eq(product).idxmax(),'quantity']
    #         return max_product_quantity[0]

    #     def get_min_order_quantity(df, product):
    #         moq = df.at[df['product'].eq(product).idxmax(), 'moq']
    #         return moq

    #     def get_lost_quantity(df, product, warehouse, all_days):
    #         # Get the data
    #         lost_turnover = df.loc[(df['product'] == product) & (
    #             df['warehouse'] == warehouse), all_days]
    #         # Convert to array and clip if positive
    #         lost_turnover = lost_turnover.to_numpy().clip(max=0)
    #         # Get absolute value
    #         lost_turnover = int(abs(lost_turnover.sum()))
    #         return lost_turnover

    #     ######################################################

    #     _num_products = 100
    #     _num_warehouses = 5
    #     _all_products = generate_data_array('sku', _num_products)
    #     _all_warehouses = generate_data_array('warehouse', _num_warehouses)
    #     _all_days = ['day_0', 'day_1', 'day_2', 'day_3']
    #     _max_pallet = 33
    #     _num_product_in_pallet = 100  # Assuming the variable is the same for all products

    #     _num_rows = len(_all_products) * len(_all_warehouses)
    #     _products_cost = 10  # Assuming all products have same cost

    #     cdc_warehouse_df = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products),
    #         'quantity': [random.randint(500, 5000) for i in range(_num_products)],
    #     })

    #     min_order_quantity_df = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products),
    #         'moq': [random.randint(1, 10) for i in range(_num_products)],
    #         'unit_size': '',

    #     })
    #     min_order_quantity_df['unit_size'] = min_order_quantity_df['moq']

    #     forecasting_data = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products) * _num_warehouses,
    #         'warehouse': generate_data_array('warehouse', _num_warehouses, duplication_coefficient=_num_products),
    #         'day_0': [random.randint(100, 500) for i in range(_num_products * _num_warehouses)],
    #         'day_1': [random.randint(100, 500) for i in range(_num_products * _num_warehouses)],
    #         'day_2': [random.randint(100, 500) for i in range(_num_products * _num_warehouses)],
    #         'day_3': [random.randint(100, 500) for i in range(_num_products * _num_warehouses)],
    #     })

    #     reception_data = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products) * _num_warehouses,
    #         'warehouse': generate_data_array('warehouse', _num_warehouses, duplication_coefficient=_num_products),
    #         'day_0': [random.randint(0, 100) for i in range(_num_products * _num_warehouses)],
    #         'day_1': [random.randint(0, 100) for i in range(_num_products * _num_warehouses)],
    #         'day_2': [random.randint(0, 100) for i in range(_num_products * _num_warehouses)],
    #         'day_3': [random.randint(0, 100) for i in range(_num_products * _num_warehouses)],
    #     })

    #     expedition_data = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products) * _num_warehouses,
    #         'warehouse': generate_data_array('warehouse', _num_warehouses, duplication_coefficient=_num_products),
    #         'day_0': [random.randint(0, 5) for i in range(_num_products * _num_warehouses)],
    #         'day_1': [random.randint(0, 5) for i in range(_num_products * _num_warehouses)],
    #         'day_2': [random.randint(0, 5) for i in range(_num_products * _num_warehouses)],
    #         'day_3': [random.randint(0, 5) for i in range(_num_products * _num_warehouses)],
    #     })

    #     image_stock_data = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products) * _num_warehouses,
    #         'warehouse': generate_data_array('warehouse', _num_warehouses, duplication_coefficient=_num_products),
    #         'day_0': [random.randint(-500, 1000) for i in range(_num_products * _num_warehouses)],
    #     })

    #     # simulated_stock_data
    #     #  DEP (p,e) not taken into consideration in this phase
    #     simulated_stock_data = pd.DataFrame({
    #         'product': generate_data_array('sku', _num_products) * _num_warehouses,
    #         'warehouse': generate_data_array('warehouse', _num_warehouses, duplication_coefficient=_num_products),
    #         'day_0': image_stock_data['day_0'].to_numpy().clip(min=0) +
    #         reception_data['day_0'] - expedition_data['day_0'] -
    #         forecasting_data['day_0'],
    #         'day_1': reception_data['day_1'] - expedition_data['day_1'] -
    #         forecasting_data['day_1'],
    #         'day_2': reception_data['day_2'] - expedition_data['day_2'] -
    #         forecasting_data['day_2'],
    #         'day_3': reception_data['day_3'] - expedition_data['day_3'] -
    #         forecasting_data['day_3'],
    #     })
    #     simulated_stock_data['day_1'] += simulated_stock_data['day_0'].to_numpy().clip(min=0)
    #     simulated_stock_data['day_2'] += simulated_stock_data['day_1'].to_numpy().clip(min=0)
    #     simulated_stock_data['day_3'] += simulated_stock_data['day_2'].to_numpy().clip(min=0)

    #     # Lost turnover
    #     lost_turnover_data = pd.DataFrame({
    #         'product': [],
    #         'warehouse': [],
    #         'day_0': [],
    #         'day_1': [],
    #         'day_2': [],
    #         'day_3': [],
    #     })
    #     lost_turnover_data['product'] = simulated_stock_data['product']
    #     lost_turnover_data['warehouse'] = simulated_stock_data['warehouse']
    #     lost_turnover_data['day_0'] = abs(
    #         simulated_stock_data['day_0'].to_numpy().clip(max=0)) * _products_cost
    #     lost_turnover_data['day_1'] = abs(
    #         simulated_stock_data['day_1'].to_numpy().clip(max=0)) * _products_cost
    #     lost_turnover_data['day_2'] = abs(
    #         simulated_stock_data['day_2'].to_numpy().clip(max=0)) * _products_cost
    #     lost_turnover_data['day_3'] = abs(
    #         simulated_stock_data['day_3'].to_numpy().clip(max=0)) * _products_cost

    #     ############################

    #     # Create the model
    #     ortools_model = cp_model.CpModel()

    #     # Create deployment variables
    #     # quantity_deployed_var[(p, w)]: product 'p' in warehouse 'w' on day 'd'
    #     quantity_deployed_var = {}
    #     _max_quantity = int(cdc_warehouse_df['quantity'].to_numpy().sum())

    #     for p in _all_products:
    #         for w in _all_warehouses:
    #             suffix = '_%s_%s' % (p, w)
    #             quantity_deployed_var[(p, w)] = ortools_model.NewIntVar(
    #                 0, _max_quantity, 'quantity_deployed' + suffix)

    #     # Define constraints
    #     # Constraint 0: the quantity of product 'p' to deploy in a warehouse should be more that the min_order_quantity
    #     for w in _all_warehouses:
    #         for p in _all_products:
    #             ortools_model.Add(quantity_deployed_var[(p, w)] >= get_min_order_quantity(
    #                 min_order_quantity_df, p))
    #     # Constraint 1: the quantity of product 'p' to deploy in a warehouse should be a multiple of the min_order_quantity
    #     for w in _all_warehouses:
    #         for p in _all_products:
    #             ortools_model.AddModuloEquality(0, quantity_deployed_var[(
    #                 p, w)], get_min_order_quantity(min_order_quantity_df, p))
    #             # ortools_model.AddModuloEquality(quantity_deployed_var[(p, w)] % get_min_order_quantity(min_order_quantity_df, p))
    #     # Constraint 2: the quantity of product 'p' to deploy in all warehouses should be less than the quantity available in centrale warehouse
    #     for p in _all_products:
    #         ortools_model.Add(sum(quantity_deployed_var[(
    #             p, w)] for w in _all_warehouses) <= get_max_product_quantity(cdc_warehouse_df, p))
    #     # Constraint 3: the number of pallets of all products to deploy in a warehouse should be less than the predefined value '_max_pallet'
    #     for w in _all_warehouses:
    #         ortools_model.Add(sum(quantity_deployed_var[(
    #             p, w)] for p in _all_products) <= _max_pallet * _num_product_in_pallet)

    #     # Define the objective
    #     # TODO get 'quantity_deployed_var' and use it in 'get_lost_quantity()' before clipping
    #     ortools_model.Maximize(
    #         sum(quantity_deployed_var[(p, w)] - get_lost_quantity(simulated_stock_data, p, w, _all_days) for p in _all_products
    #             for w in _all_warehouses))

    #     #####################""

    #     # Solve model.
    #     ortools_solver = cp_model.CpSolver()
    #     status = ortools_solver.Solve(ortools_model)

    #     warehouses_array = []
    #     products_array = []
    #     quantities_array = []

    #     if status == cp_model.OPTIMAL:
    #         print('The optimal solution for the problem has been found.')
    #         for w in _all_warehouses:
    #             for p in _all_products:
    #                 warehouses_array.append(w)
    #                 products_array.append(p)
    #                 quantities_array.append(ortools_solver.Value(
    #                     quantity_deployed_var[(p, w)]))

    #     elif status == cp_model.FEASIBLE:
    #         print('The problem has a feasible solution.')
    #         for w in _all_warehouses:
    #             for p in _all_products:
    #                 warehouses_array.append(w)
    #                 products_array.append(p)
    #                 quantities_array.append(ortools_solver.Value(
    #                     quantity_deployed_var[(p, w)]))

    #     elif status == cp_model.INFEASIBLE:
    #         print('The problem was proven infeasible.')

    #     elif status == cp_model.MODEL_INVALID:
    #         print('The given CpModelProto didn\'t pass the validation step.')

    #     elif status == cp_model.UNKNOWN:
    #         print('The status of the model is unknown because a search limit was reached.')

    #     output_df = pd.DataFrame({
    #         'warehouse': warehouses_array,
    #         'product': products_array,
    #         'quantity': quantities_array,
    #     })
    #     output_df['Gain'] = output_df['quantity'] * _products_cost
    #     output_df['Transport Cost'] = ""
    #     output_df['CDC Saturation'] = ""
    #     output_df['Warehouse Saturation'] = ""

    #     output_by_warehouse = output_df.groupby(['warehouse']).sum()


    #     context = super().get_context_data(**kwargs)
    #     # Statistics:
    #     context['statistics'] = {}
    #     context['statistics']['status'] = ortools_solver.StatusName()
    #     context['statistics']['num_products'] = _num_products
    #     context['statistics']['num_warehouses'] = _num_warehouses
    #     context['statistics']['max_quantity'] = _max_quantity
    #     context['statistics']['max_pallet'] = _max_pallet
    #     context['statistics']['num_product_in_pallet'] = _num_product_in_pallet
    #     context['statistics']['new_objective_value'] = abs(ortools_solver.ObjectiveValue())
    #     context['statistics']['old_objective_value'] = sum(
    #         lost_turnover_data.sum(axis=1, skipna=True).to_numpy())
    #     context['statistics']['walltime'] = ortools_solver.WallTime()

    #     context['df'] = {}
    #     context['df']['cdc_warehouse_df'] = cdc_warehouse_df.head(
    #         n=20).to_html()
    #     context['df']['min_order_quantity_df'] = min_order_quantity_df.head(
    #         n=20).to_html()
    #     context['df']['forecasting_data'] = forecasting_data.head(
    #         n=20).to_html()
    #     context['df']['reception_data'] = reception_data.head(
    #         n=20).to_html()
    #     context['df']['expedition_data'] = expedition_data.head(
    #         n=20).to_html()
    #     context['df']['image_stock_data'] = image_stock_data.head(
    #         n=20).to_html()
    #     context['df']['simulated_stock_data'] = simulated_stock_data.head(
    #         n=20).to_html()
    #     context['df']['lost_turnover_data'] = lost_turnover_data.head(
    #         n=20).to_html()
    #     context['df']['output_df'] = output_df.to_html()
    #     context['df']['output_by_warehouse'] = output_by_warehouse.to_html()

    #     context['page_elements'] = {}
    #     context['page_elements']['page_title'] = 'Deployment'

    #     return context
