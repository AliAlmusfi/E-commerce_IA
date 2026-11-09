import grpc
from requests_log.services import RequestBuilder

def exception(e:Exception, context:grpc.ServicerContext, request_builder:RequestBuilder):
    error_msg = str(e) or type(e).__name__ 
    code:grpc.StatusCode = grpc.StatusCode.ABORTED
    
    response_payload = {
        "code": code.name,
        "details": f"Exception: {error_msg}"
    }
    
    request_builder.set_response_status(response_payload['code']).set_response_payload(response_payload)

    context.abort(code ,response_payload['details'])

def product_not_found(product_id:int, context:grpc.ServicerContext, request_builder:RequestBuilder):
    code:grpc.StatusCode = grpc.StatusCode.NOT_FOUND
    
    response_payload = {
        "code": code.name,
        "details": f"Product {product_id} not found"
    }
    
    request_builder.set_response_status(response_payload['code']).set_response_payload(response_payload)

    context.abort(code ,response_payload['details'])

def insufficient_stock(stock:int, quantity:int, context:grpc.ServicerContext, request_builder:RequestBuilder):
    code:grpc.StatusCode = grpc.StatusCode.RESOURCE_EXHAUSTED
    response_payload = {
        "code": code.name,
        "details": f"Insufficient stock: have {stock}, need {quantity}"
    }
    
    request_builder.set_response_status(response_payload['code']).set_response_payload(response_payload)

    context.abort(code, response_payload['details'])

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
    code:grpc.StatusCode = grpc.StatusCode.INVALID_ARGUMENT
    response_payload = {
        "code": code.name,
        "details": f'Invalid Argument Exception: {message}'
    }
    
    request_builder.set_response_status(response_payload['code']).set_response_payload(response_payload)

    context.abort(code, response_payload['details'])

def DB_INTEGRITY_ERROR(message:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
    code:grpc.StatusCode = grpc.StatusCode.ABORTED
    response_payload = {
        "code": code.name,
        "details": message
    }
    
    request_builder.set_response_status(response_payload['code']).set_response_payload(response_payload)

    context.abort(code, response_payload['details'])





