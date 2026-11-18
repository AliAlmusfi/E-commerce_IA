
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order
from tools.caching import invalidate_cache

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from user.public import get_users_map


@receiver([post_save, post_delete], sender=Order)
def invalidate_order_cache(sender, instance, **kwargs):
    invalidate_cache('order', sender, instance, **kwargs)


@receiver(post_save , sender=Order)
def order_status_changed(sender , instance , created , **kwargs):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f'order_{instance.id}',
        {
            'type': 'order_update', # Matches the method in OrderStatusConsumer
            'status': instance.status,
            'message': f"Order status is now {instance.get_status_display()}"
        }
    )


@receiver(post_save, sender=Order)
def created_order(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    user_map = get_users_map([instance.user_id])
    user = user_map.get(instance.user_id)
    email = user.email if user is not None else ''

    async_to_sync(channel_layer.group_send)(
        'dashboard',
        {
            'type': 'new_order',
            'order_id': instance.id,
            'user_email': email,
            'total': str(instance.total) if instance.total else '0.00',
        },
    )