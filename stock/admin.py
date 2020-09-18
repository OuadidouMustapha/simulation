from django.contrib import admin

from .models import ProductCategory, Product, Order
from import_export.admin import ImportExportModelAdmin
from .resources import OrderResource

admin.site.site_header = 'Orchest Administration'
admin.site.site_title = 'Orchest Admin'

# Override CategoryAdmin class to define dates as readonly fields 
class ProductCategoryAdmin(admin.ModelAdmin):
    readonly_fields= ['created_at', 'updated_at',]


# Add models to admin interface
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource