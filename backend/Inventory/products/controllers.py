from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import grpc

from db import db_session
from db_models import Product, Storage

from .grpc_exceptions import product_not_found, field_must_be_positive, \
                            insufficient_stock, DB_INTEGRITY_ERROR, \
                            exception

from requests_log.services import RequestBuilder


def get_product_stock_by_id(request, context:grpc.ServicerContext, request_builder:RequestBuilder)-> dict:
    try:
        product = db_session.get(Product, request.product_id)
        if product is None:
            product_not_found(
                request.product_id,
                context,
                request_builder
            )
        return {
            "product_id":request.product_id,
            "stock":product.storage.stock
        }
    except grpc.RpcError as rpc_e:
        raise rpc_e
    except Exception as e:
        if context.code() is not None:
            raise e
        exception(e, context, request_builder)


def reserve_product(request, context:grpc.ServicerContext, request_builder:RequestBuilder)-> dict:
    try:
        with db_session.begin():
            try:
                product = (
                    db_session.query(Product)
                    .filter(Product.product_id == request.product_id)
                    .options(joinedload(Product.storage))
                    .with_for_update()
                    .one()
                )
            except NoResultFound:
                product_not_found(
                    product_id=request.product_id,
                    context=context,
                    request_builder=request_builder
                )
            
            if product.storage.stock < request.quantity:
                insufficient_stock(
                    stock=product.storage.stock,
                    quantity=request.quantity,
                    context=context,
                    request_builder=request_builder
                ),
            
            product.storage.stock -= request.quantity

            remaining = product.storage.stock
            return {
                "success":True,
                "remaining_stock":remaining,
                "msg":"Success",
            }
    except grpc.RpcError as rpc_e:
        raise rpc_e
    except Exception as e:
        if context.code() is not None:
            raise e
        exception(e, context, request_builder)
    

def reserve_order(request, context:grpc.ServicerContext, request_builder:RequestBuilder)->dict:
    try:
        for product in request.products:
            if product.quantity <= 0:
                field_must_be_positive(
                    f'product {product.product_id}: quantity',
                    context,
                    request_builder
                )

        from collections import defaultdict
        product_quantities = defaultdict(int)
        for p in request.products:
            product_quantities[p.product_id] += p.quantity

        # Sorting the keys (IDs) is the most critical line for deadlock prevention!
        sorted_product_ids = sorted(product_quantities.keys())

        
        with db_session.begin():
            product_items = []
            for p_id in sorted_product_ids:
                requested_qty = product_quantities[p_id]
                try:
                    current_product = (
                        db_session.query(Product)
                        .filter(Product.product_id == p_id)
                        .options(joinedload(Product.storage))
                        .with_for_update()
                        .one()
                    )
                except NoResultFound:
                    product_not_found(p_id,context, request_builder)
                
                product_items.append({
                    "product": current_product,
                    "quantity": requested_qty
                })

            
            for product_item in product_items:
                product:Product = product_item["product"]
                qty = product_item["quantity"]
                if (qty > product.storage.stock):
                    insufficient_stock(
                        stock=product.storage.stock,
                        quantity=qty,
                        context=context,
                        request_builder=request_builder
                    )
                
                product.storage.stock -= qty 
                
            return {
                "success": True,
                "msg":"Success",
                "failed_product_ids":[]
            }
        return {
            "success": True,
            "msg":"Success",
            "failed_product_ids":[]
        }
    except grpc.RpcError as rpc_e:
        raise rpc_e
    except Exception as e:
        if context.code() is not None:
            raise e
        exception(e, context, request_builder)


def update_product_quantity(request, context:grpc.ServicerContext, request_builder:RequestBuilder)->dict:
    try:
        with db_session.begin():
            try:
                product = (
                    db_session.query(Product)
                    .filter(Product.product_id == request.product_id)
                    .options(joinedload(Product.storage))
                    .with_for_update()
                    .one()
                )
            except NoResultFound:
                product_not_found(
                    product_id=request.product_id,
                    context=context,
                    request_builder=request_builder
                )

            product.storage.stock += request.amount
            
            return {
                "success": True,
                "msg": "Success"
            }

        return {
            "success": False,
            "msg":"Failed while increasing stock"
        }
    except grpc.RpcError as rpc_e:
        raise rpc_e
    except Exception as e:
        if context.code() is not None:
            raise e
        exception(e, context, request_builder)
    
    
def create_product_storage(request, context:grpc.ServicerContext, request_builder:RequestBuilder)->dict:
    try:
        product = Product(product_id=request.product_id)
        storage = Storage(stock=request.stock)
        product.storage = storage
        with db_session.begin():
            try:
                db_session.add(product)
            except IntegrityError as ie:
                DB_INTEGRITY_ERROR(
                    ie.__str__(),
                    context,
                    request_builder
                )

            return {
                "product_id": product.product_id,
                "stock": product.storage.stock
            }
        
        return {
            "product_id": None,
            "stock": None
        }
    except grpc.RpcError as rpc_e:
        raise rpc_e
    except Exception as e:
        if context.code() is not None:
            raise e
        exception(e, context, request_builder)
    

