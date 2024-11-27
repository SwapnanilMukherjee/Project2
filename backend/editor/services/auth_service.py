# backend/editor/services/auth_service.py
from typing import Optional, Tuple
import hashlib
import jwt
import datetime
from django.conf import settings
from django.core.cache import cache

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.token_expiry = datetime.timedelta(hours=24)

    def create_access_token(self, document_id: str, passkey: str) -> str:
        """Create JWT access token for document access"""
        hashed_passkey = self._hash_passkey(passkey)
        
        payload = {
            'document_id': str(document_id),
            'passkey_hash': hashed_passkey,
            'exp': datetime.datetime.utcnow() + self.token_expiry
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def validate_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Validate JWT token and return document_id if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return True, payload['document_id']
        except jwt.ExpiredSignatureError:
            return False, 'Token has expired'
        except jwt.InvalidTokenError:
            return False, 'Invalid token'

    def verify_passkey(self, document_passkey: str, provided_passkey: str) -> bool:
        """Verify if provided passkey matches document passkey"""
        hashed_provided = self._hash_passkey(provided_passkey)
        return document_passkey == hashed_provided

    def create_share_link(self, document_id: str, expiry_hours: int = 72) -> str:
        """Create temporary share link for document"""
        share_token = self._generate_share_token()
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
        
        # Store in cache with expiration
        cache_key = f'share_link:{share_token}'
        cache.set(
            cache_key,
            {
                'document_id': str(document_id),
                'expiry': expiry.timestamp()
            },
            timeout=expiry_hours * 3600
        )
        
        return share_token

    def validate_share_link(self, share_token: str) -> Tuple[bool, Optional[str]]:
        """Validate share link and return document_id if valid"""
        cache_key = f'share_link:{share_token}'
        share_data = cache.get(cache_key)
        
        if not share_data:
            return False, 'Invalid or expired share link'
            
        if datetime.datetime.utcnow().timestamp() > share_data['expiry']:
            cache.delete(cache_key)
            return False, 'Share link has expired'
            
        return True, share_data['document_id']

    def create_session_token(self, document_id: str) -> str:
        """Create WebSocket session token"""
        session_id = self._generate_session_id()
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        # Store session in cache
        cache_key = f'session:{session_id}'
        cache.set(
            cache_key,
            {
                'document_id': str(document_id),
                'created_at': datetime.datetime.utcnow().timestamp(),
                'expiry': expiry.timestamp()
            },
            timeout=24 * 3600
        )
        
        return session_id

    def validate_session(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate WebSocket session"""
        cache_key = f'session:{session_id}'
        session_data = cache.get(cache_key)
        
        if not session_data:
            return False, 'Invalid or expired session'
            
        if datetime.datetime.utcnow().timestamp() > session_data['expiry']:
            cache.delete(cache_key)
            return False, 'Session has expired'
            
        return True, session_data['document_id']

    def _hash_passkey(self, passkey: str) -> str:
        """Hash passkey using SHA-256"""
        return hashlib.sha256(
            passkey.encode() + settings.SECRET_KEY.encode()
        ).hexdigest()

    def _generate_share_token(self) -> str:
        """Generate random share token"""
        return hashlib.sha256(
            f"{datetime.datetime.utcnow().timestamp()}{settings.SECRET_KEY}".encode()
        ).hexdigest()[:12]

    def _generate_session_id(self) -> str:
        """Generate random session ID"""
        return hashlib.sha256(
            f"{datetime.datetime.utcnow().timestamp()}{settings.SECRET_KEY}".encode()
        ).hexdigest()[:16]

class WebSocketAuthMiddleware:
    """Middleware to authenticate WebSocket connections"""
    
    def __init__(self, app):
        self.app = app
        self.auth_service = AuthService()

    async def __call__(self, scope, receive, send):
        # Get session token from query parameters
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        session_token = query_params.get('session')

        if not session_token:
            return await self.close_connection(send, 'Missing session token')

        # Validate session
        is_valid, document_id = self.auth_service.validate_session(session_token)
        if not is_valid:
            return await self.close_connection(send, 'Invalid session')

        # Add document_id to scope
        scope['document_id'] = document_id
        return await self.app(scope, receive, send)

    async def close_connection(self, send, reason: str):
        """Close WebSocket connection with error message"""
        await send({
            'type': 'websocket.close',
            'code': 4000,
            'reason': reason
        })

# Middleware factory function
def websocket_auth_middleware(app):
    return WebSocketAuthMiddleware(app)