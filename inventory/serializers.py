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
        # quantity must be an integer
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

    def validate_remaining_capacities(self, remaining_capacities):
        # remaining_capacity should be a list
        if not isinstance(remaining_capacities, list):
            raise ValidationError(
                detail="Incorrect format id obtained"
            )
        for product in remaining_capacities:
            # product and quantity key must exist
            if "product" not in product or "quantity" not in product:
                raise ValidationError(
                    detail="Missing information in remaining_capacities"
                )
        return remaining_capacities

    class Meta:
        model = Store
        fields = ('remaining_capacities',)


class SalesSerializer(serializers.Serializer):

    sale = serializers.SerializerMethodField()

    def get_sale(self, obj):
        return get_product_remaining_capacities(obj)

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)

        if "sale" not in self.initial_data:
            raise ValidationError(detail="Missing Information in sales")

        # if sale is post, there must be products exist in the data
        sale = self.initial_data.get("sale")
        if not hasattr(sale, "__len__") or len(sale) == 0:
            raise ValidationError(
                detail="No product is sold"
            )

        for product_sold in sale:
            # product and quantity key must be exist
            if "product" not in product_sold or "quantity" not in product_sold:
                raise ValidationError(
                    detail="Missing Information in products of sales"
                )

            sold_quantity = product_sold.get('quantity')
            if not isinstance(sold_quantity, int) or sold_quantity < 0:
                raise ValidationError(
                    detail="Sold quantity should be valid integer"
                )
            materials_needed = MaterialQuantity.objects.filter(
                product=product_sold.get('product')
            )
            if materials_needed.count() > 0:
                self.validate_material_sufficiency(
                    materials_needed, sold_quantity
                )

        self._validated_data["sale"] = self.initial_data["sale"]

        return not bool(self._errors)

    def validate_material_sufficiency(self, materials_needed, sold_quantity):
        # Check the sufficiency of the material, if not enough, raise error
        for material in materials_needed:
            material_quantity = material.quantity
            material_stock_obj = self.instance.material_stocks.get(
                material=material.ingredient
            )

            if material_stock_obj.current_capacity < material_quantity * sold_quantity:
                raise ValidationError(
                    detail="Ingredient - {0} is not enough for product - {1}"
                    .format(
                        material.ingredient,
                        material.product
                    )
                )
        return materials_needed

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
