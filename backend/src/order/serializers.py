
# from rest_framework import serializers
# from .models import OrderItem , Order


# class OrderItemSerializer(serializers.ModelSerializer):
#     subtotal = serializers.SerializerMethodField()

#     class Meta:
#         model  = OrderItem
#         fields = ["id", "product_id", "product_name", "quantity", "unit_price", "subtotal"]
#         read_only_fields = fields

#     def get_subtotal(self, obj):
#         return obj.quantity * obj.unit_price



# class OrderItemCreateSerializer(serializers.Serializer):
#     product_id = serializers.IntegerField(min_value=1)
#     quantity   = serializers.IntegerField(min_value=1)





# class OrderCreateSerializer(serializers.ModelSerializer):
#     items = OrderItemCreateSerializer(many=True, write_only=True)

#     class Meta:
#         model  = Order
#         fields = ["items"]

#     def validate_items(self, value):
#         if not value:
#             raise serializers.ValidationError("An order must contain at least one item.")
#         # Reject duplicate product IDs in one order
#         ids = [item["product_id"] for item in value]
#         if len(ids) != len(set(ids)):
#             raise serializers.ValidationError("Duplicate products are not allowed; combine quantities instead.")
#         return value

#     def create(self, validated_data):
#         items_data  = validated_data.pop("items")
#         user        = self.context["request"].user
#         product_ids = [item["product_id"] for item in items_data]

#         client = ProductClient()

#         try:
#             products = client.get_products(product_ids)
#         except ProductServiceError as e:
#             raise serializers.ValidationError({"detail": str(e)})

#         # Verify every product exists and is active
#         missing = [pid for pid in product_ids if pid not in products]
#         if missing:
#             raise serializers.ValidationError(
#                 {"detail": f"Unknown product(s): {missing}"}
#             )
#         inactive = [pid for pid in product_ids if not products[pid]["is_active"]]
#         if inactive:
#             raise serializers.ValidationError(
#                 {"detail": f"Product(s) no longer available: {inactive}"}
#             )

#         from decimal import Decimal

#         with transaction.atomic():
#             order = Order.objects.create(user=user)
#             total = Decimal("0.00")

#             for item_data in items_data:
#                 pid      = item_data["product_id"]
#                 qty      = item_data["quantity"]
#                 product  = products[pid]
#                 unit_price = Decimal(str(product["price"]))   # NEVER trust client price

#                 OrderItem.objects.create(
#                     order=order,
#                     product_id=pid,
#                     product_name=product["name"],           # snapshot
#                     quantity=qty,
#                     unit_price=unit_price,
#                 )
#                 total += unit_price * qty

#             order.total = total
#             order.save(update_fields=["total"])

#         return order


# orders/serializers.py
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem
from order.grpc.client import InventoryClient, InventoryServiceError


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = [
            "id", "product_id", "quantity", "unit_price", "subtotal",
        ]
        read_only_fields = fields

    def get_subtotal(self, obj):
        return obj.quantity * obj.unit_price


