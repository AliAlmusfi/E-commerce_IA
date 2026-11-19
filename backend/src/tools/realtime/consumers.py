from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from order.public import check_user_order_exists


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            # await self.accept()
            await self.close(code=4001) # 4001 = Unauthorized
            return

        # Customer connects to their personal order channel
        self.order_id = self.scope['url_route']['kwargs']['order_id']

        # Security check: Does this order belong to this user?
        is_owner = await self.check_order_owner(self.order_id, self.user.id)
        if not is_owner:
            # await self.accept()
            await self.close(code=4003) # 4003 = Forbidden (ليس مالك الطلب)
            return
            
        
        self.room_group_name = f'order_{self.order_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from room group
    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'message': event['message']
        }))

    @database_sync_to_async
    def check_order_owner(self, order_id, user_id):
        return check_user_order_exists(order_id=order_id , user_id=user_id)
        return Order.objects.filter(id=order_id, user_id=user_id).exists()


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # Security check: Only staff/admin can access the dashboard
        if not self.user.is_authenticated or not self.user.is_staff:
            await self.close()
            return

        self.room_group_name = 'dashboard'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            'order_id': event['order_id'],
            'user_email': event['user_email'],
            'total': event['total'],
        }))
    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'order_id': event['order_id'],
            'status': event['status'],
            'message': event['message']
        }))