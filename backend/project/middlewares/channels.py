from urllib.parse import parse_qsl

from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.core.cache import cache
from channels.middleware import BaseMiddleware
from channels.exceptions import DenyConnection


class ChannelsJWTAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def auth(self, query_string):
        query_params = dict(parse_qsl(query_string))
        ticket = query_params.get('ticket')
        key = f'websocket:ticket:{ticket}'
        user_data = await sync_to_async(cache.get)(key)
        if user_data is None:
            raise DenyConnection("Invalid ticket.")
        await sync_to_async(cache.delete)(key)
        return user_data

    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_string = scope['query_string'].decode('utf-8')
        try:
            scope['user_data'] = await self.auth(query_string)
        except DenyConnection as e:
            await send({
                'type': 'websocket.close',
                'code': 4001,
                'reason': str(e),
            })
            return
        return await super().__call__(scope, receive, send)


def ChannelsJWTAuthMiddlewareStack(inner):
    return ChannelsJWTAuthMiddleware(inner)
