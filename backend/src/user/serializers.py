from rest_framework import serializers
from django.db import transaction


from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = [
            'id',
            'username',
            'email',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'id': {'read_only': True}, 
        }



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    

    class Meta:
        model = User
        fields = ['username', 'email' , 'password']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        try:
            if not attrs['password']:  # Check for empty string/None
                raise serializers.ValidationError({
                    'password': 'This field may not be blank (empty).'
                })
        except KeyError:
            raise serializers.ValidationError({
                'password': 'This field is required.'
            })
        
        attrs = super().validate(attrs) 

        if len(attrs['password']) < 8:
            raise serializers.ValidationError({'password': 'must be 8 characters or more'})

        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username = validated_data['username'],
                    email = validated_data['email'],
                    password = validated_data['password'],
                )

            return user
        except KeyError as e:
            raise serializers.ValidationError(f'{str(e)}: this field is required !')
    

