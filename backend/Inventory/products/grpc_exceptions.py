import grpc

def exception(e:Exception, context:grpc.ServicerContext):
    context.abort(
        code = grpc.StatusCode.ABORTED,
        details = f"Exception: {str(e)}"
    )

def product_not_found(product_id:int, context:grpc.ServicerContext):
    context.abort(
        code = grpc.StatusCode.NOT_FOUND,
        details = f"Product {product_id} not found"
    )

def insufficient_stock(stock:int, quantity:int, context:grpc.ServicerContext):
    context.abort(
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        f"Insufficient stock: have {stock}, "
        f"need {quantity}",
    )

def field_missing(field:str, context:grpc.ServicerContext):
    INVALID_ARGUMENT_exception(
        f'{field} required and is missing!',
        context
    )

def field_must_be_positive(field:str, context:grpc.ServicerContext):
    INVALID_ARGUMENT_exception(
        f'{field} must be positive',
        context
    )

def field_must_not_be_zero(field:str, context:grpc.ServicerContext):
    INVALID_ARGUMENT_exception(
        f'{field} must NOT be zero',
        context
    )


# -- Helpers --

def INVALID_ARGUMENT_exception(message:str, context:grpc.ServicerContext):
    context.abort(
        code = grpc.StatusCode.INVALID_ARGUMENT,
        details = f'DB Exception: {message}'
    )

def DB_INTEGRITY_ERROR(message:str, context:grpc.ServicerContext):
    context.abort(
        code = grpc.StatusCode.ABORTED,
        details = message
    )