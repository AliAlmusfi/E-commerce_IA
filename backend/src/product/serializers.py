from rest_framework import serializers
from .models import Product
from .services import get_stock

class ProductSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(required=True, write_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'manufacturer',
            'price',
            'stock',
            'image',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'title': {'required': True},
            'manufacturer': {'required': True},
            'price': {'required': True}
        }

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Product Price must be Positive..."
            )

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['stock'] = self._get_stock(instance)
        return data

    def _get_stock(self, instance):
        return get_stock(
            id=instance.id,
            user_id=self.context['request'].user.id
        )
    
class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'manufacturer',
            'price',
            'image',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'title': {'required': False},
            'description': {'required': False},
            'manufacturer': {'required': False},
            'price': {'required': False},
            'image': {'required': False},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if ( 
            (not attrs.get('title')) and (not attrs.get('description'))
            and (not attrs.get('manufacturer')) and (not attrs.get('price'))
            and (not attrs.get('image'))
        ):
            raise serializers.ValidationError(
                "request does not contain any valid data to update on product ! no (title, manufacturer, description, price, image) found !"
            )
        return attrs


class ProductStockSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True, min_value=1)
    # class Meta:
    #     fields = ['amount']
    #     extra_kwargs = {
    #         'amount': {'required': True},
    #     }