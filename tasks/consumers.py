import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
    
        if self.user == AnonymousUser or not self.user.company:
            await self.close()
            return
        
        self.company_group_name = f"company_{self.user.company.id}"
        
        await self.channel_layer.group_add(
            self.company_group_name,
            self.channel_name
        )
        
        await self.accept()
  
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to {self.user.company.name} task updates'
        }))

    async def disconnect(self, close_code):
    
        if hasattr(self, 'company_group_name'):
            await self.channel_layer.group_discard(
                self.company_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection alive'
                }))
        except json.JSONDecodeError:
            pass

    async def task_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_created',
            'task': event['task'],
            'message': f"New task created: {event['task']['title']}"
        }))


    async def task_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'task': event['task'],
            'message': f"Task updated: {event['task']['title']}"
        }))

    @database_sync_to_async
    def get_user_company(self, user):
        return user.company if hasattr(user, 'company') else None
