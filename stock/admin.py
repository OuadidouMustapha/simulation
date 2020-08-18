from django.contrib import admin

from .models import ProductCategory, Product

admin.site.site_header = 'Project Administration'
admin.site.site_title = 'Site Admin'

# Override CategoryAdmin class to define dates as readonly fields 
class ProductCategoryAdmin(admin.ModelAdmin):
    readonly_fields= ['created_at', 'updated_at',]


# Add models to admin interface
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product)
