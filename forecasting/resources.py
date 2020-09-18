from .models import StockForecast
from stock.models import Product, Warehouse, Customer, Circuit

from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, IntegerWidget, DateWidget, DecimalWidget


# class IntegerCleanWidget(IntegerWidget):
#     def clean(self, value, row=None, *args, **kwargs):
#         val = super().clean(value)
#         print(val)
#         if not str(val).isnumeric():
#             print('not')
#             return None


class StockForecastResource(resources.ModelResource):
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
    forecast_date = Field(
        attribute='forecast_date',
        column_name='forecast_date',
        widget=DateWidget(),
    )
    forecast_version = Field(
        attribute='forecast_version',
        column_name='forecast_version',
        widget=DateWidget(),
    )
    forecasted_quantity = Field(
        attribute='forecasted_quantity',
        column_name='forecasted_quantity',
        # widget=IntegerCleanWidget(),
        widget=IntegerWidget(),
    )
    product_cost = Field(
        column_name='product_cost',
        widget=DecimalWidget(),
    )
    product_type = Field(
        column_name='product_type',
    )
    product_name = Field(
        column_name='product_name',
    )
    
    class Meta:
        model = StockForecast
        # fields = ('id', 'product', 'forecast_date', 'forecasted_quantity',)
        exclude = ('status', 'created_at', 'updated_at', )
        use_transactions = False
        use_bulk = True
        skip_diff = True
        chunk_size = 20






    def before_import_row(self, row, **kwargs):
        # Clean numeric fields
        if not str(row.get('forecasted_quantity')).isnumeric():
            row['forecasted_quantity'] = None
        
        # Get or create nested models
        (product_model, _created) = Product.objects.get_or_create(
            reference=row.get('product'),
            defaults={
                'cost': row.get('product_cost'),
                'product_type': row.get('product_type'),
                'name': row.get('product_name'),
            },
        )
        row['product'] = product_model.id

        (warehouse_model, _created) = Warehouse.objects.get_or_create(
            name=row.get('warehouse'))
        row['warehouse'] = warehouse_model.id

        (circuit_model, _created) = Circuit.objects.get_or_create(
            reference=row.get('circuit'),
        )
        row['circuit'] = circuit_model.id

        # (customer_model, _created) = Customer.objects.get_or_create(
        #     reference=row.get('customer'),
        #     circuit=circuit_model
        # )
        # row['customer'] = customer_model.id




    # def before_import_row(self, row, **kwargs):
    #     if int(row[4]) < int(row[5]):
    #         raise ValidationError('Product offer price cannot be greater than Product MRP. '
    #                               'Error in row with id = %s' % row[0])

