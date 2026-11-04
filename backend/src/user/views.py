from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
from rest_framework.decorators import action
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from .models import User 
from .serializers import UserSerializer , RegisterSerializer , MeSerializer
# Create your views here.


class UserViewSet (viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes.append(IsAdminUser)
        if self.action == 'me':
            self.permission_classes.append(IsAuthenticated)
        
        return super().get_permissions()
    

    @extend_schema(
        summary="Register",
        operation_id="register",
        description="registering the user",
        tags=["Users/Auth"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john'},
                    'email': {'type': 'string', 'example': 'a@agmail.come'},
                    'password': {'type': 'string' , 'example': 'Ax3gD5Cv'}
                },
                'required': ['username', 'email' , 'password']
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john'},
                    'email': {'type': 'string', 'example': 'a@agmail.come'},
                    'password': {'type': 'string' , 'example': 'Ax3gD5Cv'}
                },
                'required': ['username', 'email' , 'password']
            },
        }
    )
    @action(detail=False , methods=['post'] , serializer_class=RegisterSerializer , url_path='register')
    def register(self , request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        summary="List Users",
        operation_id="list_users",
        description="List all users to the admin",
        tags=["Users"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve User",
        operation_id="retrieve_users",
        description="retrieve one user to the admin",
        tags=["Users"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Me",
        operation_id="me",
        description="retrieve user own info",
        tags=["Users"],
    )
    @action(detail=False , methods=['GET'] , serializer_class = MeSerializer)
    def me(self , request):
        print(request.user.id)
        print("////////////////////////////////////////////////////////////////////////////")
        # if request.user == None:
        #     return Response({"details":"You are Not Authenticated"} , status=status.HTTP_404_NOT_FOUND)
        # user = User.objects.filter(pk=request.user.id).first()  
        # serializer = self.get_serializer(isinstance=user)
        # if serializer.is_valid():
        #     return Response(serializer.data , status=status.HTTP_200_OK)
        # return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

    



    