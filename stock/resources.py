from .models import Product, Warehouse, Customer, Circuit, Order

from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, IntegerWidget, DateWidget, DecimalWidget


class OrderResource(resources.ModelResource):
    product = Field(
        attribute='product',
        column_name='product',
        widget=ForeignKeyWidget(Product, 'pk')
    )
    warehouse = Field(
        attribute='warehouse',
        column_name='warehouse',
        widget=ForeignKeyWidget(Warehouse, 'pk')
    )
    # customer = Field(
    #     attribute='customer',
    #     column_name='customer',
    #     widget=ForeignKeyWidget(Customer, 'pk')
    # )
    circuit = Field(
        attribute='circuit',
        column_name='circuit',
        widget=ForeignKeyWidget(Circuit, 'pk')
    )
    ordered_at = Field(
        attribute='ordered_at',
        column_name='ordered_at',
        widget=DateWidget(),
    )
    reference = Field(
        attribute='reference',
        column_name='order_reference',
        widget=DateWidget(),
    )
    ordered_quantity = Field(
        attribute='ordered_quantity',
        column_name='ordered_quantity',
        widget=IntegerWidget(),
    )
    class Meta:
        model = Order
        # fields = ('id', 'product', 'forecast_date', 'forecasted_quantity',)
        exclude = ('status', 'created_at', 'updated_at', )
        use_transactions = True
        use_bulk = True
        skip_diff = True
        chunk_size = 20






    def before_import_row(self, row, **kwargs):
        # Clean numeric fields
        if not str(row.get('ordered_quantity')).isnumeric():
            row['ordered_quantity'] = None
        
        # Get or create nested models
        (product_model, _created) = Product.objects.get_or_create(
            reference=row.get('product'),
        )
        row['product'] = product_model.id

        (warehouse_model, _created) = Warehouse.objects.get_or_create(
            name=row.get('warehouse'))
        row['warehouse'] = warehouse_model.id

        (circuit_model, _created) = Circuit.objects.get_or_create(
            reference=row.get('circuit'),
        )
        row['circuit'] = circuit_model.id
