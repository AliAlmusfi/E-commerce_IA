
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.http import Http404
from .exceptions import AppBaseException

def custom_exception_handler(exc, context):
    # 1. Call DRF's default handler first (handles 404, 401, 403, etc.)
    response = exception_handler(exc, context)

    # 2. Handle our custom business exceptions
    if isinstance(exc, AppBaseException):
        return Response({
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }, status=exc.status_code)

    # 3. Handle Django's core ValidationError (often raised in services.py)
    if isinstance(exc, DjangoValidationError):
        return Response({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid data provided.",
                "details": exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    # 4. Handle DRF's built-in errors (like serializer validation)
    if response is not None:
        # Flatten DRF's native error format into ours
        message = "Validation failed."
        if isinstance(response.data, dict) and "detail" in response.data:
            message = response.data["detail"]
        elif isinstance(response.data, list) and len(response.data) > 0:
             message = str(response.data[0])
             
        return Response({
            "success": False,
            "error": {
                "code": "API_ERROR",
                "message": str(message),
                "details": response.data # Keep the original DRF details for debugging
            }
        }, status=response.status_code)

    # 5. Handle unhandled 500 errors (Optional: log these!)
    # If response is None, it's an unhandled Exception (500 Internal Server Error)
    return None # Let Django handle it, or return a generic 500 response if in production