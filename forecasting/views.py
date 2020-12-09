# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import PermissionRequiredMixin
import logging
from django.core.exceptions import ObjectDoesNotExist
from account.models import CustomUser
from django.views.generic.edit import FormMixin
import locale
from django.core.paginator import Paginator
from django.http import JsonResponse
from django_pandas.io import read_frame
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as py

from django_tables2.views import SingleTableMixin
from .filtersets import VersionFilter, ForecastFilter
from django_filters.views import FilterView
from extra_views import SearchableListMixin
from tablib import Dataset
from django.contrib import messages
import os
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory, ModelFormSetView
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.views import View
from django.urls import reverse, reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import Forecast, Version
from .forms import ForecastForm
from stock.models import Warehouse, Product, ProductCategory, Order, Delivery, Customer, Circuit
from .resources import ForecastResource
from import_export.forms import ConfirmImportForm, ImportForm
from django.template.response import TemplateResponse
import tempfile
from django.utils.encoding import force_text

from import_export.formats import base_formats
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from .forms import VersionForm, VersionReviewForm
# from .forms import VersionFilterFormHelper
from .tables import VersionTable, ForecastTable
from django.db.models import Count
from datetime import datetime

from django.db.models import OuterRef, Subquery

# Get an instance of a logger
logger = logging.getLogger(__name__)

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'forecasting/index.html'

# class InputInterfaceView(LoginRequiredMixin, TemplateView):
#     template_name = 'forecasting/input_interface.html'


class ForecastAccuracyView( TemplateView):
    # Add this mixin "PermissionRequiredMixin" for permission
    # permission_required = 'forecasting.validate_version'

    # model = Forecast
    # queryset = Forecast.objects.get_forecast_accuracy(OrderDetail)
    template_name = 'forecasting/stock_forecast_accuracy.html'
    # context_object_name = 'stock_forecast_accuracy_list'
    # paginate_by = 20

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     session = self.request.session

    #     demo_count = session.get('django_plotly_dash', {})
    #     ind_use = demo_count.get('ind_use', 0)
    #     ind_use += 1
    #     demo_count['ind_use'] = ind_use
    #     session['django_plotly_dash'] = demo_count



    #     # context['stock_forecast_order'] = Forecast.objects.get_forecast_accuracy(
    #     #     OrderDetail)
    #     context['page_elements'] = {}
    #     context['page_elements']['page_title'] = 'Forecast Accuracy'
    #     context['page_elements']['table_title'] = 'Forecast Accuracy Table'

    #     return context


class ForecastAccuracyMadecView(LoginRequiredMixin, TemplateView):
    template_name = 'forecasting/stock_forecast_accuracy_madec.html'

class ForecastAccuracyV1View(LoginRequiredMixin, TemplateView):
    template_name = 'forecasting/stock_forecast_accuracy_v1.html'


class ForecastInline(InlineFormSetFactory):
    model = Forecast
    form_class = ForecastForm

    # fields = ['product', 'warehouse', 'forecast_date', 'forecasted_quantity']


# class WarehouseInline(InlineFormSetFactory):
#     model = Warehouse
    # fields = ['name', 'email']



class UpdateForcastView(UpdateWithInlinesView):
    model = Version
    # form_class = VersionForm
    inlines = [ForecastInline]
    inlines_names = ['Forecast']

    fields = ['version', 'note', 'forecast_type']
    template_name = 'forecasting/input_interface.html'

    def get_success_url(self):
        # kwargs={'pk': self.object.pk})
        return reverse('forecasting:input_interface_update', args=[self.object.pk])





