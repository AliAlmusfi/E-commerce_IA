from rest_framework import serializers
from django.db import transaction


from .models import Users

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users 
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

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users 
        fields = [
            'id',
            'username',
            'email',
            'is_staff',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'id': {'read_only': True}, 
        }



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    

    class Meta:
        model = Users
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



