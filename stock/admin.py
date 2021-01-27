from django.contrib import admin

from .models import ProductCategory, Product, Warehouse, Circuit, Customer, Order, Delivery
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from .resources import OrderResource, DeliveryResource, WarehouseResource, CircuitResource, ProductResource, ProductCategoryResource


admin.site.site_header = 'Orchest Administration'
admin.site.site_title = 'Orchest Admin'

# Override CategoryAdmin class to define dates as readonly fields 
# class ProductCategoryAdmin(admin.ModelAdmin):
#     readonly_fields= ['created_at', 'updated_at',]


# # Add models to admin interface
# admin.site.register(ProductCategory, ProductCategoryAdmin)
# admin.site.register(Product)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource

@admin.register(Delivery)
class DeliveryAdmin(ImportExportModelAdmin):
    resource_class = DeliveryResource

# @admin.register(Product)
# class ProductAdmin(ImportExportModelAdmin):
#     resource_class = ProductResource

@admin.register(ProductCategory)
class ProductCategoryAdmin(ImportExportModelAdmin):
    resource_class = ProductCategoryResource

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource


@admin.register(Warehouse)
class WarehouseAdmin(ImportExportModelAdmin):
    resource_class = WarehouseResource

@admin.register(Circuit)
class CircuitAdmin(ImportExportModelAdmin):
    resource_class = CircuitResource

