import grpc
from db_models import RPCServiceEnum

from .grpc_exceptions import field_missing, field_must_be_positive, \
                            field_must_not_be_zero

class Validator:
    @staticmethod
    def validate(rpc_service:RPCServiceEnum, request, context:grpc.ServicerContext):
        fields = Validator.get_request_fields(rpc_service, request)
        for field in fields.keys():
            if fields[field] is None:
                field_missing(fields[field], context)
        if request.user_id < 0:
            field_must_be_positive('user_id', context)
        if request.product_id and request.product_id < 0:
            field_must_be_positive('product_id', context)
        if request.quantity and request.quantity <= 0:
            field_must_be_positive('quantity', context)
        if request.stock and request.stock <= 0:
            field_must_be_positive('stock', context)
        if request.idempotency_key:
            Validator.check_for_idempotency_key(request.idempotency_key, context)
       
        match(rpc_service):
            case RPCServiceEnum.RESERVE_ORDER:
                for order_item in request.products:
                    if order_item.product_id < 0:
                        field_must_be_positive('products.product_id', context)
                    if order_item.quantity <= 0:
                        field_must_be_positive('quantity', context)
            case RPCServiceEnum.UPDATE_PRODUCT_QUANTITY:
                if request.amount == 0:
                    field_must_not_be_zero('amount', context)
    @staticmethod
    def check_for_idempotency_key(idempotency_key:str, context:grpc.ServicerContext):
        pass #TODO
    
    @staticmethod
    def get_request_fields(rpc_service:RPCServiceEnum, request):
        match(rpc_service):
            case RPCServiceEnum.GET_PRODUCT_Stock_BY_Id:
                return {
                        "user_id": request.user_id,
                        "product_id":request.product_id
                    }
            case RPCServiceEnum.RESERVE_PRODUCT:
                return {
                        "user_id": request.user_id,
                        "product_id":request.product_id,
                        "quantity":request.quantity,
                        "idempotency_key":request.idempotency_key
                    }
            case RPCServiceEnum.RESERVE_ORDER:
                return {
                    "user_id": request.user_id,
                    "products": request.products,
                    "products.product_id": request.products.product_id if (request.products and request.products.product_id) else None,
                    "products.quantity": request.products.quantity if (request.products and request.products.quantity) else None,
                    "idempotency_key":request.idempotency_key
                }
            case RPCServiceEnum.UPDATE_PRODUCT_QUANTITY:
                return {
                    "user_id": request.user_id,
                    "product_id":request.product_id,
                    "amount":request.amount,
                    "idempotency_key":request.idempotency_key
                }
            case RPCServiceEnum.Create_Product_Storage:
                return {
                    "user_id": request.user_id,
                    "product_id":request.product_id,
                    "stock":request.stock,
                    "idempotency_key":request.idempotency_key
                }
