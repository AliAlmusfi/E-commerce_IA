from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework import status 
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import UserSerializer , RegisterSerializer
# Create your views here.


class UserViewSet (viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        
        return super().get_permissions()
    

    @extend_schema(
        summary="Register",
        operation_id="register",
        description="registering the user (just for testing [without verification] )",
        tags=["Users/Auth"],
    )
    @action(detail=False , methods=['post'] , serializer_class=RegisterSerializer , url_path='register')
    def register(self , request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status = status.HTTP_201_CREATED)
        return Response(serializer.data , status = status.HTTP_400_BAD_REQUEST)



# @action(detail=False , methods=['post'] , serializer_class=RegisterSerializer , url_path='register')
#     def register(self , request):
#         serializer = self.serializer_class(data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data , status = status.HTTP_201_CREATED)
#         return Response(serializer.data , status = status.HTTP_400_BAD_REQUEST)