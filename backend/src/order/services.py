from .models import Order , OrderItem
from tools.grpc.client import InventoryClient
from django.core.exceptions import ValidationError , PermissionDenied
from django.db import transaction
from decimal import Decimal



def create_order(user, items_data: list[dict]) -> Order:

    client = InventoryClient()
    products = {}
    for item in items_data:
        pid = item['product_id']
        product = client.get_product_stock(pid , user.id)
        if product is None :
            raise ValidationError(
                {"detail": f"Product {pid} does not exist."}
            )
        if product['stock'] < item['quantity']:
            #TODO after doing the public.py add it to the product , just get the product info from it like the title
            raise ValidationError(
                {"detail":  f"Product has only {product['stock']} in the stock"}
            )
        products[pid] = product


    result = client.reserve_order(
        item=[(item['product_id'] , item['quantity']) for item in items_data],
        user_id=user.id
    )

    if not result['success']:
        _raise_reservation_failure(client, items_data, products , user)

    try:
        with transaction.atomic():
            order = Order.objects.create(user_id = user.id)
            total = Decimal("0.00")

            for item in items_data:
                pid = products["product_id"]
        #TODO   unit_price =  add this from the public.py from the product 
                qty = item["quantity"]
                OrderItem.objects.create(
                    order=order,
                    product_id=item["product_id"],
                    # product_title=product["title"],             # snapshot
                    # product_manufacturer=product["manufacturer"],
                    # product_image=product["image"],
                    quantity=qty,
                    #TODO unit_price=unit_price,
                )
                #TODO total += unit_price * qty

            order.total = total
            order.save(update_fields=["total"]) 

            return order
    except Exception:
        
        _release_reserved(client, items_data , user)
        raise   


def _raise_reservation_failure(client, items_data, products , user):
    for item in items_data:
        pid = item["product_id"]
        current = client.get_product_stock(pid , user.id)
        if current is None:
            raise ValidationError({"detail": f"Product {pid} is no longer available."})
        if current < item["quantity"]:
            #TODO get the title
            raise ValidationError({
                "detail": f"Product '{products[pid]}' has only {current} in stock."
            })
    raise ValidationError({
        "detail": "Could not reserve stock (a concurrent order may have taken it). Please try again."
    })


def _release_reserved(client, items_data , user):

    import logging
    log = logging.getLogger(__name__)

    for item in items_data:
        pid, qty = item["product_id"], item["quantity"]
        try:
            result = client.update_product_quantity(pid, amount=qty , user_id=user.id)
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