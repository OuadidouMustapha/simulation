from django.urls import path
from forecasting.dashboards import forecast_accuracy
from forecasting.dashboards import forecast_accuracy_madec
from forecasting.dashboards import forecast_accuracy_v1
from . import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'forecasting'
urlpatterns = [
    path('index', views.IndexView.as_view(),
         name='index'),
#     path('input_interface', views.InputInterfaceView.as_view(),
#          name='input_interface'),
    path('accuracy', views.ForecastAccuracyView.as_view(),
         name='forecast_accuracy'),
    path('accuracy_madec', views.ForecastAccuracyMadecView.as_view(),
         name='forecast_accuracy_madec'),
    path('accuracy_test', views.ForecastAccuracyV1View.as_view(),
         name='forecast_accuracy_v1'),
#     url(r'^input_interface/new/$', views.CreateProductView.as_view(), name='input_interface_new'),
    path('input_interface/<int:pk>', views.UpdateForcastView.as_view(),
         name='input_interface_update'),
    path('version/listold', views.VersionList.as_view(),
         name='version_list_old'),
    path('version/', views.FilteredVersionListView.as_view(),
         name='version_list'),
    path('version/<int:pk>', views.VersionDetailView.as_view(),
         name='version_detail'),
    path('version/update/<int:pk>', views.VersionUpdateView.as_view(),
         name='version_update'),
    path('forecast/v<int:version>', views.ForecastListByVersiomView.as_view(),
         name='forecast_list'),
#     path('forecast/v<int:version>/getpivottable', views.getPivotData),
    path('forecast/v<int:version>/updatequantity', views.updateQuantity, name = 'ajax_update_forecast_qty'),
    path('forecast/v<int:version>/addquantity', views.addQuantity, name = 'ajax_add_forecast_qty'),
    path('forecast/v<int:version>/addforecast', views.addForecast, name = 'ajax_add_forecast'),


#     url(r'^input_interface/(?P<pk>\d+)/$',
#         views.UpdateProductView.as_view(), name='input_interface_update'),


#     #export
#     url(r'export/$', login_required(views.ForecastExport.as_view()), name='forecast_export'),

#     #import
#     url(r'import/$', login_required(views.ForecastImport.as_view()), name='forecast_import'),

#     url(r'process_import/$',
#         login_required(views.ForecastProcessImport.as_view()), name='process_import'),
    path('simple_upload', views.simple_upload,
         name='simple_upload'),


]
