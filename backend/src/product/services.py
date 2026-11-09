from .models import Product

from tools.grpc.client import InventoryClient, InventoryServiceError


def create_product(user_id, data:dict)->Product:
    # data must be validated by serializer
    product = None
    stock = data.pop('stock')

    product = Product.objects.create(**data)
    if product is None:
        raise Exception("can't create product !")


    # create storage in Inventory service
    try:
        client = InventoryClient()
        response = client.create_product_storage(
            user_id=user_id,
            product_id=product.id,
            stock=stock
        )
    except InventoryServiceError:
        delete_product(product.id)
        raise

    if not response['product_id']:
        delete_product(product.id)
        raise Exception("can't create product storage (but can create product with no storage)!")

    return product

def delete_product(id:int):
    Product.objects.filter(id=id).delete()

def patch_product(id, user_id, data:dict)->Product:
    product = Product.objects.get(id)
    if product is None:
        raise Exception(f"product {id} is not found!")

    if data['title']:
        product.title = data['title']
    if data['description']:
        product.description = data['description']
    if data['manufacturer']:
        product.manufacturer = data['manufacturer']
    if data['price']:
        product.price = data['price']
    if data['image']:
        product.image = data['image']

    product.save()

    return product


def get_stock(id, user_id)-> int:
    try:
        client = InventoryClient()
        stock = client.get_product_stock(
            user_id=user_id,
            product_id=id
        )
        return stock
    except InventoryServiceError:
        raise
        
def update_stock(id, user_id, amount)->bool:
    try:
        client = InventoryClient()
        response = client.update_product_quantity(
            user_id=user_id,
            product_id=id,
            amount=amount
        )
        if not response['success']: return False
        return response['success']
    except InventoryServiceError:
        raise
