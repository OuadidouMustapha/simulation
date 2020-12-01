from django.urls import path
from stock.dashboards import stock_value
from stock.dashboards import stock_dio
from stock.dashboards import stock_pareto
from stock.dashboards import warehouse_location
from . import views

app_name = 'stock'
urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:category_id>/refill/', views.refill, name='refill'),

    # # URL used in view.backup200227
    # path('product/', views.ProductListView.as_view(), name='product_list'),
    # path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    # path('product/new/', views.ProductCreate.as_view(), name='product_create'),
    # path('product/<int:pk>/edit/', views.ProductUpdate.as_view(), name='product_update'),
    # path('product/<int:pk>/delete/', views.ProductDelete.as_view(), name='product_delete'),
    # path('upload-csv/', views.CsvDataUpload, name="csv_data_upload"),
    # path('product/chart/', views.chart, name='product_chart'),

    path('product_index/', views.ProductIndexView.as_view(),
         name='product_index'),
    path('index/', views.StockIndexView.as_view(),
         name='stock_index'),
    path('stock/value/', views.StockValueView.as_view(),
         name='stock_value'),
    path('dio/', views.StockDioView.as_view(),
         name='stock_dio'),
    path('pareto/', views.StockParetoView.as_view(),
         name='stock_pareto'),
    path('sale/index/', views.DeliveryIndexView.as_view(),
         name='sale_index'),
    path('purchase/index/', views.PurchaseIndexView.as_view(),
         name='purchase_index'),
    path('', views.DashboardIndexView.as_view(),
         name='index'),

]

