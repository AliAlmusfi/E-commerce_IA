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
    

