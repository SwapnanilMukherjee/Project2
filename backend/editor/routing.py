# backend/editor/routing.py
from django.urls import re_path
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import DocumentConsumer

websocket_urlpatterns = [
    re_path(r'ws/document/(?P<document_id>[^/]+)/$', DocumentConsumer.as_asgi()),
]

application = AuthMiddlewareStack(
    URLRouter(websocket_urlpatterns)
)