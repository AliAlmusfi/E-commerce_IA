"""
URL configuration for E_commerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from drf_spectacular.utils import extend_schema , extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView



api_patterns = [
    path('users/token/' , extend_schema_view(
        post=extend_schema(
            tags=['Users/Auth'],
            summary="Token",
            request={
                'application/json':{
                    'type':'object',
                    'properties':{
                        'email':{'type':'string', 'example':'m@m.com'},
                        'password':{'type':'string', 'example':'12345678'}
                    }
                }
            }
        ))(TokenObtainPairView.as_view()) , name='token_obtain_pair'),
    path('users/token/refresh/' , extend_schema_view(post=extend_schema(tags=['Users/Auth'], summary="Refresh Token"))(TokenRefreshView.as_view()) , name='token_refresh'),
    path('' , include('user.urls') ),
    
]

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/' , include(api_patterns)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]