def simple_upload(request):
    if request.method == 'POST':
        form = VersionForm(request.POST, request.FILES)
        if form.is_valid():
            _file_path_tag = 'file_path'
            # Import data from file
            new_file = request.FILES.get(_file_path_tag, None)


            # Prepare data to process
            model_resource = ForecastResource()
            dataset = Dataset()

            imported_data = dataset.load(
                new_file.read().decode('utf-8'), format='csv')
                
            # Save the form (TODO order is important. 'imported_data' should be defined before saving the form)
            form_obj = form.save()
            # Info message when file is saved
            file_name = str(form.cleaned_data.get(_file_path_tag))
            messages.info(
                request, _('Your file named {} is successfully uploaded'.format(file_name)), extra_tags='safe')

            # Append version column (pk of Version)
            imported_data = imported_data.append_col(
                (form_obj.pk,) * dataset.height, header='version')

            # Test the data import
            result = model_resource.import_data(
                dataset, dry_run=True)  

            if not result.has_errors():
                # Actually import now
                model_resource.import_data(
                    dataset, dry_run=False)  
                messages.success(
                    request, _('Success: Data processed successfully'))

                return redirect(reverse('forecasting:input_interface_update', args=[form_obj.pk]))
            else:
                messages.warning(
                    request, _('Warning: An error has occurred while processing the file'))
                return render(request, 'forecasting/simple_upload.html', {
                    'form': form
                })

    else:
        form = VersionForm()

    return render(request, 'forecasting/simple_upload.html', {
        'form': form
    })


    ################## NEW VERSIONS SPRINT1###########

class VersionList(LoginRequiredMixin, FilterView):
    model = Version
    context_object_name = 'versions'
    filterset_class = VersionFilter
    paginate_by = 12
    template_name = 'forecasting/version_list_old.html'


class FilteredVersionListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Version
    table_class = VersionTable
    filterset_class = VersionFilter
    template_name = "forecasting/version_list.html"
    paginate_by = 20
    order_by = 'created_at'
    # formhelper_class = VersionFilterFormHelper


class VersionDetailView(LoginRequiredMixin, DetailView):
    model = Version

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = 'timezone.now()'
        return context


class VersionUpdateView(LoginRequiredMixin, UpdateView):
    model = Version
    form_class = VersionForm
    # fields = ['description', 'file_path']
    template_name_suffix = '_update'
    # success_url = 

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'forecasting:forecast_list', args=[self.object.pk])


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        version = form.save(commit=False)
        version.created_by = self.request.user
        version.save()

        # Get the uploaded file from the form
        my_file_path = self.request.FILES.get('file_path', None)
        if my_file_path:
            csv_file = my_file_path.read().decode('utf-8')
            # Get version id from the link param
            version_id = self.kwargs['pk']
            # Save csv data in the model
            form.save_csv_data(csv_file, version_id)
            print('Data saved in the model')

            # Success message
            messages.success(
                self.request, _('Success: Data processed successfully'))
        return super().form_valid(form)


