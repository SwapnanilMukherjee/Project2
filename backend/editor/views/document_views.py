# backend/editor/views/document_views.py
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.core.exceptions import PermissionDenied
import json
import uuid

from ..models import Document, DocumentVersion
from ..services.document_service import DocumentService
from ..services.auth_service import verify_passkey

class DocumentListView(View):
    def get(self, request):
        """List all documents accessible to user"""
        documents = Document.objects.all()
        return JsonResponse({
            'documents': [{
                'id': str(doc.id),
                'title': doc.title,
                'created_at': doc.created_at.isoformat(),
                'last_modified': doc.last_modified.isoformat()
            } for doc in documents]
        })

class DocumentCreateView(View):
    def post(self, request):
        """Create new document"""
        try:
            data = json.loads(request.body)
            title = data.get('title', 'Untitled Document')
            passkey = data.get('passkey')

            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=400)

            service = DocumentService()
            document = service.create_document(title, passkey)

            return JsonResponse({
                'id': str(document.id),
                'title': document.title,
                'created_at': document.created_at.isoformat()
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class DocumentDetailView(View):
    def get(self, request, document_id):
        """Get document details and content"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            return JsonResponse({
                'id': str(document.id),
                'title': document.title,
                'content': document.content,
                'version': document.current_version,
                'created_at': document.created_at.isoformat(),
                'last_modified': document.last_modified.isoformat()
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request, document_id):
        """Update document content"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            data = json.loads(request.body)
            changes = data.get('changes', [])

            success = service.apply_changes(document, changes)
            if not success:
                return JsonResponse({'error': 'Failed to apply changes'}, status=400)

            return JsonResponse({
                'version': document.current_version,
                'last_modified': document.last_modified.isoformat()
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class VersionHistoryView(View):
    def get(self, request, document_id):
        """Get document version history"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            history = service.get_version_history(document)
            return JsonResponse({'versions': history})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def post(self, request, document_id):
        """Restore document to specific version"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            data = json.loads(request.body)
            version = data.get('version')

            success = service.restore_version(document, version)
            if not success:
                return JsonResponse({'error': 'Failed to restore version'}, status=400)

            return JsonResponse({
                'version': document.current_version,
                'content': document.content,
                'last_modified': document.last_modified.isoformat()
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class ExportMarkdownView(View):
    def get(self, request, document_id):
        """Export document as Markdown"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            markdown_content = service.export_markdown(document)
            response = HttpResponse(markdown_content, content_type='text/markdown')
            response['Content-Disposition'] = f'attachment; filename="{document.title}.md"'
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class ExportDocxView(View):
    def get(self, request, document_id):
        """Export document as DOCX"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            docx_content = service.export_docx(document)
            response = HttpResponse(docx_content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{document.title}.docx"'
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class ShareLinkView(View):
    def post(self, request, document_id):
        """Create share link for document"""
        try:
            passkey = request.headers.get('X-Document-Passkey')
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            service = DocumentService()
            document = service.get_document(document_id, passkey)
            
            if not document:
                return JsonResponse({'error': 'Document not found or invalid passkey'}, status=404)

            share_id = str(uuid.uuid4())
            # Store share link with expiration if needed

            return JsonResponse({
                'share_url': f'/documents/access/{share_id}/'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class AccessDocumentView(View):
    def post(self, request, share_id):
        """Access document using share link and passkey"""
        try:
            data = json.loads(request.body)
            passkey = data.get('passkey')
            
            if not passkey:
                return JsonResponse({'error': 'Passkey is required'}, status=401)

            # Validate share link and get document
            # Implement share link validation logic here

            return JsonResponse({
                'redirect_url': f'/editor/{document_id}/'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)