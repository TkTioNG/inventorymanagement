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

    return float(round(total_price, 2))


def get_model_obj_property(model, instance):
    field_names = [f.name for f in model._meta.fields]
    property_names = [name for name in dir(
        model) if isinstance(getattr(model, name), property)]
    return dict((name, getattr(instance, name)) for name in field_names + property_names)
