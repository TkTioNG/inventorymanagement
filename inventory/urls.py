from django.urls import path, include

from rest_framework.routers import DefaultRouter

from inventory import api
from inventory import views

router = DefaultRouter()
router.register(r'store', api.StoreViewSet, 'store')
router.register(r'user', api.UserViewSet, 'user')
router.register(r'material', api.MaterialViewSet, 'material')
router.register(r'material-stock',
                api.MaterialStockViewSet, 'material-stock')
router.register(r'material-quantity',
                api.MaterialQuantityViewSet, 'material-quantity')
router.register(r'product', api.ProductViewSet, 'product')
router.register(r'restock', api.RestockViewSet, 'restock')
router.register(r'inventory', api.InventoryViewSet, 'inventory')
router.register(r'product-capacity',
                api.ProductCapacityViewSet, 'product-capacity')
router.register(r'sales', api.SalesViewSet, 'sales')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('', views.index),
    path('products', views.products, name="products"),
    path('materials', views.materials, name="materials"),
    path('material-stock', views.material_stocks, name="material-stock"),
    path('restock', views.restock, name="restock"),
    path('inventory', views.inventory, name="inventory"),
    path('product-capacity', views.productCapacity, name="product-capacity"),
    path('sales', views.sales, name="sales"),
]
