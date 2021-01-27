import factory
from faker import Faker

from .models import (ProductCategory, Product, Warehouse, Stock, StockPolicy, StockControl,
                     Customer, Order, OrderDetail, Delivery, DeliveryDetail, Circuit)
from forecasting.factories import ForecastFactory
import random
import pytz

class ProductCategoryFactory(factory.django.DjangoModelFactory):
    reference = factory.Sequence(lambda n: 'cat00%d' % n) # factory.Iterator(["cat001", "cat002", "cat003"])
    name = factory.Sequence(lambda n: 'Category %d' % n) # factory.Iterator(["Category 1", "Category 2", "Category 3"])
    parent = factory.SelfAttribute('id')
    # reference = factory.Sequence(lambda n: 'cat %d' % n)
    # name = factory.Faker('company')

    class Meta:
        model = ProductCategory

    @factory.post_generation
    def create_products(self, create, how_many, **kwargs):
        # this method will be called twice, first time how_many will take the value passed
        # in factory call (e.g., create_products=3), second time it will be None
        # (see factory.declarations.PostGeneration#call to understand how how_many is populated)
        # ProductCategoryFactory is therefore called +1 times but somehow we get right amount of objs
        at_least = 1
        if not create:
            return
        for n in range(how_many or at_least):
            # child_lev_1 = ProductCategoryFactory(
            #     reference=factory.LazyFunction(lambda:'%d-lev-1-%d' % (self.id, random.randint(0, 1000))),
            #     parent=self
            # )
            # child_lev_2 = ProductCategoryFactory(
            #     reference=factory.LazyFunction(lambda:'%d-lev-2-%d' % (self.id, random.randint(0, 1000))),
            #     parent=child_lev_1
            # )
            # child_lev_3 = ProductCategoryFactory(
            #     reference=factory.LazyFunction(lambda:'%d-lev-3-%d' % (self.id, random.randint(0, 1000))),
            #     parent=child_lev_2
            # )

            ProductFactory(category=self)


class ProductFactory(factory.django.DjangoModelFactory):

    category = factory.SubFactory(ProductCategoryFactory)
    reference = factory.Sequence(lambda n: 'sku %d' % n)
    cost = factory.Faker(
        'pydecimal',
        left_digits=None,
        right_digits=None,
        positive=True,
        min_value=10,
        max_value=500
    )
    weight = factory.Faker(
        'pydecimal',
        left_digits=None,
        right_digits=None,
        positive=True,
        min_value=1,
        max_value=50
    )
    weight_unit = factory.LazyFunction(lambda: random.choice(['kg']))
    volume = factory.Faker(
        'pydecimal',
        left_digits=None,
        right_digits=None,
        positive=True,
        min_value=1,
        max_value=100
    )
    volume_unit = factory.LazyFunction(lambda: random.choice(['cm3']))
    package = factory.Faker('random_number', digits=2, fix_len=False)
    pallet = factory.LazyAttribute(lambda o: int(o.package * random.randint(1,10)))

    product_type = factory.Iterator(['PV', 'AP', 'CS'])
    product_ray = factory.Iterator(['Food', 'Non Food'])
    product_universe = factory.Iterator(['Groupe', 'Non Groupe'])

    class Meta:
        model = Product

    @factory.post_generation
    def create_stock_and_saledetail(self, create, how_many, **kwargs):
        at_least = 100 # TODO : use a global constant or console parameter
        if not create:
            return
        for n in range(how_many or at_least):
            # Generate random date
            fake = Faker()
            random_date_this_year = fake.date_this_year()

            # Generate warehouses
            warehouse_1 = WarehouseFactory.create(name='warehouse_1')
            warehouse_2 = WarehouseFactory.create(name='warehouse_2')
            warehouse_3 = WarehouseFactory.create(name='warehouse_3')
            # Generate circuits
            circuit_1 = CircuitFactory.create(reference='circuit_1')
            circuit_2 = CircuitFactory.create(reference='circuit_2')
            circuit_3 = CircuitFactory.create(reference='circuit_3')
            circuits = [circuit_1, circuit_2, circuit_3]
            # Generate customers
            customer_1 = CustomerFactory.create(
                reference='customer_1', circuit=circuits[0])
            customer_2 = CustomerFactory.create(
                reference='customer_2', circuit=circuits[1])
            customer_3 = CustomerFactory.create(
                reference='customer_3', circuit=circuits[2])
            customers = [customer_1, customer_2, customer_3]


            # Create Stocks
            # fake_stock_1 = StockFactory(
            #     product=self,
            #     warehouse__name='Warehouse_{}'.format(n)
            #     # warehouse__name=factory.Iterator(
            #     #     ["Warehouse 1", "Warehouse 2", "Warehouse 3"])
            # )
            fake_stock_1 = StockFactory(
                product=self,
                warehouse=warehouse_1,
            )
            fake_stock_2 = StockFactory(
                product=self,
                warehouse=warehouse_2,
            )
            fake_stock_3 = StockFactory(
                product=self,
                warehouse=warehouse_3,
            )
            fake_stock_list = [fake_stock_1, fake_stock_2, fake_stock_3]
            
            # 
            StockControlFactory(
                stock=fake_stock_1,
            )
            
            # Generate forecasting 
            for fake_stock in fake_stock_list:
                ForecastFactory(
                    stock=fake_stock,
                    customer=random.choice(customers),
                    circuit=random.choice(circuits),
                    forecast_date=random_date_this_year,
                    forecasted_quantity=1000,
                )

            DeliveryDetailFactory(
                stock=fake_stock_1,
                sale__customer=random.choice(customers),
            )
            
            # Generate Orders
            for fake_stock in fake_stock_list:
                OrderDetailFactory(
                    stock=fake_stock,
                    order__customer=random.choice(customers),
                    order__reference='order_1_{}'.format(n),
                    order__ordered_at=random_date_this_year,
                    ordered_quantity=500,
                )
                OrderDetailFactory(
                    stock=fake_stock,
                    order__customer=random.choice(customers),
                    order__reference='order_2_{}'.format(n),
                    order__ordered_at=random_date_this_year,
                    ordered_quantity=500,
                )


