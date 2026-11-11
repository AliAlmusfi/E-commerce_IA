
# orders/serializers.py
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem
# from backend.src.tools.grpc.client import InventoryClient, InventoryServiceError


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    # product_title = serializers.SerializerMethodField()
    # product_manufacturer = serializers.SerializerMethodField()
    # product_image = serializers.SerializerMethodField()
    # product_description = serializers.SerializerMethodField()
    
    class Meta:
        model  = OrderItem
        fields = [
            "id", "product_id", "quantity", "unit_price", "subtotal",
            # "product_title", "product_manufacturer",  "product_image", "product_description"
        ]
        read_only_fields = fields

    def get_subtotal(self, obj):
        return obj.quantity * obj.unit_price

    # def get_product_title(self, obj) -> str:
    #     product_map = self.context.get('product_map', {})
    #     product = product_map.get(obj.product_id)
    #     return product.get("title") if product else "Unknown Product"

    # def get_product_image(self, obj) -> str:
    #     product_map = self.context.get('product_map', {})
    #     product = product_map.get(obj.product_id) 
    #     return product.get("image") if product else ""

    # def get_product_manufacturer(self, obj) -> str:
    #     product_map = self.context.get('product_map', {})
    #     product = product_map.get(obj.product_id)
    #     return product.get("manufacturer") if product else ""
    
    # def get_product_manufacturer(self, obj) -> str:
    #     product_map = self.context.get('product_map', {})
    #     product = product_map.get(obj.product_id)
    #     return product.get("description") if product else ""
    

class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    user_email     = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model  = Order
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
        model  = Order
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
        model  = Order
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
        model  = Order
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