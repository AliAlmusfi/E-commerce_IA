from sqlalchemy.orm.exc import NoResultFound
import grpc

from db import db_session
from db_models import Product

def get_product_by_id(request, context:grpc.ServicerContext)-> dict:
    product = db_session.get(Product, request.id)
    if product is None:
        context.abort(grpc.StatusCode.NOT_FOUND,
                        f"Product {request.id} not found")
    return {
        "id":product.id,
        "title":product.title,
        "manufacturer":product.manufacturer or "",
        "image":product.image or "",
        "stock":product.stock,
        "price":float(product.price),
    }


def get_product_quantity(request, context:grpc.ServicerContext)-> dict:
    product = db_session.get(Product, request.id)
    if product is None:
        context.abort(grpc.StatusCode.NOT_FOUND,
                        f"Product {request.id} not found")
    return {
        "id":product.id,
        "stock":product.stock
    }


def reserve_product(request, context:grpc.ServicerContext)-> dict:
    if request.quantity <= 0:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                        "quantity must be positive")
    with db_session.begin():
        # stmt = (
        #     update(Product)
        #     .where(Product.id == request.id)
        #     .where(Product.stock >= request.quantity)
        #     .values(stock=Product.stock - request.quantity)
        # )
        # result = db_session.execute(stmt)
        # db_session.commit()
        try:
            product = db_session.query(Product).filter(Product.id == request.id).with_for_update().one()
        except NoResultFound:
            context.abort(grpc.StatusCode.NOT_FOUND,
                            f"Product {request.id} not found")
        if product.stock < request.quantity:
            context.abort(
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                f"Insufficient stock: have {product.stock}, "
                f"need {request.quantity}",
            )
        product.stock = product.stock - request.quantity

        remaining = product.stock
        return {
            "success":True,
            "remaining_stock":remaining,
            "message":"Reserved successfully",
        }
    

def reserve_order(request, context:grpc.ServicerContext)->dict:
    for product in request.products:
        if product.quantity <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                            f"for product {product.id}: quantity must be positive")

    from collections import defaultdict
    product_quantities = defaultdict(int)
    for p in request.products:
        product_quantities[p.id] += p.quantity

    # Sorting the keys (IDs) is the most critical line for deadlock prevention!
    sorted_product_ids = sorted(product_quantities.keys())

    
    with db_session.begin():
        product_items = []
        for p_id in sorted_product_ids:
            requested_qty = product_quantities[p_id]
            try:
                current_product = (
                    db_session.query(Product)
                    .filter(Product.id == p_id)
                    .with_for_update()
                    .one()
                )
            except NoResultFound:
                context.abort(grpc.StatusCode.NOT_FOUND,
                                f"Product {p_id} not found")
            product_items.append({
                "product": current_product,
                "quantity": requested_qty
            })

        
        for product_item in product_items:
            product = product_item["product"]
            qty = product_item["quantity"]
            if not (qty <= product.stock):
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    f"Insufficient stock: have {product.stock}, "
                    f"need {qty}",
                )
            
            product.stock -= qty    
            
        return {
            "success": True
        }
    return {
        "success": False
    }



def add_product_quantity(request, context:grpc.ServicerContext)->dict:
    if request.quantity <= 0:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT,
            f"for product {request.id}: quantity must be positive")

    with db_session.begin():
        try:
            product = (
                db_session.query(Product)
                .filter(Product.id == request.id)
                .one()
            )
        except NoResultFound:
            context.abort(grpc.StatusCode.NOT_FOUND,
                            f"Product {request.id} not found")

        product.stock += request.quantity
        
        return {
            "success": True
        }

    return {
        "success": False
    }
    
    
    
