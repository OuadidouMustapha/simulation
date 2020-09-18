from django.urls import path
from . import views
from deployment.dashboards import deployment_dashboard

app_name = 'deployment'
urlpatterns = [
    path('index', views.IndexView.as_view(),
         name='deployment_index'),
    path('dashboard', views.DashboardView.as_view(),
         name='deployment_dashboard'),
    path('form_test', views.form_handler,
         name='form_test'),
]