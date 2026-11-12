# orders/views.py
from django.db.models import Prefetch
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.filters import OrderingFilter, SearchFilter
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
from rest_framework.throttling import UserRateThrottle , ScopedRateThrottle 

from .services import create_order , update_order_status
from django.core.exceptions import ValidationError , PermissionDenied

from user.public import get_users_map



from drf_spectacular.utils import extend_schema , extend_schema_view
from rest_framework.pagination import PageNumberPagination

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderListSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer

from tools.grpc.client import InventoryServiceError
from tools.caching import do_cache, get_cache_key, get_cached_response

from product.public import get_products_map


MODULE = "order"


class IsOwnerOrStaff(permissions.BasePermission):
    """Object-level: only the owner of the order (or staff) may see/modify it."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_id == request.user.id


@extend_schema_view(
    list=extend_schema(tags=["Order"]),
    retrieve = extend_schema(tags=["Order"])
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    Full CRUD viewset, with `update` / `partial_update` disabled on purpose.
    Status changes go through the dedicated @action `update_status`.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    throttle_classes = [UserRateThrottle]
    
    pagination_class = PageNumberPagination
    pagination_class.page_size=50
    pagination_class.max_page_size=120
    pagination_class.page_size_query_param='size'

    #for more control on it if I want 
    # throttle_classes = [ScopedRateThrottle]
    # throttle_scope = "order_create"

    # ─── queryset & filtering ──────────────────────────────────
    # filter_backends   = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields  = ["status"]
    # ordering_fields   = ["created_at", "total", "status"]
    # ordering          = ["-created_at"]
    # search_fields     = ["id", "items__product_title"]

    def get_permissions(self):
        if self.action == "update_status" :#or self.action == 'list_all' or self.action == 'retrieve_one'  :
            self.permission_classes.append(IsAdminUser)
        else:
            self.permission_classes = [IsAuthenticated]
            

        # return [permission() for permission in permission_classes]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = (
            Order.objects
            # .select_related("user")
            .prefetch_related(
                Prefetch("items", queryset=OrderItem.objects.order_by("created_at"))
            )
        )
        # avoid duplicate rows from search on reverse relation
        # if "search" in self.request.query_params:
        #     qs = qs.distinct()
        if user.is_staff:
            return qs
        return qs.filter(user_id=user.id)

    # ─── serializer routing ────────────────────────────────────
    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "list":
            return OrderListSerializer
        if self.action == "update_status":
            return OrderStatusUpdateSerializer
        return OrderSerializer


    def get_serializer_context(self):
        context = super().get_serializer_context()
        
        # Only fetch users for list/retrieve (READ operations)
        if self.action in ['list', 'retrieve']:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            orders = page if page is not None else queryset
            
            # 1. Extract unique user IDs from the orders
            user_ids = list(set(order.user_id for order in orders))
            
            # 2. Call the User Facade (ONE query to the user database)
            context['user_map'] = get_users_map(user_ids)


            # 2. Fetch Product Map (ONE query)
            # Extract all unique product IDs from all items in all orders on this page
            product_ids = set()
            for order in orders:
                for item in order.items.all():
                    product_ids.add(item.product_id)
            
            context['product_map'] = get_products_map(list(product_ids))

        return context

    # ─── create ────────────────────────────────────────────────



    @extend_schema(
        tags=["Order"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # try:
        order = create_order(user = request.user , items_data=serializer.validated_data["items"])
        # except InventoryServiceError as exc:
        #     return Response(
        #         {
        #             "detail": "Inventory service unavailable. Try again shortly.",
        #             "error":  str(exc),
        #         },
        #         status=status.HTTP_503_SERVICE_UNAVAILABLE,
        #     )
        # except ValidationError as exc:
            
        #     return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)

        out = OrderSerializer(order, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)

    # ─── update / partial_update — DISABLED ────────────────────
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Orders cannot be edited. Cancel and create a new one."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Orders cannot be edited. Use PATCH /orders/{id}/status/ "
                       "to change status."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # ─── destroy — cancel, don't delete ────────────────────────
    @extend_schema(exclude=True)

    def destroy(self, request, *args, **kwargs):

        return Response(
            {"detail": "Orders cannot be deleted"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


    # ─── extra action: PATCH /orders/{id}/status/ ──────────────
    
    @extend_schema(
        tags=["Order"],
    )
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        order = self.get_object()



        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # try:
        updated_status = update_order_status(user = request.user ,order = order , new_status=serializer.validated_data['status'] )
        # except PermissionDenied as e:
        #     return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        # except ValidationError as e:
        #     return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        # # serializer.save()
        return Response(OrderSerializer(updated_status, context=self.get_serializer_context()).data)


    def list(self, request, *args, **kwargs):
        endpoint = self.action
        cache_timeout_minutes = 10
        
        cache_key = get_cache_key(
            module= MODULE,
            endpoint= endpoint,
            user_id= str(request.user.id),
            is_staff= str(request.user.is_staff),
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

    def retrieve(self, request, pk, *args, **kwargs):
        endpoint = self.action
        cache_timeout_minutes = 10
        
        cache_key = get_cache_key(
            module= MODULE,
            endpoint= endpoint,
            wildcard_pk=pk,
            user_id= str(request.user.id),
            is_staff= str(request.user.is_staff)
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
 
    # ─── Admin ────────────────────────────────────────────────

    # @extend_schema(
    #     summary="List All Orders",
    #     operation_id="list_all",
    #     description="List all Orders to the admin",
    #     tags=["Order/Admin"],
    # )
    # @action(detail=False, methods=["GET"], url_path="list_all")
    # def list_all(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    # @extend_schema(
    #     summary="Retrieve one Order",
    #     operation_id="retrieve_one",
    #     description="retrieve one Order to the admin",
    #     tags=["Order/Admin"],
    # )
    # @action(detail=True, methods=["GET"], url_path="retrieve_one")
    # def retrieve_one(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)