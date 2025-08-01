from urllib.parse import parse_qsl

from django.db import close_old_connections
from django.core.cache import cache
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from channels.exceptions import DenyConnection


class ChannelsJWTAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def auth(self, query_string):
        query_params = dict(parse_qsl(query_string))
        ticket = query_params.get('ticket')
        key = f'websocket:ticket:{ticket}'
        user_id = cache.get(key)
        if user_id is None:
            raise DenyConnection("Invalid ticket.")
        cache.delete(key)
        User = get_user_model()
        try:
            return await self.get_user(user_id)
        except User.DoesNotExist:
            raise DenyConnection("Invalid ticket.")

    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = scope['query_string'].decode('utf-8')
        try:
            scope['user'] = await self.auth(query_string)
        except DenyConnection as e:
            await send({
                'type': 'websocket.close',
                'code': 4001,
                'reason': str(e),
            })
            return
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        return User.objects.get(id=user_id)


def ChannelsJWTAuthMiddlewareStack(inner):
    return ChannelsJWTAuthMiddleware(AuthMiddlewareStack(inner))
