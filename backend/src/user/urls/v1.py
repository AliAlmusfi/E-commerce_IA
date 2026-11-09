from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet

app_name = 'user'

router = DefaultRouter()
# Point to the V2 ViewSet
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]