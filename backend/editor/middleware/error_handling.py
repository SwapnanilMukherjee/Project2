# backend/editor/middleware/error_handling.py
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return JsonResponse({
                'error': 'Permission denied',
                'detail': str(exc)
            }, status=403)
            
        if isinstance(exc, ObjectDoesNotExist):
            return JsonResponse({
                'error': 'Not found',
                'detail': str(exc)
            }, status=404)
            
        # Log unexpected errors
        logger.exception('Unexpected error occurred')
        
        if settings.DEBUG:
            return JsonResponse({
                'error': 'Internal server error',
                'detail': str(exc)
            }, status=500)
        else:
            return JsonResponse({
                'error': 'Internal server error'
            }, status=500)