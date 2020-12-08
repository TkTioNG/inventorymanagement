def get_model_obj_property(model, instance, exclude=("pk")):
    field_names = [f.name for f in model._meta.fields]
    property_names = [
        name for name in dir(model)
        if isinstance(getattr(model, name), property) and name not in exclude
    ]
    return dict((name, getattr(instance, name)) for name in field_names + property_names)
