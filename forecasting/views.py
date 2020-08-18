# from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import StockForecast

class StockForecastAccuracyView(LoginRequiredMixin, TemplateView):
    # model = StockForecast
    # queryset = StockForecast.objects.get_forecast_accuracy(OrderDetail)
    template_name = "forecasting/stock_forecast_accuracy.html"
    # context_object_name = 'stock_forecast_accuracy_list'
    # paginate_by = 20

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['stock_forecast_order'] = StockForecast.objects.get_forecast_accuracy(
    #     #     OrderDetail)
    #     context['page_elements'] = {}
    #     context['page_elements']['page_title'] = 'Forecast Accuracy'
    #     context['page_elements']['table_title'] = 'Forecast Accuracy Table'

    #     return context


class StockForecastAccuracyMadecView(LoginRequiredMixin, TemplateView):
    template_name = "forecasting/stock_forecast_accuracy_madec.html"
