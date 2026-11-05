from django.db import models
from tools.models import TimeStampedModel



# Create your models here.
def product_image_upload_path(instance , filename):
    if not instance.id:
        # Handle case where instance isn't saved yet
        return f'products/temp/{filename}'
    return f'products/{instance.id}/{filename}'
class Product(TimeStampedModel):
    class Meta:
        db_table = 'product'

    title = models.CharField(max_length=20 , null= False , blank=False)
    manufacture = models.CharField(max_length=20 , null= False , blank=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0 , blank=True)
    description = models.CharField(max_length=100)
    stock = models.IntegerField()
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_image_upload_path,
        # default="defaults/products/default.png"
    )




