import grpc
from db_models import RPCServiceEnum

from .grpc_exceptions import field_missing, field_must_be_positive, \
                            field_must_not_be_zero

from requests_log.services import RequestBuilder

class Validator:
    @staticmethod
    def validate(rpc_service:RPCServiceEnum, request, context:grpc.ServicerContext, request_builder:RequestBuilder):
        try:
            fields = Validator.get_request_fields(rpc_service, request)
            for field in fields.keys():
                if fields[field] is None:
                    field_missing(field, context, request_builder)
            if hasattr(request, "user_id") and request.user_id < 0:
                field_must_be_positive('user_id', context, request_builder)
            if hasattr(request, "product_id") and request.product_id < 0:
                field_must_be_positive('product_id', context, request_builder)
            if hasattr(request, "quantity") and request.quantity <= 0:
                field_must_be_positive('quantity', context, request_builder)
            if hasattr(request, "stock") and request.stock <= 0:
                field_must_be_positive('stock', context, request_builder)
            if hasattr(request, "idempotency_key"):
                Validator.check_for_idempotency_key(request.idempotency_key, context, request_builder)
        
            match(rpc_service):
                case RPCServiceEnum.RESERVE_ORDER:
                    try:
                        request.products[0].product_id
                    except Exception as e:
                        field_missing("products.product_id", context, request_builder)
                    try:
                        request.products[0].quantity
                    except Exception as e:
                        field_missing("products.quantity", context, request_builder)
                    
                    for order_item in request.products:
                        if order_item.product_id < 0:
                            field_must_be_positive('products.product_id', context, request_builder)
                        if order_item.quantity <= 0:
                            field_must_be_positive('products.quantity', context, request_builder)
                case RPCServiceEnum.UPDATE_PRODUCT_QUANTITY:
                    if request.amount == 0:
                        field_must_not_be_zero('amount', context, request_builder)
        except grpc.RpcError:
            raise
        except Exception as e:
            if context.code() is not None:
                raise e
            e.add_note("--Validator.validate()--")
            raise e
    
    @staticmethod
    def check_for_idempotency_key(idempotency_key:str, context:grpc.ServicerContext, request_builder:RequestBuilder):
        return True #TODO
    
    @staticmethod
    def get_request_fields(rpc_service:RPCServiceEnum, request):
        match(rpc_service):
            case RPCServiceEnum.GET_PRODUCT_Stock_BY_Id:
                return {
                        "user_id": request.user_id if hasattr(request, "user_id") else None,
                        "product_id": request.product_id if hasattr(request, "product_id") else None
                    }
            case RPCServiceEnum.RESERVE_PRODUCT:
                return {
                        "user_id": request.user_id if hasattr(request, "user_id") else None,
                        "product_id":request.product_id if hasattr(request, "product_id") else None,
                        "quantity":request.quantity if hasattr(request, "quantity") else None,
                        "idempotency_key":request.idempotency_key if hasattr(request, "idempotency_key") else None
                    }
            case RPCServiceEnum.RESERVE_ORDER:
                return {
                    "user_id": request.user_id if hasattr(request, "user_id") else None,
                    "products": request.products if hasattr(request, "products") else None,
                    "idempotency_key":request.idempotency_key if hasattr(request, "idempotency_key") else None
                }
            case RPCServiceEnum.UPDATE_PRODUCT_QUANTITY:
                return {
                    "user_id": request.user_id if hasattr(request, "user_id") else None,
                    "product_id":request.product_id if hasattr(request, "product_id") else None,
                    "amount":request.amount if hasattr(request, "amount") else None,
                    "idempotency_key":request.idempotency_key if hasattr(request, "idempotency_key") else None
                }
            case RPCServiceEnum.Create_Product_Storage:
                return {
                    "user_id": request.user_id if hasattr(request, "user_id") else None,
                    "product_id":request.product_id if hasattr(request, "product_id") else None,
                    "stock":request.stock if hasattr(request, "stock") else None,
                    "idempotency_key":request.idempotency_key if hasattr(request, "idempotency_key") else None
                }
