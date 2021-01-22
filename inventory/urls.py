from django.urls import path
from inventory.dashs import stock_image
from inventory.dashs import dash_order
from inventory.dashs import dash_delivery_vs_customer
from inventory.dashs import otif
from inventory.dashs import dash_otif_vs_sp
from inventory.dashs import dash_order_vs_supplier
from inventory.dashs import dash_delivery_vs_supplier
from . import views

app_name = 'inventory'
urlpatterns = [

    path('', views.DashboardIndexView.as_view(),
         name='index'),
    path('order_customer', views.OrderCustomerIndexView.as_view(),
        name='index'),
    path('order_supplier', views.OrderSupplierIndexView.as_view(),
         name='index'),
    path('delivery_customer', views.DeliveryCustomerIndexView.as_view(),
        name='index'),
    path('delivery_supplier', views.DeliverySupplierIndexView.as_view(),
         name='index'),
    path('otif', views. OtifIndexView.as_view(),
         name='index'),
    path('otif_supplier', views.OtifSupplierIndexView.as_view(),
         name='index'),
]

