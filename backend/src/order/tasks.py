from celery import shared_task
from django.core.mail import send_mail
import logging
from .models import Order

from tools.error_handler.exceptions import BusinessRuleViolation , InventoryServiceError

from tools.db.db_router import WRITE_DB
logger = logging.getLogger(__name__)

@shared_task(bind=True , max_retries=3 , default_retry_delay=10)
def send_order_email(self, user_email: str, order_ref: str, event: str, error_message: str = ''):
    from django.conf import settings
    try:
        if event == 'confirmed':
            subject = 'Order Confirmed'
            body    = f'Your order #{order_ref} has been placed and is pending approval.'
        elif event == 'failed':
            subject = 'Order Failed'
            body    = f'Sorry, your order #{order_ref} failed. Reason: {error_message}'
        else:
            raise ValueError(f"Unknown event type: {event!r}")
        print("//////////////////////////////////////////////////////////////////////")
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        print(settings.DEFAULT_FROM_EMAIL)
        print("//////////////////////////////////////////////////////////////////////")
        logger.info("Email %r sent to %s (order %s)", event, user_email, order_ref)
    except Exception as exc:
        logger.exception("Email send failed: %s", exc)
        raise self.retry(exc=exc)



# def process_order_async(self, created_at ,user_email):

#     # try:
#     #     order = Order.objects.db_manager(WRITE_DB).get(id=order_id)
#     # except Order.DoesNotExist:
#     #     logger.error(f"Order {order_id} not found in database.")
#     #     return

#     try:

#         # process_order_logic(order, items_data, user_id)
        

#         # order.status = Order.Status.PENDING
#         # order.save(update_fields=['status'], using=WRITE_DB)


#         from django.conf import settings

#         send_mail(
#             'Order Confirmed',
#             f'Your order #{created_at} has been placed and is pending approval.',
#             # 'cycle@e-commerce.com',
#             settings.DEFAULT_FROM_EMAIL,
#             [user_email],
#             fail_silently=False,
#         )
#         # send_mail()
#         logger.info(f"Order {created_at} successfully processed.")

#     except (BusinessRuleViolation, InventoryServiceError) as exc:
    
#         logger.warning(f"Order {created_at} failed business rules: {exc.message}")

#         from django.conf import settings
        
#         # order.status = Order.Status.FAILED
#         # order.error_message = exc.message
#         # order.save(update_fields=['status', 'error_message'], using=WRITE_DB)

#         send_mail(
#             'Order Failed',
#             f'Sorry, your order #{created_at} failed. Reason: {exc.message}',
#             # 'cycle@e-commerce.com',
#             settings.DEFAULT_FROM_EMAIL,
#             [user_email],
#             fail_silently=False,
#         )

#     except Exception as exc:
#         # Infrastructure error (e.g., RabbitMQ or gRPC network crash) -> RETRY
#         logger.error(f"System error processing order {created_at}: {exc}")
#         raise self.retry(exc=exc)