class ForecastListByVersionView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Forecast
    table_class = ForecastTable
    filterset_class = ForecastFilter
    form_class = VersionReviewForm

    template_name = "forecasting/forecast_list.html"
    paginate_by = 20
    # order_by = 'created_at'

    # def get(self, request, version):
    #     form = self.form_class()
    #     # form2 = self.form_class2(None)
    #     return render(request, self.template_name, {'review_request_form': form})

    # def post(self, request):
    #     version_id = self.kwargs['version']
    #     if request.method == 'POST' and 'review_request_submit' in request.POST:
    #         form = self.form_class(request.POST)
    #         if form.is_valid:
    #             user = CustomUser.objects.get(pk=request.POST['approved_by'])

    #             # Success message
    #             messages.success(
    #                 request, _('Review request sent to {} ({})').format(user.get_full_name(), user.username))

    #             return redirect(reverse('forecasting:forecast_list', args=[version_id]))

    #         else:
    #             # Error message
    #             messages.warning(
    #                 request, _('Form not valid. Request not sent.'))

    #             return redirect(reverse('forecasting:forecast_list', args=[version_id]))
    #     # elif request.method=='POST' and 'htmlsubmitbutton2' in request.POST:
    #     #         ## do what ever you want to do for second function ####
    #     return render(request, self.template_name, {'review_request_form': form})

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(version=self.kwargs['version_id'])
        # queryset = ForecastFilter(self.request.GET, queryset)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get the form
        context['form'] = ForecastForm()

        # Get params
        category_id = self.request.GET.get('category', None)
        circuit_id = self.request.GET.get('circuit', None)
        version_id = self.kwargs['version_id']

        # Get current version object
        context['version'] = Version.objects.get(pk=version_id)

        
        # Orders chart
        print('category_id {} circuit_id {}'.format(category_id, circuit_id))
        category_id = int(category_id) if category_id else None
        circuit_id = int(circuit_id) if circuit_id else None
        # context['chart_plot'] = chart_plot(category_id, circuit_id, version_id)
        
        context['order_plot'] = order_plot(category_id, circuit_id)
        context['delivery_plot'] = delivery_plot(category_id, circuit_id)
        context['forecast_plot'] = forecast_plot(category_id, circuit_id, version_id)

        # # Create pivot table (my method)
        # df = read_frame(self.get_queryset())
        # pt = pd.pivot_table(df, values='forecasted_quantity', index=['category', 'circuit'],
        #                     columns=['forecast_date'], aggfunc=np.sum)
        # context['pivot_table'] = pt.to_html(
        #     classes="table table-sm table-hover table-responsive-md")


        # Create editable pivot table
        pt_context = get_pivot_data_context(self.request, version_id)
        context.update(pt_context)

        # # Get data from tables
        # deliveries = Delivery.
        # orders = Order.
        last_budget_subquery = Forecast.objects.filter(
            category=OuterRef('category'),
            circuit=OuterRef('circuit'),
            forecast_date=OuterRef('forecast_date'),
            version__version_date__lte=OuterRef('version__version_date'),
            version__is_budget=True,
        ).order_by('-created_at'
        ).values('forecasted_quantity')[:1]
        
        previous_version_subquery = Forecast.objects.filter(
            category=OuterRef('category'),
            circuit=OuterRef('circuit'),
            forecast_date=OuterRef('forecast_date'),
            version__version_date__lte=OuterRef('version__version_date'),
            version__is_budget=False,
        ).order_by('-created_at'
        ).values('forecasted_quantity')[:1]

        pivot_table_qs = Forecast.objects.filter(
            version=version_id
        ).annotate(
            budget=Subquery(last_budget_subquery),
            previous_version=Subquery(previous_version_subquery),
        ).values(
            'id',
            'category',
            'circuit',
            'forecast_date',
            'budget',
            'previous_version',
        )

        print('pivot_table_qs ', pivot_table_qs)

        Order.objects.filter()


        # User objects
        context['supervisor_users'] = CustomUser.objects.filter(groups__name='supervisor')

        return context
    

def order_plot(category_id, circuit_id):
    ''' Get filter params and return a chart ready to use in template '''
    # Get queryset
    orders_qs = Order.objects.get_historical_order(
        category_id=category_id, circuit_id=circuit_id)
    # Convert queryset to dataframe
    orders_df = read_frame(orders_qs)
    orders_df = orders_df.groupby(
        by=['circuit', 'ordered_at'],
        as_index=False
    ).agg({
        'ordered_quantity': 'sum',
    }).reset_index(
        # ).sort_values(
        #     by=['category_circuit'],
        #     ascending=False,
        #     na_position='first',
    )
    orders_pt = pd.pivot_table(orders_df, values='ordered_quantity', index=['ordered_at'],
                               columns=['circuit'], aggfunc=np.sum)
    orders_pt = orders_pt.reset_index()



    # print(orders_pt)
    # print('category_id ', category_id)
    # print('circuit_id ', circuit_id)

    # Prepare figure dict
    orders_pt = orders_pt.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['ordered_at'],
        # y=['ordered_quantity'],
        # categories=['circuit'],
        theme='white',
        title=_('Commandes'),
        xTitle=_('Dates'),
        yTitle=_('Quantité UVC'),
    )
    # Convert figure to Div
    plot_div = py.plot(orders_pt, include_plotlyjs=False,
                    output_type='div', show_link=False)
    # print(orders_df)
    return plot_div

def delivery_plot(category_id, circuit_id):
    ''' Get filter params and return a chart ready to use in template '''
    # Get queryset
    qs = Delivery.objects.get_historical_delivery(
        category_id=category_id, circuit_id=circuit_id)
    # Convert queryset to dataframe
    df = read_frame(qs)
    df = df.groupby(
        by=['circuit', 'delivered_at'],
        as_index=False
    ).agg({
        'delivered_quantity': 'sum',
    }).reset_index(
        # ).sort_values(
        #     by=['category_circuit'],
        #     ascending=False,
        #     na_position='first',
    )
    pt = pd.pivot_table(df, values='delivered_quantity', index=['delivered_at'],
                               columns=['circuit'], aggfunc=np.sum)
    pt = pt.reset_index()

    # Prepare figure dict
    pt = pt.iplot(
        asFigure=True,
        kind='bar',
        barmode='stack',
        x=['delivered_at'],
        # y=['delivered_quantity'],
        # categories=['circuit'],
        theme='white',
        title=_('Livraisons'),
        xTitle=_('Dates'),
        yTitle=_('Quantité UVC'),
    )
    # Convert figure to Div
    plot_div = py.plot(pt, include_plotlyjs=False,
                       output_type='div', show_link=False)
    # print(df)
    return plot_div

