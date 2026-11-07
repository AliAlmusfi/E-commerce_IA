from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import grpc

from db import db_session
from db_models import Product, Storage

from grpc_exceptions import product_not_found, field_must_be_positive, \
                            insufficient_stock, DB_INTEGRITY_ERROR, \
                            exception


def get_product_stock_by_id(request, context:grpc.ServicerContext)-> dict:
    try:
        product = db_session.get(Product, request.product_id)
        if product is None:
            product_not_found(
                request.product_id,
                context
            )
        return {
            "id":request.product_id,
            "stock":product.storage.stock
        }
    except Exception as e:
        exception(e)


def reserve_product(request, context:grpc.ServicerContext)-> dict:
    try:
        with db_session.begin():
            try:
                product = (
                    db_session.query(Product)
                    .filter(Product.product_id == request.product_id)
                    .with_for_update()
                    .one()
                )
            except NoResultFound:
                product_not_found(
                    product_id=request.product_id,
                    context=context
                )
            
            if product.storage.stock < request.quantity:
                insufficient_stock(
                    stock=product.storage.stock,
                    quantity=request.quantity,
                    context=context
                ),
            
            product.storage.stock -= request.quantity

            remaining = product.storage.stock
            return {
                "success":True,
                "remaining_stock":remaining,
                "msg":"Success",
            }
    except Exception as e:
        exception(e)
    

def reserve_order(request, context:grpc.ServicerContext)->dict:
    try:
        for product in request.products:
            if product.quantity <= 0:
                field_must_be_positive(
                    f'product {product.product_id}: quantity',
                    context
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
                        .with_for_update()
                        .one()
                    )
                except NoResultFound:
                    product_not_found(p_id,context)
                
                product_items.append({
                    "product": current_product,
                    "quantity": requested_qty
                })

            
            for product_item in product_items:
                product:Product = product_item["product"]
                qty = product_item["quantity"]
                if not (qty > product.storage.stock):
                    insufficient_stock(
                        stock=product.storage.stock,
                        quantity=qty,
                        context=context
                    )
                
                product.stock -= qty 
                
            return {
                "success": True,
                "msg":"Success",
                "failed_products_ids":[]
            }
        return {
            "success": True,
            "msg":"Success",
            "failed_products_ids":[]
        }
    except Exception as e:
        exception(e)


def update_product_quantity(request, context:grpc.ServicerContext)->dict:
    try:
        with db_session.begin():
            try:
                product = (
                    db_session.query(Product)
                    .filter(Product.product_id == request.product_id)
                    .with_for_update()
                    .one()
                )
            except NoResultFound:
                product_not_found(
                    product_id=request.product_id,
                    context=context
                )

            product.stock += request.quantity
            
            return {
                "success": True,
                "msg": "Success"
            }

        return {
            "success": False,
            "msg":"Failed while increasing stock"
        }
    except Exception as e:
        exception(e)
    
    
def create_product_storage(request, context:grpc.ServicerContext)->dict:
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
                    context
                )

            return {
                "product_id": product.product_id,
                "stock": product.storage.stock
            }
        
        return {
            "product_id": None,
            "stock": None
        }
    except Exception as e:
        exception(e)
    
