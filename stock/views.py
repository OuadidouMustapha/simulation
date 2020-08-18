from django.shortcuts import render
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


from .models import (ProductCategory, Product, Supplier, Customer, Supply, SupplyDetail,
                     Order, OrderDetail, Sale, SaleDetail, Warehouse, StockControl)


class ProductIndexView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "stock/product_index.html"
    context_object_name = 'product_list'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        # NOTE : You can use super(ProductDescriptionView, self) to inherate from other classes
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        context['page_title'] = 'Product Dashboard'
        context['table_title'] = 'Product List'
        context['dash_title'] = 'Product Description'
        context['total_products'] = Product.get_total_products()
        context['total_categories'] = ProductCategory.get_total_categories()
        return context


class StockIndexView(LoginRequiredMixin, ListView):
    # permission_required = 'polls.add_choice'

    model = StockControl
    product_category_model = ProductCategory
    template_name = "stock/stock_index.html"
    context_object_name = 'stock_list'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        context['product_category_model'] = self.product_category_model
        context['product_category_list'] = ProductCategory.tree.all()
        context['page_elements'] = {}
        context['page_elements']['page_title'] = 'Stock Overview'
        context['page_elements']['table_title'] = 'Stock List'
        # context['page_elements']['dash_stock_value_title'] = 'Stock Value'
        # context['page_elements']['dash_stock_coverage_title'] = 'Stock DIO'
        return context


class StockValueView(LoginRequiredMixin, TemplateView):
    template_name = "stock/stock_value.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_elements'] = {}
        context['page_elements']['page_title'] = 'Stock Value'
        context['page_elements']['dash_title'] = 'Stock Value'
        return context

class StockDioView(LoginRequiredMixin, TemplateView):
    template_name = "stock/stock_dio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_elements'] = {}
        context['page_elements']['page_title'] = 'Stock DIO'
        context['page_elements']['dash_title'] = 'Stock DIO'
        return context


class StockParetoView(LoginRequiredMixin, TemplateView):
    template_name = "stock/stock_pareto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_elements'] = {}
        context['page_elements']['page_title'] = 'Pareto Distribution'
        context['page_elements']['dash_title'] = 'Pareto Distribution'
        return context



class SaleIndexView(LoginRequiredMixin, TemplateView):
    template_name = "stock/sale_index.html"


class PurchaseIndexView(LoginRequiredMixin, TemplateView):
    template_name = "stock/purchase_index.html"


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = "stock/index.html"



# def get_product_category_tree(request):
#     return render(request, "stock/product_category_tree.html", {'product_category': ProductCategory.objects.all()})
