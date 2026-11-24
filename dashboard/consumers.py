import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AdminConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if not user.is_authenticated or user.role != "admin":
            await self.close()
            return

        self.group_name = "admin_orders"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def order_created(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_order",
            "order": event["order"],
        }))

    async def courier_location_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "courier_location",
            "location": event["location"],
        }))

    async def order_status_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "order_status",
            "order": event["order"],
        }))