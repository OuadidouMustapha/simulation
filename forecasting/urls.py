from django.urls import path
from forecasting.dashboards import stock_forecast_accuracy
from forecasting.dashboards import stock_forecast_accuracy_madec
from forecasting.dashboards import stock_forecast_accuracy_test
from . import views

app_name = 'forecasting'
urlpatterns = [
    path('stock/forecast/accuracy', views.StockForecastAccuracyView.as_view(),
         name='stock_forecast_accuracy'),
    path('stock/forecast/accuracy_madec', views.StockForecastAccuracyMadecView.as_view(),
         name='stock_forecast_accuracy_madec'),
    path('stock/forecast/accuracy_test', views.StockForecastAccuracyTestView.as_view(),
         name='stock_forecast_accuracy_test'),
]
