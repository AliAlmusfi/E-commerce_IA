from dataclasses import dataclass
from decimal import Decimal

from .models import Order
from tools.db.db_router import WRITE_DB


@dataclass(frozen=True)
class OrderDTO:
    id: int
    total: Decimal
    user_id: int
    status: Order.Status            # or str, if you convert with .value
    error_message: str | None       # None when no error

    @classmethod
    def from_model(cls, o: Order) -> "OrderDTO":
        return cls(
            id=o.id,
            total=o.total,
            user_id=o.user_id,
            status=o.status,
            error_message=o.error_message,
        )


def get_orders_map(order_ids: list[int] ) -> dict[int, OrderDTO]:
    orders = Order.objects.using(WRITE_DB).filter(id__in=order_ids)
    return {o.id: OrderDTO.from_model(o) for o in orders}


def check_user_order_exists(order_id: int , user_id: int ) -> bool:
    order = Order.objects.using(WRITE_DB).filter(id=order_id , user_id = user_id)
    return order.exists()