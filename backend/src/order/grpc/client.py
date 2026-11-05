# order/grpc/client.py
import grpc
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Iterable

from django.conf import settings

from order.grpc.inventory_pb2 import (
    GetProductByIdRequest,
    GetProductQuantityRequest,
    ReserveProductRequest,
    ReserveOrderRequest,
)
from order.grpc.inventory_pb2_grpc import InventoryServiceStub


class InventoryServiceError(Exception):
    """Raised when the inventory service is unreachable or returns an error."""


_CENTS = Decimal("0.01")


def _to_decimal(price: float) -> Decimal:
    """
    Convert a proto `double` to Decimal, rounding to cents.
    Never trust a raw float for money — this is the boundary where we sanitize it.
    """
    return Decimal(str(price)).quantize(_CENTS, rounding=ROUND_HALF_UP)


class InventoryClient:
    def __init__(self, host: Optional[str] = None, timeout: float = 3.0):
        self.host    = host or settings.INVENTORY_GRPC_HOST
        self.timeout = timeout

    def _stub(self, channel):
        return InventoryServiceStub(channel)

    # ─── read ────────────────────────────────────────────────────
    def get_product(self, product_id: int) -> Optional[dict]:
        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).GetProductById(
                    GetProductByIdRequest(id=product_id),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise InventoryServiceError(
                f"GetProductById({product_id}) failed: {e.code()}"
            ) from e

        if resp.id == 0:        # defensive: some implementations signal "missing" this way
            return None

        return {
            "id":           resp.id,
            "title":        resp.title,
            "manufacturer": resp.manufacturer,
            "image":        resp.image,
            "stock":        resp.stock,
            "price":        _to_decimal(resp.price),   # already a Decimal
        }

    def get_stock(self, product_id: int) -> Optional[int]:
        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).GetProductQuantity(
                    GetProductQuantityRequest(id=product_id),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise InventoryServiceError(
                f"GetProductQuantity({product_id}) failed: {e.code()}"
            ) from e
        return resp.stock

    # ─── write ───────────────────────────────────────────────────
    def reserve_product(self, product_id: int, quantity: int) -> dict:
        """
        Reserve a single product.
        Returns {'success': bool, 'remaining_stock': int, 'message': str}.
        """
        if quantity < 1:
            raise ValueError("quantity must be >= 1")

        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).ReserveProduct(
                    ReserveProductRequest(id=product_id, quantity=quantity),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            raise InventoryServiceError(
                f"ReserveProduct({product_id}, {quantity}) failed: {e.code()}"
            ) from e

        return {
            "success":         resp.success,
            "remaining_stock": resp.remaining_stock,
            "message":         resp.message,
        }

    def reserve_order(self, items: Iterable[tuple[int, int]]) -> dict:
        """
        Reserve multiple products in a single RPC (all-or-nothing).

        `items` is an iterable of (product_id, quantity) pairs.

        Returns {'success': bool}.

        Note: `ReserveOrderResponse` only carries a boolean, so if the
        server rejects the batch, we don't get which item failed.
        """
        items = list(items)
        if not items:
            raise ValueError("items must not be empty")
        for pid, qty in items:
            if qty < 1:
                raise ValueError(f"quantity for product {pid} must be >= 1")

        request = ReserveOrderRequest(
            products=[
                ReserveProductRequest(id=pid, quantity=qty)
                for pid, qty in items
            ]
        )

        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).ReserveOrder(
                    request, timeout=self.timeout
                )
        except grpc.RpcError as e:
            raise InventoryServiceError(
                f"ReserveOrder({items}) failed: {e.code()}"
            ) from e

        return {"success": resp.success}

    def add_product_quantity(self, product_id: int, quantity: int) -> dict:
        """
        Increase stock for a product (e.g. restock).

        Note: the proto reuses `ReserveProductRequest` for this call and
        returns `ReserveOrderResponse` (only `success`), so we build the
        same message and read only the boolean.

        Returns {'success': bool}.
        """
        if quantity < 1:
            raise ValueError("quantity must be >= 1")

        try:
            with grpc.insecure_channel(self.host) as channel:
                # NOTE: proto uses lowercase `a` → stub method is `addProductQuantity`
                resp = self._stub(channel).addProductQuantity(
                    ReserveProductRequest(id=product_id, quantity=quantity),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            raise InventoryServiceError(
                f"addProductQuantity({product_id}, {quantity}) failed: {e.code()}"
            ) from e

        return {"success": resp.success}