from django.urls import path
from . import views

app_name = 'deployment'
urlpatterns = [
    path('index', views.IndexView.as_view(),
         name='deployment_index'),
]