class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    user_email     = serializers.EmailField(source="user.email", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model  = Order
        fields = [
            "id", "user", "user_email", "status", "status_display",
            "total", "items", "created_at", "updated_at",
        ]
        read_only_fields = fields


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

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user       = self.context["request"].user
        client     = InventoryClient()

        # ─── Phase 1: fetch every product (no DB writes yet) ─────
        # Proto still has no batch GetProduct RPC, so this stays N calls.
        # Fine for small carts; batch it later if carts grow.
        products = {}
        for item in items_data:
            pid     = item["product_id"]
            product = client.get_product(pid)
            if product is None:
                raise serializers.ValidationError(
                    {"detail": f"Product {pid} does not exist."}
                )
            if product["stock"] < item["quantity"]:
                raise serializers.ValidationError(
                    {"detail": f"Product '{product['title']}' has only "
                            f"{product['stock']} in stock."}
                )
            products[pid] = product

        # ─── Phase 2: reserve stock atomically (batch RPC) ──────
        # ReserveOrder is all-or-nothing server-side. If it fails,
        # nothing was reserved → no cleanup needed here.
        # try:
        result = client.reserve_order(
            (item["product_id"], item["quantity"]) for item in items_data
        )
        # except InventoryServiceError as e:
        #     raise serializers.ValidationError({"detail": str(e)})

        if not result["success"]:
            # ReserveOrderResponse only carries `success`, so we re-check
            # stock to produce a useful message. This is diagnostic only —
            # the batch has already rolled back server-side.
            self._raise_reservation_failure(client, items_data, products)

        # ─── Phase 3: persist order + items ─────────────────────
        try:
            with transaction.atomic():
                order = Order.objects.create(user=user)
                total = Decimal("0.00")

                for item in items_data:
                    product    = products[item["product_id"]]
                    unit_price = product["price"]          # already a Decimal
                    qty        = item["quantity"]

                    OrderItem.objects.create(
                        order=order,
                        product_id=item["product_id"],
                        # product_title=product["title"],             # snapshot
                        # product_manufacturer=product["manufacturer"],
                        # product_image=product["image"],
                        quantity=qty,
                        unit_price=unit_price,
                    )
                    total += unit_price * qty

                order.total = total
                order.save(update_fields=["total"])
        except Exception:
            # DB failed AFTER stock was reserved. Use addProductQuantity
            # as a release mechanism (it just adds back to stock).
            self._release_reserved(client, items_data)
            raise

        return order

    @staticmethod
    def _raise_reservation_failure(client, items_data, products):
        """
        Best-effort diagnosis for a failed batch reserve.
        Re-fetches stock to identify the shortfall, then raises.
        """
        for item in items_data:
            pid = item["product_id"]
            current = client.get_stock(pid)
            if current is None:
                raise serializers.ValidationError(
                    {"detail": f"Product {pid} is no longer available."}
                )
            if current < item["quantity"]:
                raise serializers.ValidationError(
                    {"detail": f"Product '{products[pid]['title']}' has only "
                            f"{current} in stock."}
                )
        # None of the products look short → likely a race with another order.
        raise serializers.ValidationError(
            {"detail": "Could not reserve stock (a concurrent order may have "
                    "taken it). Please try again."}
        )


    @staticmethod
    def _release_reserved(client, items_data):
        """
        Compensate: return reserved stock back to inventory via addProductQuantity.
        Called only when the DB write fails after a successful batch reserve.
        Logs failures so ops can reconcile manually.
        """
        import logging
        log = logging.getLogger(__name__)

        for item in items_data:
            pid, qty = item["product_id"], item["quantity"]
            try:
                result = client.add_product_quantity(pid, qty)
                if not result["success"]:
                    log.error("Failed to release stock: product=%s qty=%s", pid, qty)
            except Exception as e:
                log.error("Exception releasing stock: product=%s qty=%s err=%s", pid, qty, e)



class OrderStatusUpdateSerializer(serializers.ModelSerializer):

    """
    Accepts exactly one field: `status`. Enforces legal transitions.
    Used by PATCH /api/orders/{id}/status/.
    """
    class Meta:
        model  = Order
        fields = ["status"]

    # ── Allowed transitions, keyed by current status ───────────────
    # None means "any current status is allowed" — used for first-time set.
    ALLOWED_TRANSITIONS = {
        Order.Status.PENDING:  {Order.Status.COMPLETE},
        Order.Status.COMPLETE: set(),    # terminal
    }

    def validate_status(self, value):
        """`value` has already passed the `choices=` check — it's a valid status string."""
        if self.instance is None:
            # Shouldn't happen (this serializer is only used for updates),
            # but guard against misuse as a create serializer.
            return value

        current = self.instance.status
        if value == current:
            raise serializers.ValidationError(
                f"Order is already in status '{current}'."
            )

        allowed = self.ALLOWED_TRANSITIONS.get(current, set())
        if value not in allowed:
            pretty = ", ".join(s.value for s in allowed) or "none (terminal state)"
            raise serializers.ValidationError(
                f"Cannot transition from '{current}' to '{value}'. "
                f"Allowed next: {pretty}."
            )
        return value




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