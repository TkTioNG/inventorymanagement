from django.contrib.auth.models import User
import factory

from inventory.models import Store, Material, MaterialStock, MaterialQuantity, Product


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('name')
    email = factory.Faker('email')

    class Meta:
        model = User


class StoreFactory(factory.django.DjangoModelFactory):
    store_name = factory.Faker('name')
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of products were passed in
            for product in extracted:
                self.products.add(product)

    class Meta:
        model = Store


class MaterialFactory(factory.django.DjangoModelFactory):
    price = factory.Faker('pydecimal', right_digits=2,
                          positive=True, max_value=99999999.99)
    name = factory.Faker('name')

    class Meta:
        model = Material


class MaterialStockFactory(factory.django.DjangoModelFactory):
    store = factory.SubFactory(StoreFactory)
    material = factory.SubFactory(MaterialFactory)
    max_capacity = factory.Faker('pyint')
    current_capacity = factory.Faker('pyint', max_value=max_capacity)

    class Meta:
        model = MaterialStock


class ProductFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')

    class Meta:
        model = Product


class MaterialQuantityFactory(factory.django.DjangoModelFactory):
    quantity = factory.Faker('pyint')
    product = factory.SubFactory(ProductFactory)
    ingredient = factory.SubFactory(MaterialFactory)

    class Meta:
        model = MaterialQuantity
