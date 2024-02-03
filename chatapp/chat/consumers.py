import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # gets the 'room_name' parameter from URL route in chat/routing.py
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # construct channel group name directly from user-specified room name
        self.room_group_name = "chat_%s" % self.room_name

        # join room group
        # async to sync wrapper is required because ChatConsumer is a sync. WebSocket, but channel layer is async
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # accept WebSocket connection
        # if we don't call accept() within connect(), connection will be rejected and closed
        # accept() is recommended to be the last action
        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # send message (event) to room group
        # event has a special type key corresponding to the name of the method that should be invoked
        # on consumers that receive the event
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat_message", "message": message})

    # receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({'message': message}))
