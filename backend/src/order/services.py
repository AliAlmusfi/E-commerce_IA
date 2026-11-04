# orders/services/product_client.py
import grpc
from django.conf import settings
from typing import List, Dict

# These are generated from your .proto — see setup section below
from orders.grpc.product_pb2       import ProductRequest, ProductsRequest, ProductResponse
from orders.grpc.product_pb2_grpc  import ProductServiceStub


class ProductServiceError(Exception):
    """Raised when the product service is unavailable or returns an error."""


class ProductClient:
    """
    Thin wrapper around the Flask product service (gRPC).

    All methods return plain dicts so the rest of the Django code never
    imports gRPC classes directly. This makes testing trivial: mock this class.
    """

    def __init__(self, host: str = None, timeout: float = 3.0):
        self.host    = host or settings.PRODUCT_SERVICE_GRPC_HOST
        self.timeout = timeout

    # ── single product ────────────────────────────────────────
    def get_product(self, product_id: int) -> Dict | None:
        try:
            with grpc.insecure_channel(self.host) as channel:
                stub = ProductServiceStub(channel)
                resp: ProductResponse = stub.GetProduct(
                    ProductRequest(id=product_id),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            raise ProductServiceError(f"gRPC GetProduct failed: {e.code()} — {e.details()}") from e

        if not resp.found:
            return None

        return {
            "id":       resp.id,
            "name":     resp.name,
            "price":    resp.price,           # string like "9.99" → parse to Decimal
            "is_active": resp.is_active,
        }

    # ── batch (preferred) ─────────────────────────────────────
    def get_products(self, product_ids: List[int]) -> Dict[int, Dict]:
        """Fetch many products in one round trip. Returns {id: product_dict}."""
        if not product_ids:
            return {}

        try:
            with grpc.insecure_channel(self.host) as channel:
                stub = ProductServiceStub(channel)
                resp = stub.GetProducts(
                    ProductsRequest(ids=product_ids),
                    timeout=self.timeout,
                )
        except grpc.RpcError as e:
            raise ProductServiceError(f"gRPC GetProducts failed: {e.code()} — {e.details()}") from e

        return {
            p.id: {
                "id":        p.id,
                "name":      p.name,
                "price":     p.price,
                "is_active": p.is_active,
            }
            for p in resp.products
        }