from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Without base path for local development
    re_path(r'ws/game/(?P<room_name>[\w-]+)/$', consumers.GameConsumer.as_asgi()),
    # With base path for production (ingress)
    re_path(r'copilot/memory-game/ws/game/(?P<room_name>[\w-]+)/$', consumers.GameConsumer.as_asgi()),
]
