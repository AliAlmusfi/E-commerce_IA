
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order
from tools.caching import invalidate_cache

@receiver([post_save, post_delete], sender=Order)
def invalidate_order_cache(sender, instance, **kwargs):
    invalidate_cache('order', sender, instance, **kwargs)


