from django.urls import path, include

from rest_framework.routers import DefaultRouter

from inventory import views

router = DefaultRouter()
router.register(r'store', views.StoreViewSet, 'store')
router.register(r'user', views.UserViewSet, 'user')
router.register(r'material', views.MaterialViewSet, 'material')
router.register(r'material-stock',
                views.MaterialStockViewSet, 'material-stock')
router.register(r'material-quantity',
                views.MaterialQuantityViewSet, 'material-quantity')
router.register(r'product', views.ProductViewSet, 'product')
router.register(r'restock', views.RestockViewSet, 'restock')
router.register(r'inventory', views.InventoryViewSet, 'inventory')
router.register(r'product-capacity',
                views.ProductCapacityViewSet, 'product-capacity')
router.register(r'sales', views.SalesViewSet, 'sales')

urlpatterns = [
    path('', include(router.urls)),
]
