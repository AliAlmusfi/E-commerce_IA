from rest_framework import serializers
from .models import Device



class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['registration_id', 'device_type']
        extra_kwargs = {
            'registration_id': {'required': True},
            'device_type': {'required': False}
        }

        