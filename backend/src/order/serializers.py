
# orders/serializers.py
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .models import Orders, OrderItems
from backend.src.tools.grpc.client import InventoryClient, InventoryServiceError


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItems
        fields = [
            "id", "product_id", "quantity", "unit_price", "subtotal",
        ]
        read_only_fields = fields

    def get_subtotal(self, obj):
        return obj.quantity * obj.unit_price


class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    user_email     = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model  = Orders
        fields = [
            "id", "user_id", "user_email", "status", "status_display",
            "total", "items", "created_at", "updated_at",
        ]
        read_only_fields = fields


    def get_user_email(self , obj):
        user_map = self.context.get('user_map',{})
        user = user_map.get(obj.user_id)

        if user :
            return user.email
        return "Unknown User"


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity   = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model  = Orders
        fields = ["items"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("An order must contain at least one item.")
        ids = [i["product_id"] for i in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Duplicate products are not allowed; combine quantities instead."
            )
        return value





class OrderStatusUpdateSerializer(serializers.ModelSerializer):


    class Meta:
        model  = Orders
        fields = ["status"]





    # orders/serializers.py


class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight order summary for `GET /api/orders/`.
    No nested items — keeps the page small (single-digit KB instead of hundreds).
    """
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    item_count     = serializers.SerializerMethodField()

    class Meta:
        model  = Orders
        fields = [
            "id",
            "status",
            "status_display",
            "total",
            "item_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_item_count(self, obj):
        # Prefer the annotated value if the viewset added it.
        # Otherwise fall back to a per-row count() — correct, just slower.
        return getattr(obj, "item_count_annotated", obj.items.count())