from django.db import models
from tools.models import TimeStampedModel
from e_commerce import settings
# Create your models here.



class Orders (TimeStampedModel):
    class Meta:
        db_table = 'order'

    total  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # product_quantity = models.IntegerField(null=False, blank=False)

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETE = "complete", "Complete"
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        null=False,
        blank=False
    )

    user_id = models.PositiveBigIntegerField(db_index=True)
    
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.PROTECT,   
    #     related_name='orders',
    # )



class OrderItems(TimeStampedModel):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="items")
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

