from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.decorators import action



from .signals import send_welcome_notification
from .models import Device
from .serializer import DeviceSerializer

from user.models import User

from drf_spectacular.utils import extend_schema


class NotificationViewSet (viewsets.ModelViewSet):
    queryset = Device.objects.all()
    permission_classes = [AllowAny]


    @extend_schema(
        summary="Register Device",
        operation_id="register_device",
        description="Register the device to send notification to the device",
        tags=["User/Device"]
    )
    @action(detail=False , methods=['post'] , serializer_class=DeviceSerializer)
    def register_device(self, request):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            device, created = Device.objects.update_or_create(
                user=request.user,
                registration_id=serializer.validated_data['registration_id'],
                defaults={
                    'device_type': serializer.validated_data.get('device_type'),
                    'active': True
                }
            )
            send_welcome_notification(User , request.user , True)
            return Response(DeviceSerializer(device).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

