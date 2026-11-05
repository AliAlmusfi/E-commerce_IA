from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_spectacular.utils import extend_schema

from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter , ProductSearchFilter


# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    pagination_class = PageNumberPagination
    pagination_class.page_size=50
    pagination_class.max_page_size=120
    pagination_class.page_size_query_param='size'
    # filtering/searching/ordering
    filter_backends = [
        DjangoFilterBackend,
        ProductSearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ['title', 'manufacture']
    ordering_fields = ['title', 'manufacture', 'created_at', 'updated_at']

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            self.permission_classes.append(IsAdminUser)
        return super().get_permissions()

    @extend_schema(
        summary="Create",
        operation_id="create",
        description="Create Product by admin",
        tags=["Product"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacture': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['title' , 'manufacture' , 'price' , 'stock']
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacture': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['title' , 'manufacture' , 'price' , 'stock']

            },
        }           
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Delete",
        operation_id="delete",
        description="delete Product by admin",
        tags=["Product"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


    @extend_schema(
        summary="Update",
        operation_id="update",
        description="Update Product by admin",
        tags=["Product"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacture': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['title' , 'manufacture' , 'price' , 'stock']
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacture': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['title' , 'manufacture' , 'price' , 'stock']

            },
        }         
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    
    @extend_schema(
        summary="Partial Update",
        operation_id="partial_update",
        description="Partial Update Product by admin",
        tags=["Product"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacture': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['title' , 'manufacture' , 'price' , 'stock']
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacture': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['title' , 'manufacture' , 'price' , 'stock']

            },
        }         
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    
    @extend_schema(
        summary="List",
        operation_id="list",
        description="list Product to user",
        tags=["Product"],
    )    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve",
        operation_id="retrieve",
        description="retrieve Product to user",
        tags=["Product"],
    ) 
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)