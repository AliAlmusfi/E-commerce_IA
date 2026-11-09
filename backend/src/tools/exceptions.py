import grpc

from rest_framework import status 
from rest_framework.response import Response

from .grpc.client import (InventoryServiceError,
                          InventoryUnavailableError,
                          InventoryClientError,
                          InventoryServerError)

def exception_response(e:Exception):
    return Response(
        data={
            "detail": f"Exception: {str(e)}"
        },
        status=status.HTTP_409_CONFLICT,
        exception=True
    )

def grpc_exception_response(e:InventoryServiceError):
    if isinstance(e, InventoryUnavailableError):
        return Response(
            {
                "detail": "Inventory service unavailable. Try again shortly.",
                "error":  str(e),
                "grpc_code": e.code,
                "grpc_details": e.details
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    if isinstance(e, InventoryClientError) or isinstance(e, InventoryServerError): 
        return Response(
            {
                "detail": "Inventory Client Error.",
                "error":  str(e),
                "grpc_code": e.code,
                "grpc_details": e.details
            },
            status=(
                status.HTTP_503_SERVICE_UNAVAILABLE
                if not (e.code == grpc.StatusCode.RESOURCE_EXHAUSTED)
                else status.HTTP_507_INSUFFICIENT_STORAGE
            ),
        )










