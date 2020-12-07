from django.urls import path, include

from rest_framework.routers import DefaultRouter

from inventory import api

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
    path('', )
]
