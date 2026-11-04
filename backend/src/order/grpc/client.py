# orders/grpc/client.py
import grpc
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from django.conf import settings

from order.grpc.inventory_pb2        import (
    GetProductByIdRequest,
    GetProductQuantityRequest,
    ReserveProductRequest,
)
from order.grpc.inventory_pb2_grpc   import InventoryServiceStub


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
            raise InventoryServiceError(f"GetProductById({product_id}) failed: {e.code()}") from e

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
            raise InventoryServiceError(f"GetProductQuantity({product_id}) failed: {e.code()}") from e
        return resp.stock

    # ─── write ───────────────────────────────────────────────────
    def reserve_product(self, product_id: int, quantity: int) -> dict:
        """
        Returns {'success': bool, 'remaining_stock': int, 'message': str}.
        Raises InventoryServiceError on transport failures.
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
            raise InventoryServiceError(f"ReserveProduct({product_id}, {quantity}) failed: {e.code()}") from e

        return {
            "success":         resp.success,
            "remaining_stock": resp.remaining_stock,
            "message":         resp.message,
        }