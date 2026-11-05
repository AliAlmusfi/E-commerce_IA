from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router_product = DefaultRouter()
router_product.register(r'products' , ProductViewSet)

urlpatterns = [
    *router_product.urls
]
