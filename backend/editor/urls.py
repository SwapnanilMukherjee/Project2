# backend/editor/urls.py
from django.urls import path
from .views import document_views

urlpatterns = [
    # Document management
    path('documents/', document_views.DocumentListView.as_view(), name='document-list'),
    path('documents/create/', document_views.DocumentCreateView.as_view(), name='document-create'),
    path('documents/<uuid:document_id>/', document_views.DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<uuid:document_id>/versions/', document_views.VersionHistoryView.as_view(), name='version-history'),
    
    # Document export
    path('documents/<uuid:document_id>/export/md/', document_views.ExportMarkdownView.as_view(), name='export-markdown'),
    path('documents/<uuid:document_id>/export/docx/', document_views.ExportDocxView.as_view(), name='export-docx'),
    
    # Share and access
    path('documents/<uuid:document_id>/share/', document_views.ShareLinkView.as_view(), name='share-link'),
    path('documents/access/<uuid:share_id>/', document_views.AccessDocumentView.as_view(), name='access-document'),
]