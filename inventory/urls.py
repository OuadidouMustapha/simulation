from django.urls import path
from inventory.dashs import stock_image
from inventory.dashs import dash_order
from inventory.dashs import dash_delivery
from inventory.dashs import dash_otif
from . import views

app_name = 'inventory'
urlpatterns = [

    path('', views.DashboardIndexView.as_view(),
         name='index'),
    path('/order', views.OrderIndexView.as_view(),
        name='index'),
    path('/delivery', views.DeliveryIndexView.as_view(),
        name='index'),
    path('/otif', views. OtifIndexView.as_view(),
         name='index'),
]

