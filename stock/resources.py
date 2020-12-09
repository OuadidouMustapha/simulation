from .models import Product, Warehouse, Customer, Circuit, Order, ProductCategory, Delivery

from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, IntegerWidget, DateWidget, DecimalWidget
import datetime


class WarehouseResource(resources.ModelResource):
    class Meta:
        model = Warehouse
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('reference',)
        exclude = ('id',)

class CircuitResource(resources.ModelResource):
    class Meta:
        model = Circuit
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('reference',)
        exclude = ('id',)

class ProductCategoryResource(resources.ModelResource):
    class Meta:
        model = ProductCategory
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('reference',)
        exclude = ('id',)

class ProductResource(resources.ModelResource):
    category = Field(
        attribute='category',
        column_name='category',
        widget=ForeignKeyWidget(ProductCategory, 'pk')
    )
    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('reference',)
        exclude = ('id',)
    
    def before_import_row(self, row, **kwargs):
        # Get or create nested models
        category_model, _created = ProductCategory.objects.get_or_create(
            reference=row.get('category'),
        )
        row['category'] = category_model.id

    # TODO I'm here!!! try this method (optimizing?)
    # def init_instance(self, row, *args, **kwargs):
    #     instance = super().init_instance(*args, **kwargs)
    #     reference = row.get("reference")
    #     description = row.get("description")
    #     category, created = Category.objects.get_or_create(
    #         reference=reference,
    #     )
    #     user.role = user.EMPLOYEE
    #     user.save()
    #     instance.user = user
    #     return instance


class OrderResource(resources.ModelResource):
    # product = Field(
    #     attribute='product',
    #     column_name='product',
    #     widget=ForeignKeyWidget(Product, 'pk')
    # )
    # warehouse = Field(
    #     attribute='warehouse',
    #     column_name='warehouse',
    #     widget=ForeignKeyWidget(Warehouse, 'pk')
    # )
    # customer = Field(
    #     attribute='customer',
    #     column_name='customer',
    #     widget=ForeignKeyWidget(Customer, 'pk')
    # )
    # circuit = Field(
    #     attribute='circuit',
    #     column_name='circuit',
    #     widget=ForeignKeyWidget(Circuit, 'pk')
    # )
    ordered_at = Field(
        attribute='ordered_at',
        column_name='ordered_at',
        widget=DateWidget(),
    )
    ordered_quantity = Field(
        attribute='ordered_quantity',
        column_name='ordered_quantity',
        widget=IntegerWidget(),
    )
    # reference = Field(
    #     attribute='reference',
    #     column_name='order_reference',
    #     widget=DateWidget(),
    # )
    class Meta:
        model = Order
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('circuit', 'warehouse', 'product', 'category', 'ordered_quantity', 'ordered_at',) 
        exclude = ('id',)


        # use_transactions = True
        # use_bulk = True
        # skip_diff = True
        # chunk_size = 200

    # def get_queryset(self):
    #     ''' Select related object data with the query '''
    #     return super().get_queryset().select_related('circuit', 'warehouse', 'product', 'customer')  # .all()


    # def before_import_row(self, row, **kwargs):
    #     # Clean numeric fields
    #     if not str(row.get('ordered_quantity')).isnumeric():
    #         row['ordered_quantity'] = None
        
    #     # # Get or create nested models
    #     # (product_model, _created) = Product.objects.get_or_create(
    #     #     reference=row.get('product'),
    #     #     # name=row.get('product'),
    #     # )
    #     # row['product'] = product_model.id

    #     # (warehouse_model, _created) = Warehouse.objects.get_or_create(
    #     #     reference=row.get('warehouse')
    #     # )
    #     # row['warehouse'] = warehouse_model.id

    #     # (circuit_model, _created) = Circuit.objects.get_or_create(
    #     #     reference=row.get('circuit'),
    #     # )
    #     # row['circuit'] = circuit_model.id
    #     row['ordered_at'] = datetime.datetime.strptime(
    #         row['ordered_at'], "%m/%d/%Y").date()

class DeliveryResource(resources.ModelResource):
    # product = Field(
    #     attribute='product',
    #     column_name='product',
    #     widget=ForeignKeyWidget(Product, 'pk')
    # )
    # warehouse = Field(
    #     attribute='warehouse',
    #     column_name='warehouse',
    #     widget=ForeignKeyWidget(Warehouse, 'pk')
    # )
    # customer = Field(
    #     attribute='customer',
    #     column_name='customer',
    #     widget=ForeignKeyWidget(Customer, 'pk')
    # )
    # circuit = Field(
    #     attribute='circuit',
    #     column_name='circuit',
    #     widget=ForeignKeyWidget(Circuit, 'pk')
    # )
    delivered_at = Field(
        attribute='delivered_at',
        column_name='delivered_at',
        widget=DateWidget(),
    )
    delivered_quantity = Field(
        attribute='delivered_quantity',
        column_name='delivered_quantity',
        widget=IntegerWidget(),
    )
    # reference = Field(
    #     attribute='reference',
    #     column_name='order_reference',
    #     widget=DateWidget(),
    # )
    class Meta:
        model = Delivery
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('circuit', 'warehouse', 'product',
                            'category', 'delivered_quantity', 'delivered_at',)
        exclude = ('id',)


        # use_transactions = True
        # use_bulk = True
        # skip_diff = True
        # chunk_size = 20

    # def get_queryset(self):
    #     ''' Select related object data with the query '''
    #     return super().get_queryset().select_related('circuit', 'warehouse', 'product', 'customer')  # .all()


    def before_import_row(self, row, **kwargs):
        # Clean numeric fields
        if not str(row.get('delivered_quantity')).isnumeric():
            row['delivered_quantity'] = None
        
        # # Get or create nested models
        # (product_model, _created) = Product.objects.get_or_create(
        #     reference=row.get('product'),
        #     # name=row.get('product'),
        # )
        # row['product'] = product_model.id

        # (warehouse_model, _created) = Warehouse.objects.get_or_create(
        #     reference=row.get('warehouse')
        # )
        # row['warehouse'] = warehouse_model.id

        # (circuit_model, _created) = Circuit.objects.get_or_create(
        #     reference=row.get('circuit'),
        # )
        # row['circuit'] = circuit_model.id
        row['delivered_at'] = datetime.datetime.strptime(
            row['delivered_at'], "%m/%d/%Y").date()
