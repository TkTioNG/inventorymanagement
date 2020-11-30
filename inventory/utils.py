from inventory.models import Material


def get_restock_total_price(materials):
    total_price = 0
    for material in materials:
        price = Material.objects.get(pk=material.get('material')).price
        total_price = price * material.get('quantity')
    return total_price
