# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
# from django.views.decorators.vary import vary_on_headers

import hashlib
from urllib.parse import urlencode

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
from .serializers import ProductSerializer, ProductUpdateSerializer, ProductStockSerializer
from .filters import ProductFilter , ProductSearchFilter
from .services import create_product, patch_product, update_stock as update_stk

from tools.exceptions import exception_response, grpc_exception_response
from tools.grpc.client import InventoryServiceError
from tools.caching import do_cache, get_cache_key, get_cached_response

# Create your views here.
MODULE = "product"

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
    search_fields = ['title', 'manufacturer']
    ordering_fields = ['title', 'manufacturer', 'created_at', 'updated_at']

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update' or self.action == 'update_stock':
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
                    'manufacturer': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20},
                    'image': {'type': 'string' , 'format': 'binary'},

                },
                'required': ['title' , 'manufacturer' , 'price' , 'stock']
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacturer': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20},
                },
                'required': ['title' , 'manufacturer' , 'price' , 'stock']

            },
        }           
    )
    def create(self, request, *args, **kwargs):
        # try:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # try:
        product = create_product(request.user.id, serializer.validated_data)
        # except InventoryServiceError as e:
        #     return grpc_exception_response(e)

        product_data = self.get_serializer(product)
        return Response(
            product_data,
            status=status.HTTP_201_CREATED
        )
        # except Exception as e:
        #     return exception_response(e)

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
                    'manufacturer': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'image': {'type': 'string' , 'format': 'binary'},
                }
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacturer': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                }
            },
        }         
    )
    # @action(serializer_class = ProductUpdateSerializer)
    def partial_update(self, request, pk, *args, **kwargs):
        # try:
        serializer = ProductUpdateSerializer(data=request.data , partial = True)
        serializer.is_valid(raise_exception=True)
        # try:
        product = patch_product(pk, request.user.id, serializer.validated_data)
        # except InventoryServiceError as e:
        #     return grpc_exception_response(e)

        product_data = self.get_serializer(product)
        return Response(
            product_data,
            status=status.HTTP_202_ACCEPTED
        )
        # except Exception as e:
        #     return exception_response(e)

    @extend_schema(
        summary="Update Stock",
        operation_id="update_stock",
        description="update product stock",
        tags=["Product"],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'stock': {'type': 'integer' , 'example': 20}
                },
                'required': ['stock']
            },
        }        
    )
    @action(detail=True, methods=["PATCH"])
    def update_stock(self, request, pk, *args, **kwargs):
        # try:
        serializer = ProductStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
            # try:
        updated = update_stk(pk, request.user.id, serializer.validated_data['amount'])
            # except InventoryServiceError as e:
            #     return grpc_exception_response(e)

        return Response(
            {'success': updated}, # TODO: Error Unification
            status=status.HTTP_202_ACCEPTED
        )
        # except Exception as e:
        #     return exception_response(e)
    
    @extend_schema(
        summary="List",
        operation_id="list",
        description="list Product to user",
        tags=["Product"],
    )    
    def list(self, request, *args, **kwargs):
        endpoint = self.action
        cache_timeout_minutes = 30
        
        cache_key = get_cache_key(
            module= MODULE,
            endpoint= endpoint,
            params_hash= request.query_params.lists(),
            page= request.query_params.get('page', '1')
        )
        cached_response = get_cached_response(cache_key)
        if cached_response is not None:
            return cached_response

        
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response:Response = self.get_paginated_response(serializer.data)
            do_cache(
                cache_key= cache_key,
                data= response.data,
                timeout= 60 * cache_timeout_minutes
            )
            return response

        serializer = self.get_serializer(queryset, many=True)
        do_cache(
            cache_key= cache_key,
            data= serializer.data,
            timeout= 60 * cache_timeout_minutes
        )
        return Response(serializer.data)
        # return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve",
        operation_id="retrieve",
        description="retrieve Product to user",
        tags=["Product"],
    ) 
    def retrieve(self, request, pk, *args, **kwargs):
        endpoint = self.action
        cache_timeout_minutes = 30
        
        cache_key = get_cache_key(
            module= MODULE,
            endpoint= endpoint,
            wildcard_pk=pk
        )
        cached_response = get_cached_response(cache_key)
        if cached_response is not None:
            return cached_response
        
        
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        do_cache(
            cache_key= cache_key,
            data= serializer.data,
            timeout= 60 * cache_timeout_minutes
        )
        return Response(serializer.data)


    @extend_schema(
        summary="Delete",
        operation_id="delete",
        description="delete Product by admin",
        tags=["Product"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


    @extend_schema(
        exclude=True,
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
                    'manufacturer': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20},
                    'image': {'type': 'string' , 'format': 'binary'},

                },
                'required': ['title' , 'manufacturer' , 'price' , 'stock']
            },
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Giant x7 ir'},
                    'description': {'type': 'string', 'example': 'Perfect cycle to the long ride'},
                    'manufacturer': {'type': 'string' , 'example': 'Giant '},
                    'price': {'type': 'integer' , 'example': 200},
                    'stock': {'type': 'integer' , 'example': 20},

                },
                'required': ['title' , 'manufacturer' , 'price' , 'stock']

            },
        }         
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)




