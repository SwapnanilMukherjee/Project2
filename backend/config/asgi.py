# backend/config/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from editor.routing import websocket_urlpatterns
from editor.middleware import WebSocketAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Get ASGI application for HTTP requests
django_asgi_app = get_asgi_application()

# Configure the ASGI application
application = ProtocolTypeRouter({
    # Handle regular HTTP requests
    "http": django_asgi_app,
    
    # Handle WebSocket requests
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            WebSocketAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})

# Middleware configuration for different protocols
http_middleware = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "editor.middleware.error_handling.ErrorHandlingMiddleware",
]

websocket_middleware = [
    "channels.middleware.BaseMiddleware",
    "channels.sessions.SessionMiddleware",
    "channels.auth.AuthMiddleware",
    "editor.middleware.WebSocketAuthMiddleware",
]

# ASGI application settings
ASGI_APPLICATION = "config.asgi.application"

# Channel layer configuration (already in settings.py)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_HOST', 'localhost'), 
                      int(os.getenv('REDIS_PORT', 6379)))],
        },
    },
}

# WebSocket specific settings
WEBSOCKET_MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB
WEBSOCKET_ACCEPT_ALL = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Configure CORS for WebSocket
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
if os.getenv('DJANGO_DEBUG', 'True') == 'True':
    CORS_ALLOW_ALL_ORIGINS = True

# Configure channel layers for different environments
if os.getenv('DJANGO_DEBUG', 'True') == 'True':
    # Use in-memory channel layer for development
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    # Use Redis channel layer for production
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(os.getenv('REDIS_HOST', 'localhost'), 
                          int(os.getenv('REDIS_PORT', 6379)))],
                "capacity": 1500,  # Maximum number of messages to hold
                "expiry": 10,      # Message expiry time in seconds
            },
        },
    }

# Optional: Configure channel name generators
from channels.layers import BaseChannelLayer
BaseChannelLayer.channel_name_generator = lambda self: f"channel_{os.urandom(8).hex()}"

# Optional: Configure group name validators
from channels.layers import BaseChannelLayer
def validate_group_name(name):
    """Custom group name validator"""
    if not isinstance(name, str):
        raise TypeError("Group name must be a string")
    if len(name) > 100:
        raise ValueError("Group name too long (>100 characters)")
    if not name.replace("_", "").isalnum():
        raise ValueError("Group name must be alphanumeric plus underscores")
    return name

BaseChannelLayer.valid_group_name = staticmethod(validate_group_name)

# Optional: Error handlers for different protocols
async def http_error_handler(scope, receive, send):
    """Handle HTTP errors"""
    await send({
        "type": "http.response.start",
        "status": 500,
        "headers": [
            [b"content-type", b"application/json"],
        ],
    })
    await send({
        "type": "http.response.body",
        "body": b'{"error": "Internal server error"}',
    })

async def websocket_error_handler(scope, receive, send):
    """Handle WebSocket errors"""
    await send({
        "type": "websocket.close",
        "code": 1011,  # Internal error
    })

ERROR_HANDLERS = {
    "http": http_error_handler,
    "websocket": websocket_error_handler,
}