from django.db import models
from tools.models import TimeStampedModel



# Create your models here.

class Product(TimeStampedModel):
    class Meta:
        db_table = 'product'

    title = models.CharField(max_length=20 , null= False , blank=False)
    manufacture = models.CharField(max_length=20 , null= False , blank=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0 , blank=True)
    description = models.CharField(max_length=100)
    stock = models.IntegerField()




