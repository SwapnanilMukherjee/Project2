# backend/editor/consumers/document_consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from ..models import Document, Change
from ..services.merge_service import MergeService
from ..services.auth_service import verify_passkey
from typing import Dict, Any

class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'document_{self.document_id}'
        self.user_id = self.scope.get('user_id', str(id(self)))  # Fallback to connection ID if no user
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send current document state
        try:
            document = await self.get_document()
            await self.send(json.dumps({
                'type': 'document_state',
                'content': document.content,
                'version': document.current_version,
                'active_users': await self.get_active_users()
            }))
        except ObjectDoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove user from active users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_disconnected',
                'user_id': self.user_id
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        handlers = {
            'operation': self.handle_operation,
            'cursor_update': self.handle_cursor_update,
            'sync_request': self.handle_sync_request
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(data)

    async def handle_operation(self, data: Dict[str, Any]):
        """Handle document operations (insert, delete, style, line)"""
        document = await self.get_document()
        
        # Verify operation is valid for current version
        if data['sourceVersion'] != document.current_version:
            await self.send(json.dumps({
                'type': 'sync_required',
                'currentVersion': document.current_version
            }))
            return
        
        # Record change
        change = await self.create_change(data)
        
        # Apply change to document
        merge_service = MergeService()
        success = await database_sync_to_async(merge_service.apply_change)(document, change)
        
        if success:
            # Broadcast change to all users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'document_change',
                    'change': data,
                    'user_id': self.user_id,
                    'new_version': document.current_version
                }
            )

    async def handle_cursor_update(self, data: Dict[str, Any]):
        """Handle cursor position updates"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_position',
                'user_id': self.user_id,
                'position': data['position']
            }
        )

    async def handle_sync_request(self, data: Dict[str, Any]):
        """Handle synchronization requests"""
        document = await self.get_document()
        await self.send(json.dumps({
            'type': 'sync_response',
            'content': document.content,
            'version': document.current_version
        }))

    # Channel layer message handlers
    async def document_change(self, event):
        """Handle document change messages"""
        if event['user_id'] != self.user_id:  # Don't send back to sender
            await self.send(json.dumps({
                'type': 'document_change',
                'change': event['change'],
                'user_id': event['user_id'],
                'new_version': event['new_version']
            }))

    async def cursor_position(self, event):
        """Handle cursor position messages"""
        if event['user_id'] != self.user_id:
            await self.send(json.dumps({
                'type': 'cursor_position',
                'user_id': event['user_id'],
                'position': event['position']
            }))

    async def user_disconnected(self, event):
        """Handle user disconnection messages"""
        await self.send(json.dumps({
            'type': 'user_disconnected',
            'user_id': event['user_id']
        }))

    # Database access methods
    @database_sync_to_async
    def get_document(self) -> Document:
        """Get document from database"""
        return Document.objects.get(id=self.document_id)

    @database_sync_to_async
    def create_change(self, data: Dict[str, Any]) -> Change:
        """Create change record"""
        return Change.objects.create(
            document_id=self.document_id,
            source_version=data['sourceVersion'],
            operation_type=data['operation']['type'],
            position=data['operation']['position'],
            content=data['operation'].get('content'),
            attributes=data['operation'].get('attributes')
        )

    @database_sync_to_async
    def get_active_users(self) -> list:
        """Get list of active users for document"""
        # Implementation depends on how you track active users
        return []