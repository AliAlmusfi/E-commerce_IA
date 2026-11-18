from .models import Order , OrderItem
from tools.grpc.client import InventoryClient
from django.core.exceptions import ValidationError , PermissionDenied
from django.db import transaction
from decimal import Decimal
from product.public import get_products_map
from tools.error_handler.exceptions import BusinessRuleViolation , InventoryServiceError
# from .tasks import send_order_confirmation_email
from user.public import get_users_map
# from .tasks import process_order_async



def initiate_order_processing(user_id: int, user_email: str, items_data: list[dict]) -> Order:
    
    from .tasks import process_order_async
    # 1. Create the shell order
    order = Order.objects.create(
        user_id=user_id, 
        status=Order.Status.PROCESSING
    )


    transaction.on_commit(
        lambda: process_order_async.delay(
            order_id=order.id,
            items_data=items_data,
            user_id=user_id,
            user_email=user_email
        )
    )

    return order


def process_order_logic(order: Order, items_data: list[dict] , user_id: int) -> Order:

    client = InventoryClient()
    products = {}
    try:
            
        for item in items_data:
            pid = item['product_id']
            stock = client.get_product_stock(pid, user_id)
            product_public = get_products_map([pid])
            
            if stock is None:
                raise BusinessRuleViolation(f"Product {pid} does not exist.")
            if stock < item['quantity']:
                title = getattr(product_public, 'title', pid) 
                raise BusinessRuleViolation(f"Product '{title}' has only {stock} in stock.")
            products[pid] = stock

        result = client.reserve_order(
            items=[(item['product_id'], item['quantity']) for item in items_data],
            user_id=user_id
        )

    except InventoryServiceError :
        # print("//////////////////////////////////////////////////////////////////////")
        # print(order.id)
        # print("//////////////////////////////////////////////////////////////////////")
        # Order.objects.filter(id=order.id).delete()
        # order.delete()
        _release_reserved(client , items_data , user_id)
        raise 
    except Exception:
        raise
    # if not result['success']:
    #     _raise_reservation_failure(client, items_data, products, user_id)

    try:
        with transaction.atomic():
            total = Decimal("0.00")
            for item in items_data:
                pid = item["product_id"]
                product_public = get_products_map([pid])
                unit_price = product_public.get(pid).price
                qty = item["quantity"]
                
                OrderItem.objects.create(
                    order=order,
                    product_id=pid,
                    quantity=qty,
                    unit_price=unit_price,
                )
                total += unit_price * qty

            order.total = total
            order.save(update_fields=["total"]) 
            
    except Exception:
        _release_reserved(client, items_data, user_id)
        raise   


# def _raise_reservation_failure(client, items_data, products , user):
#     for item in items_data:
#         pid = item["product_id"]
#         product_public = get_products_map([pid])
#         current = client.get_product_stock(pid , user.id)
#         if current is None:
#             raise BusinessRuleViolation( f"Product {pid} is no longer available.")
#         if current < item["quantity"]:
#             #TODO get the title
#             title = getattr(get_products_map([pid]), 'title', pid)
#             raise BusinessRuleViolation(f"Product '{title}' has only {current} in stock.")
#     raise BusinessRuleViolation("Could not reserve stock. Please try again.")


def _release_reserved(client, items_data , user_id:int):

    import logging
    log = logging.getLogger(__name__)

    for item in items_data:
        pid, qty = item["product_id"], item["quantity"]
        try:
            result = client.update_product_quantity(pid, amount=qty , user_id=user_id)
            if not result["success"]:
                log.error("Failed to release stock: product=%s qty=%s", pid, qty)
        except Exception as e:
            log.error("Exception releasing stock: product=%s qty=%s err=%s", pid, qty, e)



def update_order_status(user , order:Order , new_status: str) ->Order:
    if not user.is_staff: 
        raise PermissionDenied(
            {"detail": "Only staff can change order status "},
        )

    ALLOWED_TRANSITIONS = {
        Order.Status.PENDING:  {Order.Status.COMPLETE},
        Order.Status.COMPLETE: set(),    # terminal
    }

    current_status = order.status
    if new_status == current_status:
        raise ValidationError({
            "status": f"Order is already in status '{current_status}'."
        })
    allowed = ALLOWED_TRANSITIONS.get(current_status , set())
    if new_status not in allowed:
        pretty = ", ".join(s.value for s in allowed) or "none (terminal state)"
        raise ValidationError({
            "status": f"Cannot transition from '{current_status}' to '{new_status}'. Allowed next: {pretty}."
        })

    order.status = new_status
    order.save(update_fields=['status'])
    return order