from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User

from inventory.models import Store, Material, MaterialStock, MaterialQuantity, Product
from inventory.utils import get_product_remaining_capacities


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
        if instance.current_capacity + self.initial_data.get('quantity') > instance.max_capacity \
                or self.initial_data.get('quantity') < 0:
            raise ValidationError(
                detail="Current capacity cannot be greater than max capacity or negative value"
            )

        instance.current_capacity = instance.current_capacity + \
            self.initial_data.get('quantity')
        instance.save()

        return instance

    class Meta:
        model = MaterialStock
        fields = ('material', 'quantity',)


class InventorySerializer(serializers.ModelSerializer):
    percentage_of_capacity = serializers.SerializerMethodField()

    def get_percentage_of_capacity(self, obj):
        return round(obj.current_capacity / obj.max_capacity * 100, 2)

    class Meta:
        model = MaterialStock
        fields = ('material', 'max_capacity',
                  'current_capacity', 'percentage_of_capacity',)


class ProductCapacitySerializer(serializers.ModelSerializer):
    remaining_capacities = serializers.SerializerMethodField()

    def get_remaining_capacities(self, obj):
        return get_product_remaining_capacities(obj)

    class Meta:
        model = Store
        fields = ('remaining_capacities',)


class SalesSerializer(serializers.Serializer):

    sale = serializers.SerializerMethodField()

    def get_sale(self, obj):
        return get_product_remaining_capacities(obj)

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
                    if not isinstance(sold_quantity, int) or sold_quantity < 0:
                        raise ValidationError(
                            detail="Sold quantity should be valid integer"
                        )
                    material_quantities_need = MaterialQuantity.objects.filter(
                        product=product_sold.get('product')
                    )
                    for material_quantity in material_quantities_need:
                        material_quantity_needed = material_quantity.quantity
                        material_stock_obj = self.instance.material_stocks.get(
                            material=material_quantity.ingredient
                        )

                        if (material_stock_obj.current_capacity < material_quantity_needed * sold_quantity):
                            raise ValidationError(
                                detail="Ingredient - {0} is not enough for product - {1}"
                                .format(
                                    material_quantity.ingredient,
                                    material_quantity.product
                                )
                            )

                self._validated_data = self.initial_data
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def update(self, instance, validated_data):
        sale = self.validated_data.get('sale')

        for product_sold in sale:
            sold_quantity = product_sold.get('quantity')
            material_quantities_need = MaterialQuantity.objects.filter(
                product=product_sold.get('product')
            )
            for material_quantity in material_quantities_need:
                material_quantity_needed = material_quantity.quantity
                material_stock_obj = self.instance.material_stocks.get(
                    material=material_quantity.ingredient
                )
                material_stock_obj.current_capacity = material_stock_obj.current_capacity - \
                    material_quantity_needed * sold_quantity
                material_stock_obj.save()

        return self.instance

    class Meta:
        fields = ('sale',)
