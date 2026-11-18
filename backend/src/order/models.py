from django.db import models
from tools.models import TimeStampedModel
from e_commerce import settings
# Create your models here.



class Order (TimeStampedModel):
    class Meta:
        db_table = 'orders'
        ordering = ['id']

    total  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # product_quantity = models.IntegerField(null=False, blank=False)

    class Status(models.TextChoices):
        PROCESSING = "processing" , "Processing"
        PENDING = "pending", "Pending"
        COMPLETE = "complete", "Complete"
        FAILED = "failed" , "Failed"
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
        null=False,
        blank=False
    )

    error_message = models.CharField(max_length=255 , blank=True , null=True)
    user_id = models.PositiveBigIntegerField(db_index=True)
    
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.PROTECT,   
    #     related_name='orders',
    # )



class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.PositiveBigIntegerField(db_index=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
        constraints = [
            models.UniqueConstraint(fields=["order", "product_id"], name="unique_product_per_order"),
        ]


# class Product(TimeStampedModel):
#     title = models.CharField(max_length=20 , null= False , blank=False)
#     manufacture = models.CharField(max_length=20 , null= False , blank=False)
#     price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     description = models.CharField(max_length=100)

