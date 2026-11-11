# order/grpc/client.py
import grpc
import uuid
from typing import Optional, Iterable
from django.conf import settings

# ✅ Updated imports based on your new generated code
from .inventory_pb2 import (
    GetProductStockByIdRequest,
    ReserveProductRequest,
    ReserveOrderRequest,
    ReserveOrderItem,
    UpdateProductQuantityRequest,
    CreateProductStorageRequest,
)
from .inventory_pb2_grpc import InventoryServiceStub


class InventoryServiceError(Exception):
    """Raised when the inventory service is unreachable or returns an error."""
    def __init__(self, message: str, code: grpc.StatusCode | None = None, details: str = ""):
        super().__init__(message)
        self.code = code
        self.details = details

class InventoryUnavailableError(InventoryServiceError):
    """Service unreachable / timed out — safe to retry or surface as 503."""
class InventoryClientError(InventoryServiceError):
    """Server rejected the request (NOT_FOUND, INVALID_ARGUMENT, …) — do not retry."""
class InventoryServerError(InventoryServiceError):
    """Server-side failure (INTERNAL, UNKNOWN) — likely a bug, do not retry."""

# Codes that mean "try again later"
_RETRYABLE = {
    grpc.StatusCode.UNAVAILABLE,
    grpc.StatusCode.DEADLINE_EXCEEDED
}
# Codes that mean "the server understood but rejected the request"
_CLIENT = {
    grpc.StatusCode.NOT_FOUND,
    grpc.StatusCode.INVALID_ARGUMENT,
    grpc.StatusCode.PERMISSION_DENIED,
    grpc.StatusCode.UNAUTHENTICATED,
    grpc.StatusCode.FAILED_PRECONDITION,
    grpc.StatusCode.RESOURCE_EXHAUSTED,  # arguably retryable; see note below
}


def _raise_for_rpc(e: grpc.RpcError, op: str) -> None:
    code = e.code()
    msg = f"{op} failed: {code}"
    if code in _RETRYABLE:
        raise InventoryUnavailableError(msg, code=code, details=e.details()) from e
    if code in _CLIENT:
        raise InventoryClientError(msg, code=code, details=e.details()) from e
    raise InventoryServerError(msg, code=code, details=e.details()) from e


class InventoryClient:
    def __init__(self, host: Optional[str] = None, timeout: float = 3.0):
        self.host    = host or settings.INVENTORY_GRPC_HOST
        self.timeout = timeout

    def _stub(self, channel):
        return InventoryServiceStub(channel)

    # ─── read ────────────────────────────────────────────────────
    def get_product_stock(self, product_id: int, user_id: int) -> Optional[int]:
        """
        Replaces the old get_product() and get_stock().
        Returns the stock quantity, or None if the product doesn't exist.
        """
        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).GetProductStockById(
                    GetProductStockByIdRequest(user_id=user_id, product_id=product_id),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            _raise_for_rpc(e, f"GetProductStockById({product_id})")

        return resp.stock

    # ─── write ───────────────────────────────────────────────────
    def reserve_product(self, product_id: int, quantity: int, user_id: int, idempotency_key: str = None) -> dict:
        if quantity < 1:
            raise ValueError("quantity must be >= 1")

        # Generate an idempotency key if not provided
        idem_key = idempotency_key or str(uuid.uuid4())

        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).ReserveProduct(
                    ReserveProductRequest(
                        user_id=user_id,
                        product_id=product_id,
                        quantity=quantity,
                        idempotency_key=idem_key
                    ),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            _raise_for_rpc(e, f"ReserveProduct({product_id}, {quantity})")

        return {
            "success": resp.success,
            "remaining_stock": resp.remaining_stock,
            "message": resp.msg, # Changed from 'message' to 'msg' in proto
        }

    def reserve_order(self, items: Iterable[tuple[int, int]], user_id: int, idempotency_key: str = None) -> dict:
        items = list(items)
        if not items:
            raise ValueError("items must not be empty")
        for pid, qty in items:
            if qty < 1:
                raise ValueError(f"quantity for product {pid} must be >= 1")

        idem_key = idempotency_key or str(uuid.uuid4())

        # ✅ Build ReserveOrderItem objects instead of ReserveProductRequest
        order_items = [
            ReserveOrderItem(product_id=pid, quantity=qty)
            for pid, qty in items
        ]

        request = ReserveOrderRequest(
            user_id=user_id,
            products=order_items,
            idempotency_key=idem_key
        )

        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).ReserveOrder(
                    request, timeout=self.timeout
                )
        except grpc.RpcError as e:
            _raise_for_rpc(e, f"ReserveOrder")

        # ✅ Capture failed_product_ids and msg from the new response
        return {
            "success": resp.success,
            "message": resp.msg,
            "failed_product_ids": list(resp.failed_product_ids)
        }

    # ✅ Renamed from add_product_quantity to update_product_quantity
    def update_product_quantity(self, product_id: int, amount: int, user_id: int, idempotency_key: str = None) -> dict:
        """
        Adjust stock for a product (e.g. release reserved stock).
        Note: 'amount' can be positive or negative depending on the operation.
        """
        idem_key = idempotency_key or str(uuid.uuid4())

        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).UpdateProductQuantity(
                    UpdateProductQuantityRequest(
                        user_id=user_id,
                        product_id=product_id,
                        amount=amount,
                        idempotency_key=idem_key
                    ),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            _raise_for_rpc(e, f"UpdateProductQuantity({product_id}, {amount})")

        return {
            "success": resp.success,
            "message": resp.msg
        }

    def create_product_storage(self, product_id: int, stock: int, user_id: int, idempotency_key: str = None) -> dict:
        """
        Adjust stock for a product (e.g. release reserved stock).
        Note: 'amount' can be positive or negative depending on the operation.
        """
        idem_key = idempotency_key or str(uuid.uuid4())

        try:
            with grpc.insecure_channel(self.host) as channel:
                resp = self._stub(channel).UpdateProductQuantity(
                    CreateProductStorageRequest(
                        user_id=user_id,
                        product_id=product_id,
                        stock=stock,
                        idempotency_key=idem_key
                    ),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            _raise_for_rpc(e, f"CreateProductStorageRequest({product_id}, {stock})")

        return {
            "product_id": resp.product_id,
            "stock": resp.stock
        }













