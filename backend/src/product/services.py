from .models import Product

from tools.grpc.client import InventoryClient
from tools.error_handler.exceptions import BusinessRuleViolation , InventoryServiceError
from tools.db.db_router import WRITE_DB
from tools.etag_tools import get_etag
from tools.caching import explicit_invalidate_cache


def create_product(user_id, data:dict)->Product:
    # data must be validated by serializer
    product = None
    stock = data.pop('stock')

    product = Product.objects.db_manager(WRITE_DB).create(**data)
    if product is None:
        raise Exception("can't create product !")


    # create storage in Inventory service
    try:
        print("\n\nIN TRY\n")
        client = InventoryClient()
        response = client.create_product_storage(
            user_id=user_id,
            product_id=product.id,
            stock=stock
        )
        print("END OF TRY\n") 
    except InventoryServiceError as e:
        print("IN EXCEPT\n")
        print(f"EXCEPT EXCEPTION<{e.__class__}> ({str(e)})\n")
        delete_product(product)
        print("AFTER DELETE\n\n")
        raise
        

    if not response['product_id']:
        delete_product(product)
        raise BusinessRuleViolation("can't create product storage (but can create product with no storage)!")

    return product

def delete_product(product:Product):
    # Product.objects.filter(id=id).delete()
    product.delete(using=WRITE_DB)

def patch_product(id, user_id, data:dict)->Product:
    product = Product.objects.db_manager(WRITE_DB).get(id)
 
    if product is None:
        raise BusinessRuleViolation(f"Product {id} is not found!", code="NOT_FOUND", status_code=404)

    if data.get('title'):
        product.title = data.get('title')
    if data.get('description'):
        product.description = data.get('description')
    if data.get('manufacturer'):
        product.manufacturer = data.get('manufacturer')
    if data.get('price'):
        product.price = data.get('price')
    if data.get('image'):
        product.image = data.get('image')

    product.save(using=WRITE_DB)

    return product


def get_stock(id, user_id)-> int:
    try:
        client = InventoryClient()
        stock = client.get_product_stock(
            user_id=int(user_id),
            product_id=int(id)
        )
        return stock
    except InventoryServiceError:
        raise
        
def update_stock(id, user_id, amount)->bool:
    try:
        explicit_invalidate_cache('product', id)
        client = InventoryClient()
        response = client.update_product_quantity(
            user_id=int(user_id),
            product_id=int(id),
            amount=int(amount)
        )
        return response['success'] or False
    except InventoryServiceError:
        raise


def get_product_etag(request, pk=None, **kwargs)->str:
    return get_etag(Product, "product", request, pk, **kwargs)