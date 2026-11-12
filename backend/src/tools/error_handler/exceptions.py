import grpc 
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from ..grpc.client import (
    # InventoryServiceError as GrpcInventoryServiceError, # Aliased to avoid name clash
    InventoryUnavailableError,
    InventoryClientError,
    InventoryServerError
)

class AppBaseException(Exception):
    """Base exception for all business logic errors."""
    def __init__(self, message, code="BAD_REQUEST", status_code=400, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

# Specific exceptions for your modules
class InventoryServiceError(AppBaseException):
    def __init__(self, message="Inventory service unavailable."):
        super().__init__(message, code="INVENTORY_UNAVAILABLE", status_code=503)

class BusinessRuleViolation(AppBaseException):
    def __init__(self, message, details=None):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", status_code=400, details=details)


def custom_exception_handler(exc, context):
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

    # 4. Fallback for unknown exceptions (so you never return an HTML 500 page)
    return Response(
        {"detail": f"Internal Server Error: {str(exc)}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )