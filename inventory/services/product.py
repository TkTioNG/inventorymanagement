from inventory.models import MaterialQuantity, Store


def get_product_remaining_capacities(obj):
    """Return the remaining capacity for each product in the store"""
    data = []
    if not isinstance(obj, Store):
        return data
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
