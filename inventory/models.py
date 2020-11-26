from django.db import models


class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=100, unique=True)
    products = models.ManyToManyField('Product')
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='stores')


class MaterialStock(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='material_stocks')
    material = models.ForeignKey(
        'Material', on_delete=models.CASCADE, related_name='material_stocks')
    max_capacity = models.IntegerField(default=10000)
    current_capacity = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Material Stocks"
        constraints = [
            models.CheckConstraint(check=models.Q(
                max_capacity__gt=0), name='max_capacity__gt_0'),
            models.CheckConstraint(check=models.Q(current_capacity__gte=0) & models.Q(
                current_capacity__lte=models.F('max_capacity')), name='current_capacity_valid'),
        ]


class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(
                price__gte=0.00), name='price__gte_0'),
        ]


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    materials = models.ManyToManyField(
        'Material', related_name='products', through='MaterialQuantity')


class MaterialQuantity(models.Model):
    quantity = models.IntegerField()
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='material_quantities')
    ingredient = models.ForeignKey('Material', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Material Quantities"
        constraints = [
            models.CheckConstraint(check=models.Q(
                quantity__gt=0), name='quantity__gt_0'),
            models.UniqueConstraint(
                fields=['product', 'ingredient'], name='unique_product_ingredient')
        ]
