from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'manufacture',
            'price',
            'stock',
        ]
        extra_kwargs = {
            'id': {'read_only': True}, 
        }