def forecast_plot(category_id, circuit_id, version_id):
    ''' Get filter params and return a chart ready to use in template '''
    # Get queryset
    qs = Forecast.objects.get_historical_forecast(
        category_id=category_id, circuit_id=circuit_id, version_id=version_id)
    # Convert queryset to dataframe
    df = read_frame(qs)
    df = df.groupby(
        by=['version__reference', 'forecast_date'],
        as_index=False
    ).agg({
        'forecasted_quantity': 'sum',
    }).reset_index(
        # ).sort_values(
        #     by=['category_circuit'],
        #     ascending=False,
        #     na_position='first',
    )
    pt = pd.pivot_table(df, values='forecasted_quantity', index=['forecast_date'],
                               columns=['version__reference'], aggfunc=np.sum)
    pt = pt.reset_index()

    # Prepare figure dict
    pt = pt.iplot(
        asFigure=True,
        kind='bar',
        # barmode='stack',
        x=['forecast_date'],
        # y=['forecasted_quantity'],
        # categories=['version__reference'],
        theme='white',
        title=_('Previsions'),
        xTitle=_('Dates'),
        yTitle=_('Quantité UVC'),
    )
    # Convert figure to Div
    plot_div = py.plot(pt, include_plotlyjs=False,
                       output_type='div', show_link=False)
    # print(df)
    return plot_div

##############################""
# Forecast pivot table 
def get_pivot_data_context(request, version_id):
    _rows_per_page = 20
    filter = ForecastFilter(request.GET, queryset=Forecast.objects.filter(version_id=version_id).values('forecast_date').annotate(Count('forecast_date')).order_by('forecast_date').all())
    forecast_dates = filter.qs

    paginator = Paginator(ForecastFilter(request.GET, Forecast.objects.filter(version_id=version_id).values(
        'category', 'category__reference', 'circuit', 'circuit__reference').annotate(Count('category'), Count('circuit')).all()).qs, _rows_per_page)
    page = int(request.GET.get('page', '1'))
    try:
        page_obj = paginator.page(page)
    except Paginator:
        page_obj = paginator.page(1)

    # print(page_obj)
    header_data = ['forecast_date']

    for date in forecast_dates:
        header_data.append(date['forecast_date'])

    body_data = []

    for value_obj in page_obj:
        row = []
        # print(value_obj)
        row.append(str(value_obj['category__reference']) +
                   '_'+str(value_obj['circuit__reference']))
        for date in forecast_dates:
            # FIXME optimize the query! select_related or one time query call might help
            forecasts = Forecast.objects.filter(category=value_obj['category']).filter(
                circuit=value_obj['circuit']).filter(forecast_date=date['forecast_date']).values()
            if len(forecasts):
                row.append(
                    {'quantity': forecasts[0]['forecasted_quantity'], 'id': forecasts[0]['id']})
            else:
                row.append({'none': None, 'forecast_date': date['forecast_date'].strftime('%Y-%m-%d'),
                            'categoryId': value_obj['category'], 'circuitId': value_obj['circuit']})
        body_data.append(row)
        # for forecast in forcasts:
    # print("+++++=")
    # print(body_data)
    # TODO Find a way to get data from a form 
    # REF https://docs.djangoproject.com/en/3.0/topics/class-based-views/mixins/#using-formmixin-with-detailview
    customers = Customer.objects.values()
    categories = ProductCategory.objects.values()
    circuits = Circuit.objects.values()
    versions = Version.objects.values()

    context = {
        'header_data': header_data,
        'body_data': body_data,
        'cutomers': customers,
        'categories': categories,
        'circuits': circuits,
        'versions': versions,
        'page_obj': page_obj,
        'version_id': version_id,
        'filter': filter
    }
    return context


