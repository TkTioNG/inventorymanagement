from django.contrib import admin

from inventory.models import Store, Material, MaterialStock, MaterialQuantity, Product


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    pass


@admin.register(MaterialStock)
class MaterialStockAdmin(admin.ModelAdmin):
    pass


@admin.register(MaterialQuantity)
class MaterialQuantityAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
