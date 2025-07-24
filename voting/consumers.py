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
        self.group_name = 'match_status_all'  # fixed group name for all clients

        # Join common group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def match_status_update(self, event):
        # Send a simple notification about match update to clients
        await self.send(text_data=json.dumps({
            "type": "match_status_update",
            "message": "Match data updated, please refresh or fetch latest data.",
            # optionally, send some minimal data like updated match id(s)
            "updated_match_id": event.get("match_id", None),
        }))
