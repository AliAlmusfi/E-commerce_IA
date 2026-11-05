# orders/views.py
from django.db.models import Prefetch
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.filters import OrderingFilter, SearchFilter
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser





from drf_spectacular.utils import extend_schema

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderListSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer

from .grpc.client import InventoryServiceError


class IsOwnerOrStaff(permissions.BasePermission):
    """Object-level: only the owner of the order (or staff) may see/modify it."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_id == request.user.id


class OrderViewSet(viewsets.ModelViewSet):
    """
    Full CRUD viewset, with `update` / `partial_update` disabled on purpose.
    Status changes go through the dedicated @action `update_status`.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    # ─── queryset & filtering ──────────────────────────────────
    # filter_backends   = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields  = ["status"]
    # ordering_fields   = ["created_at", "total", "status"]
    # ordering          = ["-created_at"]
    # search_fields     = ["id", "items__product_title"]

    def get_permissions(self):
        if self.action == 'list_all' or self.action == 'retrieve_one':
            self.permission_classes.append(IsAdminUser)
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = (
            Order.objects
            .select_related("user")
            .prefetch_related(
                Prefetch("items", queryset=OrderItem.objects.order_by("created_at"))
            )
        )
        # avoid duplicate rows from search on reverse relation
        if "search" in self.request.query_params:
            qs = qs.distinct()
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    # ─── serializer routing ────────────────────────────────────
    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "list":
            return OrderListSerializer
        if self.action == "update_status":
            return OrderStatusUpdateSerializer
        return OrderSerializer

    # ─── create ────────────────────────────────────────────────





    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = serializer.save()
        except InventoryServiceError as exc:
            return Response(
                {
                    "detail": "Inventory service unavailable. Try again shortly.",
                    "error":  str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

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
        # order = self.get_object()

        # if order.status not in (Order.Status.PENDING, Order.Status.PAID):
        #     return Response(
        #         {"detail": f"Cannot cancel an order in status '{order.status}'."},
        #         status=status.HTTP_409_CONFLICT,
        #     )

        # order.status = Order.Status.CANCELLED
        # order.save(update_fields=["status", "updated_at"])
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Orders cannot be deleted"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


    # ─── extra action: PATCH /orders/{id}/status/ ──────────────
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        order = self.get_object()

        if not request.user.is_staff: #and request.data.get("status") != Order.Status.CANCELLED:
            return Response(
                {"detail": "Only staff can change order status (except to cancel)."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order, context=self.get_serializer_context()).data)


 
    # ─── Admin ────────────────────────────────────────────────

    @extend_schema(
        summary="List All Orders",
        operation_id="list_all",
        description="List all Orders to the admin",
        tags=["Order/Admin"],
    )
    @action(detail=False, methods=["GET"], url_path="list_all")
    def list_all(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve one Order",
        operation_id="retrieve_one",
        description="retrieve one Order to the admin",
        tags=["Order/Admin"],
    )
    @action(detail=True, methods=["GET"], url_path="retrieve_one")
    def retrieve_one(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)