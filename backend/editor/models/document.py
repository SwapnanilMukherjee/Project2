# backend/editor/models/document.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    current_version = models.FloatField(default=1.0)
    passkey = models.CharField(max_length=64)  # Hashed passkey
    
    # JSON field to store the piece table state
    content = models.JSONField(default=dict)
    
    def initialize_content(self):
        """Initialize empty document content structure"""
        self.content = {
            'originalBuffer': '',
            'addBuffer': '',
            'pieces': [],
            'styles': [],
            'lines': []
        }
        self.save()
    
    def get_piece_table(self):
        """Return PieceTable instance from stored content"""
        return PieceTable.from_json(self.content)
    
    def update_content(self, piece_table):
        """Update content from PieceTable instance"""
        self.content = piece_table.to_json()
        self.save()

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.JSONField()  # Stores complete piece table state
    
    class Meta:
        unique_together = ('document', 'version')
        ordering = ['-version']

class Change(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='changes')
    timestamp = models.DateTimeField(auto_now_add=True)
    source_version = models.FloatField()
    operation_type = models.CharField(max_length=20)  # insert, delete, style, line
    position = models.IntegerField()
    content = models.TextField(null=True, blank=True)
    attributes = models.JSONField(null=True, blank=True)