def updateQuantity(request, version_id):
    try:
        id = request.GET.get('id')
        quantity = request.GET.get('quantity')
        print(request)
        Forecast.objects.filter(id=id).update(forecasted_quantity=quantity)

        return JsonResponse({"success": True})
    except Exception:
        print(Exception)
        return JsonResponse({"success": False})


def addQuantity(request, version_id):
    # try:
    forecasted_quantity = request.GET.get('forecasted_quantity', None)
    forecast_date = request.GET.get('forecast_date', None)
    category_id = request.GET.get('category_id', None)
    circuit_id = request.GET.get('circuit_id', None)


    forecast_date = datetime.strptime(forecast_date,  "%Y-%m-%d")
    forecast = Forecast(forecasted_quantity=forecasted_quantity, forecast_date=forecast_date,
                        category_id=category_id, circuit_id=circuit_id, version_id=version_id)
    forecast.save()
    return JsonResponse({'success': True})
    # except Exception:
    #     print(Exception)
    #     return JsonResponse({'success':False})


def addForecast(request, version_id):

    forecasted_quantity = request.GET.get('forecasted_quantity', None)
    forecast_date = request.GET.get('forecast_date', None)
    category_id = request.GET.get('category_id', None)
    circuit_id = request.GET.get('circuit_id', None)
    version_id = request.GET.get('version_id', None)
    customer_id = request.GET.get('customer_id', None)
    
    forecast = Forecast(version_id=version_id, customer_id=customer_id, forecasted_quantity=forecasted_quantity,
                        forecast_date=forecast_date, category_id=category_id, circuit_id=circuit_id)
    forecast.save()
    
    return redirect(reverse('forecasting:forecast_list', args=[version_id]))


    # uploaded_file_url = ''
    # if request.method == 'POST' and request.FILES:
    #     # Get the file
    #     new_file = request.FILES['myfile']

    #     # Save the file
    #     # fs = FileSystemStorage()
    #     filename = fs.save(new_file.name, new_file)
    #     uploaded_file_url = fs.url(filename)

    #     # Info message when file is saved
    #     messages.info(
    #         request, _('Your file is uploaded at:') + '<a href="' + uploaded_file_url + '">' + uploaded_file_url + '</a>', extra_tags='safe')

    #     # Import data from file
    #     model_resource = ForecastResource()
    #     dataset = Dataset()
    #     imported_data = dataset.load(
    #         new_file.read().decode('utf-8'), format='csv')

    #     # Test the data import
    #     result = model_resource.import_data(
    #         dataset, dry_run=True)  

    #     if not result.has_errors():
    #         # Actually import now
    #         model_resource.import_data(
    #             dataset, dry_run=False)  
    #         messages.success(
    #             request, _('Your file was imported successfully'))

    #     else:
    #         messages.warning(
    #             request, _('Task cancelled: An error has occurred while processing the file'))

    # return render(request, 'forecasting/simple_upload.html')

def sendReviewRequest(request, version_id):
    if request.method == 'GET':

        user_id = request.GET.get('user_id', None)
        # version = request.GET.get('version', None)

        # try:
        # Get user object
        user = CustomUser.objects.get(pk=user_id)
        
        # Get version object and update data
        version = Version.objects.get(pk=version_id)
        version.approved_by = user
        version.status = Version.PENDING
        version.save()
        # Success message
        messages.success(
            request, _('Review request sent to {} ({})').format(user.get_full_name(), user.username))

        return redirect(reverse('forecasting:forecast_list', args=[version_id]))

    # except ObjectDoesNotExist:
    #     print("Either the user or version doesn't exist.")

    # Error message
    messages.warning(
        request, _('Warning: An error has occurred. Request not sent.'))

    return redirect(reverse('forecasting:forecast_list', args=[version_id]))


def approveReviewRequest(request, version_id):
    # Get version object and update data
    version = Version.objects.get(pk=version_id)
    version.status = Version.APPROVED
    version.save()
    # Success message
    messages.success(
        request, _('Request approved.'))
    logger.info('Request for version {} is approved'.format(version))
    

    return redirect(reverse('forecasting:forecast_list', args=[version_id]))