class WarehouseFactory(factory.django.DjangoModelFactory):
    # name = factory.Iterator(["Warehouse 1", "Warehouse 2", "Warehouse 3"])
    name = factory.Sequence(lambda n: 'Warehouse_%d' % n) # 'Name {0}'.format(n)
    lat = factory.Faker('coordinate', center=32.4581643, radius=2.5)
    lon = factory.Faker('coordinate', center=-5.884532, radius=2)
    address = factory.Faker('address')

    class Meta:
        model = Warehouse
        django_get_or_create = ('name',)


class StockFactory(factory.django.DjangoModelFactory):
    warehouse = factory.SubFactory(WarehouseFactory)
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = Stock
        django_get_or_create = ('warehouse', 'product')


class StockPolicyFactory(factory.django.DjangoModelFactory):
    stock = factory.SubFactory(StockFactory)
    safety_stock = factory.Faker(
        'pyint',
        min_value=10,
        max_value=50,
        step=1,
    )
    delivery_time = factory.Faker(
        'pyint',
        min_value=1,
        max_value=10,
        step=1,
    )
    # TODO how to make order_point = safety_stock + delivery_time
    order_point = factory.Faker(
        'pyint',
        min_value=1,
        max_value=50,
        step=1,
    )
    target_stock = factory.Faker(
        'pyint',
        min_value=100,
        max_value=200,
        step=1,
    )

    class Meta:
        model = StockPolicy
        django_get_or_create = ('stock')


class StockControlFactory(factory.django.DjangoModelFactory):
    stock = factory.SubFactory(StockFactory)
    inventory_date = factory.Faker(
        'past_datetime',
        start_date='-2y',
        tzinfo=pytz.utc
    )
    product_quantity = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )

    class Meta:
        model = StockControl
        django_get_or_create = ('stock', 'inventory_date')


class CircuitFactory(factory.django.DjangoModelFactory):
    reference = factory.Sequence(lambda n: 'C %d' % n)
    name = factory.Sequence(lambda n: 'Circuit %d' % n)

    class Meta:
        model = Circuit
        django_get_or_create = ('reference',)


class CustomerFactory(factory.django.DjangoModelFactory):
    reference = factory.Sequence(lambda n: 'customer %d' % n)
    name = factory.Faker('name')
    address = factory.Faker('address')
    circuit = factory.SubFactory(CircuitFactory)

    class Meta:
        model = Customer
        django_get_or_create = ('reference',)



class OrderFactory(factory.django.DjangoModelFactory):
    customer = factory.SubFactory(CustomerFactory)
    reference = factory.Sequence(lambda n: 'order_%d' % n)
    ordered_at = factory.Faker(
        'past_datetime',
        start_date='-2y',
        tzinfo=pytz.utc
    )
    total_amount = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )

    class Meta:
        model = Order
        django_get_or_create = ('reference',)


class OrderDetailFactory(factory.django.DjangoModelFactory):
    stock = factory.SubFactory(StockFactory)
    order = factory.SubFactory(OrderFactory)
    unit_price = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )
    ordered_quantity = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )

    class Meta:
        model = OrderDetail
        django_get_or_create = ('stock', 'order')


class DeliveryFactory(factory.django.DjangoModelFactory):
    customer = factory.SubFactory(CustomerFactory)
    reference = factory.Sequence(lambda n: 'sale_%d' % n)
    # reference = factory.Iterator(["sale_1", "sale_2", "sale_3"])
    # reference = factory.Iterator(
    #     itertools.cycle(
    #         (UserFactory() for _ in range(5))
    #     )
    # )
    delivered_at = factory.Faker(
        'past_datetime',
        start_date='-2y',
        tzinfo=pytz.utc
    )
    total_amount = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )

    class Meta:
        model = Delivery
        django_get_or_create = ('reference',)


class DeliveryDetailFactory(factory.django.DjangoModelFactory):
    stock = factory.SubFactory(StockFactory)
    sale = factory.SubFactory(DeliveryFactory)
    unit_price = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )
    delivered_quantity = factory.Faker(
        'random_number',
        digits=4,
        fix_len=False
    )

    class Meta:
        model = DeliveryDetail
        django_get_or_create = ('stock', 'sale')

# TODO : delete these comments once all is settled up
# Random stuff I may use 
# factory boy : category=factory.SelfAttribute('..`self.attribute`'). Not sure what it does yet
# product = factory.SubFactory(
#     ProductFactory, category=factory.SelfAttribute('..product_quantity'))

# name = factory.Sequence(lambda n: 'Merchant %s' % n)
# url = factory.sequence(lambda n: 'www.merchant{n}.com'.format(n=n))


# class User(DjangoModelFactory):
#     # Meta, first_name, last_name - as above...
#     is_staff = False

#     @lazy_attribute
#     def email(self):
#         domain = "myapp.com" if self.is_staff else "example.com"
#         return o.username + "@" + domain

# class AccountFactory(factory.Factory):
#     class Meta:
#         model = Account
#     uid = factory.Sequence(lambda n: n)
#     name = "Test"
# >> > obj1 = AccountFactory(name="John Doe", __sequence=10)

# # CATEGORY_CHOICES is a list of (key, title) tuples
# category = factory.fuzzy.FuzzyChoice(
#     User.CATEGORY_CHOICES, getter=lambda c: c[0])
