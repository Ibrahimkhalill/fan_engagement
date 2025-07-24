# your_app_name/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .utils import get_vote_stats  # Import the utility function

class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'vote_{self.match_id}'

        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send initial vote stats
        await self.send_initial_stats()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_initial_stats(self):
        stats = await sync_to_async(get_vote_stats)(self.match_id)
        await self.send(text_data=json.dumps(stats))

    async def receive(self, text_data):
        # Handle incoming messages if needed
        pass

    async def vote_update(self, event):
        # Send updated vote stats to WebSocket clients
        await self.send(text_data=json.dumps(event['stats']))
        
        
class MatchStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'match_status_{self.match_id}'

        # Join match status group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the match status group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def match_status_update(self, event):
        # Send updated match status to WebSocket clients
        await self.send(text_data=json.dumps({
            "type": "match_status_update",
            "data": event["data"]
        }))
