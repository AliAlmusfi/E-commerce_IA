from django.urls import path
from rest_framework.routers import DefaultRouter
from product.views import ProductViewSet

app_name = 'product'

router_product = DefaultRouter()
router_product.register(r'products' , ProductViewSet)

urlpatterns = [
    *router_product.urls
]
