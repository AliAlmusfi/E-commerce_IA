from celery import shared_task
from django.core.mail import send_mail
import logging
from .models import Order
from .services import process_order_logic
from tools.error_handler.exceptions import BusinessRuleViolation , InventoryServiceError

logger = logging.getLogger(__name__)

@shared_task(bind=True , max_retries=3 , default_retry_delay=10)
def process_order_async(self, order_id, items_data, user_id ,user_email):
    # print("//////////////////////////////////////////////////////////////////////")
    # print(user_email)
    # print("//////////////////////////////////////////////////////////////////////")
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found in database.")
        return

    try:

        process_order_logic(order, items_data, user_id)
        

        order.status = Order.Status.PENDING
        order.save(update_fields=['status'])


        from django.conf import settings

        send_mail(
            'Order Confirmed',
            f'Your order #{order.created_at} has been placed and is pending approval.',
            # 'cycle@e-commerce.com',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        # send_mail()
        logger.info(f"Order {order.id} successfully processed.")

    except (BusinessRuleViolation, InventoryServiceError) as exc:
    
        logger.warning(f"Order {order_id} failed business rules: {exc.message}")

        from django.conf import settings
        
        order.status = Order.Status.FAILED
        order.error_message = exc.message
        order.save(update_fields=['status', 'error_message'])

        send_mail(
            'Order Failed',
            f'Sorry, your order #{order.created_at} failed. Reason: {exc.message}',
            # 'cycle@e-commerce.com',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )

    except Exception as exc:
        # Infrastructure error (e.g., RabbitMQ or gRPC network crash) -> RETRY
        logger.error(f"System error processing order {order_id}: {exc}")
        raise self.retry(exc=exc)
