from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User

from inventory.models import Store, Material, MaterialStock, MaterialQuantity, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class MaterialStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialStock
        fields = '__all__'


class MaterialQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialQuantity
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class RestockSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField()

    def get_quantity(self, obj):
        return obj.max_capacity - obj.current_capacity

    def validate_quantity(self, quantity):
        if not isinstance(quantity, int):
            raise ValidationError(detail="quantity is not an integer")
        return quantity

    def update(self, instance, validated_data):
        print(self.initial_data)
        instance.current_capacity = self.initial_data.get('quantity')
        instance.save()

        return instance

    class Meta:
        model = MaterialStock
        fields = ('material', 'quantity',)


class StoreCapacityPercentageSerializer(serializers.ModelSerializer):
    percentage_of_capacity = serializers.SerializerMethodField()

    def get_percentage_of_capacity(self, obj):
        return round(obj.current_capacity / obj.max_capacity * 100, 2)

    class Meta:
        model = MaterialStock
        fields = ('material', 'max_capacity',
                  'current_capacity', 'percentage_of_capacity',)


class ProductCapacitySerializer(serializers.ModelSerializer):
    remaining_capacity = serializers.SerializerMethodField()

    def get_remaining_capacity(self, obj):
        data = []
        for product in obj.products.all():
            material_quantities_need = MaterialQuantity.objects.filter(
                product=product)
            material_quantity_list = []
            for material_quantity in material_quantities_need:
                quantity_needed = material_quantity.quantity
                material_stock = obj.material_stocks.get(
                    material=material_quantity.ingredient)
                current_quantity = material_stock.current_capacity
                material_quantity_list.append(
                    int(current_quantity / quantity_needed))
            data.append({
                'product': product.product_id,
                'quantity': min(material_quantity_list, default=0),
            })

        return data

    class Meta:
        model = Store
        fields = ('remaining_capacity',)


class SalesSerializer(serializers.Serializer):

    sale = serializers.SerializerMethodField()

    def get_sale(self, obj):
        data = []
        for product in obj.products.all():
            material_quantities_need = MaterialQuantity.objects.filter(
                product=product)
            material_quantity_list = []
            for material_quantity in material_quantities_need:
                quantity_needed = material_quantity.quantity
                material_stock = obj.material_stocks.get(
                    material=material_quantity.ingredient)
                current_quantity = material_stock.current_capacity
                material_quantity_list.append(
                    int(current_quantity / quantity_needed))
            data.append({
                'product': product.product_id,
                'quantity': min(material_quantity_list, default=0),
            })

        return data

    def is_valid(self, raise_exception=False):
        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                sale = self.initial_data.get("sale")
                for product_sold in sale:
                    sold_quantity = product_sold.get('quantity')
                    material_quantities_need = MaterialQuantity.objects.filter(
                        product=product_sold.get('product'))
                    for material_quantity in material_quantities_need:
                        material_quantity_needed = material_quantity.quantity
                        material_stock_obj = self.instance.material_stocks.get(
                            material=material_quantity.ingredient)
                        if (material_stock_obj.current_capacity < material_quantity_needed * sold_quantity):
                            raise ValidationError(detail="Ingredient - {0} is not enough for product - {1}".format(
                                material_quantity.ingredient, material_quantity.product))

                self._validated_data = self.initial_data
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)

    def create(self):
        sale = self.validated_data.get('sale')

        for product_sold in sale:
            sold_quantity = product_sold.get('quantity')
            material_quantities_need = MaterialQuantity.objects.filter(
                product=product_sold.get('product'))
            for material_quantity in material_quantities_need:
                material_quantity_needed = material_quantity.quantity
                material_stock_obj = self.instance.material_stocks.get(
                    material=material_quantity.ingredient)
                material_stock_obj.current_capacity = material_stock_obj.current_capacity - \
                    material_quantity_needed * sold_quantity
                material_stock_obj.save()

        return self.instance

    class Meta:
        fields = ('sale',)
