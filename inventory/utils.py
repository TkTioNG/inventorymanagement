from inventory.models import Material, MaterialStock


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

    return total_price
