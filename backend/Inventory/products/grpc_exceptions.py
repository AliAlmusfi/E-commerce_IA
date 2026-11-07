import grpc
from requests_log.services import RequestBuilder

def exception(e:Exception, context:grpc.ServicerContext, request_builder:RequestBuilder):
    response_payload = {
        "code": grpc.StatusCode.ABORTED,
        "details": f"Exception: {str(e)}"
    }
    
    request_builder.set_response_status(response_payload.code).set_response_payload(response_payload)

    context.abort(**response_payload)

def product_not_found(product_id:int, context:grpc.ServicerContext, request_builder:RequestBuilder):
    response_payload = {
        "code": grpc.StatusCode.NOT_FOUND,
        "details": f"Product {product_id} not found"
    }
    
    request_builder.set_response_status(response_payload.code).set_response_payload(response_payload)

    context.abort(**request_builder)

def insufficient_stock(stock:int, quantity:int, context:grpc.ServicerContext, request_builder:RequestBuilder):
    response_payload = {
        "code": grpc.StatusCode.RESOURCE_EXHAUSTED,
        "details": f"Insufficient stock: have {stock}, need {quantity}"
    }
    
    request_builder.set_response_status(response_payload.code).set_response_payload(response_payload)

    context.abort(**request_builder)

def field_missing(field:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
    INVALID_ARGUMENT_exception(
        f'{field} required and is missing!',
        context,
        request_builder
    )

def field_must_be_positive(field:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
    INVALID_ARGUMENT_exception(
        f'{field} must be positive',
        context,
        request_builder
    )

def field_must_not_be_zero(field:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
    INVALID_ARGUMENT_exception(
        f'{field} must NOT be zero',
        context,
        request_builder
    )


# -- Helpers --

def INVALID_ARGUMENT_exception(message:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
    response_payload = {
        "code": grpc.StatusCode.INVALID_ARGUMENT,
        "details": f'DB Exception: {message}'
    }
    
    request_builder.set_response_status(response_payload.code).set_response_payload(response_payload)

    context.abort(**request_builder)

def DB_INTEGRITY_ERROR(message:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
    response_payload = {
        "code": grpc.StatusCode.ABORTED,
        "details": message
    }
    
    request_builder.set_response_status(response_payload.code).set_response_payload(response_payload)

    context.abort(**request_builder)



