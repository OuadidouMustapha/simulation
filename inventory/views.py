from django.shortcuts import render

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class DashboardIndexView(TemplateView):
    template_name = "inventory/index.html"

class OrderCustomerIndexView(LoginRequiredMixin,TemplateView):
    template_name = "order/customer.html"

class OrderSupplierIndexView(LoginRequiredMixin, TemplateView):
    template_name = "order/supplier.html"

class DeliveryCustomerIndexView(TemplateView):
    template_name = "delivery/customer.html"

class DeliverySupplierIndexView(TemplateView):
    template_name = "delivery/supplier.html"

class OtifIndexView(TemplateView):
    template_name = "otif/customer.html"

class OtifSupplierIndexView(TemplateView):
    template_name = "otif/supplier.html"
    
class ProfilIndexView(TemplateView):
    template_name = "profil/index.html"
