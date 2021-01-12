from django.shortcuts import render

from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class DashboardIndexView(TemplateView):
    template_name = "inventory/index.html"

class OrderIndexView(TemplateView):
    template_name = "order/index.html"

class DeliveryIndexView(TemplateView):
    template_name = "delivery/index.html"

class OtifIndexView(TemplateView):
    template_name = "otif/index.html"
