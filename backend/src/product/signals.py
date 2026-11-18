
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from tools.caching import invalidate_cache

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    invalidate_cache('product', sender, instance, **kwargs)


