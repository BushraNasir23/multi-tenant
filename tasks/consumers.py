import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Try to authenticate user from JWT token
        self.user = await self.authenticate_user()
        
        if self.user.is_anonymous or not hasattr(self.user, 'company') or not self.user.company:
            await self.close(code=4001)  # Unauthorized
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

    async def authenticate_user(self):
        """Authenticate user from JWT token in headers or query params"""
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        User = get_user_model()
        token = None
        
        # Try to get token from headers
        headers = dict(self.scope.get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode()
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # If no token in headers, try query parameters
        if not token:
            query_string = self.scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            if 'token' in query_params:
                token = query_params['token'][0]
        
        # Authenticate with token
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await self.get_user(user_id)
                return user
            except (InvalidToken, TokenError, KeyError):
                pass
        
        return AnonymousUser()
    
    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import AnonymousUser
        
        User = get_user_model()
        try:
            return User.objects.select_related('company').get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

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
