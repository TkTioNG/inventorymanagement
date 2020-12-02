from inventory.models import Material, MaterialStock, MaterialQuantity


def get_restock_total_price(materials):
    total_price = 0
    for material in materials:
        if isinstance(material, dict):
            price = Material.objects.get(pk=material.get('material')).price
            total_price += price * material.get('quantity')
        elif isinstance(material, MaterialStock):
            price = Material.objects.get(pk=material.material.pk).price
            total_price += price * \
                (material.max_capacity - material.current_capacity)

    return round(total_price, 2)


def get_model_obj_property(model, instance, exclude=("pk")):
    field_names = [f.name for f in model._meta.fields]
    property_names = [
        name for name in dir(model)
        if isinstance(getattr(model, name), property) and name not in exclude
    ]
    return dict((name, getattr(instance, name)) for name in field_names + property_names)


def get_product_remaining_capacities(obj):
    data = []
    for product in obj.products.all():
        material_quantities_need = MaterialQuantity.objects.filter(
            product=product
        )
        material_quantity_list = []
        for material_quantity in material_quantities_need:
            quantity_needed = material_quantity.quantity
            material_stock = obj.material_stocks.get(
                material=material_quantity.ingredient
            )
            current_quantity = material_stock.current_capacity
            material_quantity_list.append(
                int(current_quantity / quantity_needed)
            )
        data.append({
            'product': product.product_id,
            'quantity': min(material_quantity_list, default=0),
        })
    return data
