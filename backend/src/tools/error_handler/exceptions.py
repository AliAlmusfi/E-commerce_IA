import grpc 
from django.db.utils import OperationalError, IntegrityError, ProgrammingError
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status

class AppBaseException(Exception):
    """Base exception for all business logic errors."""
    def __init__(self, message, code="BAD_REQUEST", status_code=400, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

# Specific exceptions for your modules
class InventoryServiceError(Exception):
    """Raised when the inventory service is unreachable or returns an error."""
    def __init__(self, message: str, code: grpc.StatusCode | None = None, details: str = ""):
        super().__init__(message)
        self.code = code
        self.details = details

class InventoryUnavailableError(InventoryServiceError):
    """Service unreachable / timed out — safe to retry or surface as 503."""
class InventoryClientError(InventoryServiceError):
    """Server rejected the request (NOT_FOUND, INVALID_ARGUMENT, …) — do not retry."""
class InventoryServerError(InventoryServiceError):
    """Server-side failure (INTERNAL, UNKNOWN) — likely a bug, do not retry."""

class BusinessRuleViolation(AppBaseException):
    def __init__(self, message, details=None):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", status_code=400, details=details)


def custom_exception_handler(exc:Exception, context):
    """
    This function intercepts EVERY exception in your views.
    You no longer need try/except blocks in your views!
    """
    
    # 1. Let DRF handle its own standard exceptions (e.g., 404, 401, Validation)
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    # 2. Handle our custom Domain Exceptions
    if isinstance(exc, AppBaseException):
        return Response(
            {
                "detail": exc.message,
                "code": exc.code,
                "details": exc.details
            },
            status=exc.status_code
        )

    # 3. Handle gRPC Infrastructure Exceptions
    if isinstance(exc, InventoryUnavailableError):
        return Response(
            {
                "detail": "Inventory service unavailable. Try again shortly.",
                "error": str(exc),
                "grpc_code": str(getattr(exc, 'code', None)),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        
    if isinstance(exc, InventoryClientError) or isinstance(exc, InventoryServerError): 
        http_status = (
            status.HTTP_507_INSUFFICIENT_STORAGE 
            if exc.code == grpc.StatusCode.RESOURCE_EXHAUSTED 
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return Response(
            {
                "detail": "Inventory Client Error.",
                "error": str(exc),
                "grpc_code": str(exc.code),
            },
            status=http_status,
        )
    if isinstance(exc, ValidationError):
        return Response(
            {
                "detail": f"Validation Error: {str(exc)}"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if isinstance(exc, IntegrityError):
        return Response(
            {
                "detail": f"Database constraint violation: {str(exc)}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    # 4. Fallback for unknown exceptions (so you never return an HTML 500 page)
    return Response(
        {"detail": f"Exception({str(exc.__class__) or "no-class"}): {str(exc)}"},
        status=status.HTTP_409_CONFLICT
    )