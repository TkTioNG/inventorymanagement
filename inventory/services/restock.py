from inventory.models import Material


def get_restock_total_price(materials):
    total_price = 0
    for material in materials:
        if "material" in material or "quantity" in material:
            try:
                price = Material.objects.get(pk=material.get('material')).price
                total_price += price * material.get('quantity')
            except Material.DoesNotExist:
                raise ValueError("material is not found.")

    return round(total_price, 2)
