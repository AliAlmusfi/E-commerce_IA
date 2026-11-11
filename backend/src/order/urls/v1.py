from django.urls import path, include
from rest_framework.routers import DefaultRouter
from order.views import OrderViewSet

app_name = 'order'

router = DefaultRouter()
# Point to the V2 ViewSet
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]