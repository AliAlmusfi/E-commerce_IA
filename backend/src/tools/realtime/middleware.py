from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs



@database_sync_to_async
def get_user(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return get_user_model().objects.get(id=user_id)
    except Exception:
        raise AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]
        
        if token:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)