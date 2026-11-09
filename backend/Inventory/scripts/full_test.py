import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "proto", "generated"))

import uuid
import grpc

import inventory_pb2 as pb
import inventory_pb2_grpc as pb_grpc

PORT = "50051"


PRODUCTS_COUNT = 10
# PRODUCTS_COUNT = 1

def create_product_stock(user_id, product_id, stock):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            response = stub.CreateProductStorage(
                pb.CreateProductStorageRequest(
                    user_id=user_id,
                    product_id=product_id,
                    stock=stock,
                    idempotency_key= str(uuid.uuid4())
                ),
                timeout=5,
            )
            return response
        except grpc.RpcError as e:
            return e

def get_product_stock(user_id, product_id):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            response = stub.GetProductStockById(
                pb.GetProductStockByIdRequest(
                    user_id=user_id,
                    product_id=product_id,
                ),
                timeout=5,
            )
            return response
        except grpc.RpcError as e:
            return e

def reserve_product(user_id, product_id, quantity):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            response = stub.ReserveProduct(
                pb.ReserveProductRequest(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                    idempotency_key=str(uuid.uuid4()),
                ),
                timeout=5,
            )
            return response
        except grpc.RpcError as e:
            return e

def update_product_quantity(user_id, product_id, amount):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            response = stub.UpdateProductQuantity(
                pb.UpdateProductQuantityRequest(
                    user_id=user_id,
                    product_id=product_id,
                    amount=amount,
                    idempotency_key=str(uuid.uuid4()),
                ),
                timeout=5,
            )
            return response
        except grpc.RpcError as e:
            return e

def reserve_order(user_id:int, products:list[dict[str,int]]):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            response = stub.ReserveOrder(
                pb.ReserveOrderRequest(
                    user_id=user_id,
                    products=products,
                    idempotency_key=str(uuid.uuid4()),
                ),
                timeout=5,
            )
            return response
        except grpc.RpcError as e:
            return e


if __name__ == "__main__":
    # create product stock
    products_created:int = 0
    for i in range(PRODUCTS_COUNT):
        result = create_product_stock(
            user_id=i+1,
            product_id=i+1,
            stock=10+i
        )
        if isinstance(result, grpc.RpcError):
            print(f"failed to create product {i+1}\ndetails:\n{result.code()}\n{result.details()}\n")
        else:
            products_created += 1
    # get product stock
    gets_success:int = 0
    for i in range(PRODUCTS_COUNT):
        result = get_product_stock(
            user_id=i+1,
            product_id=i+1
        )
        if isinstance(result, grpc.RpcError):
            print(f"failed to get product {i+1}\ndetails: {result}")
        else:
            gets_success += 1
    # reserve product
    products_reservation_success:int = 0
    for i in range(PRODUCTS_COUNT):
        result = reserve_product(
            user_id=i+1,
            product_id=i+1,
            quantity=1
        )
        if isinstance(result, grpc.RpcError):
            print(f"failed to reserve product {i+1}\ndetails: {result}")
        else:
            products_reservation_success += 1
    # update product quantity
    update_quantity_success:int = 0
    for i in range(PRODUCTS_COUNT):
        result = update_product_quantity(
            user_id=i+1,
            product_id=i+1,
            amount=5
        )
        if isinstance(result, grpc.RpcError):
            print(f"failed to update product:{i+1} stock\ndetails: {result}")
        else:
            update_quantity_success += 1
    # reserve order
    PRODUCT_QTY = 1
    order_reserved_success:int = 0
    for i in range(PRODUCTS_COUNT):
        products = []
        for j in range(PRODUCTS_COUNT):
            products.append({"product_id":j+1, "quantity":PRODUCT_QTY})

        result = reserve_order(
            user_id=i+1,
            products=products
        )
        if isinstance(result, grpc.RpcError):
            print(f"failed to reserve order:{i+1}\ndetails: {result}")
        else:
            order_reserved_success += 1



    print(f"products_created= {products_created}")
    print(f"gets_success= {gets_success}")
    print(f"products_reservation_success= {products_reservation_success}")
    print(f"update_quantity_success= {update_quantity_success}")
    print(f"order_reserved_success= {order_reserved_success}")


    # delete records
    # Get the absolute path of the parent directory (Inventory/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from app import app

    runner = app.test_cli_runner()
    result = runner.invoke(args=["clear-db", "--yes"])

    print(result.exit_code)   # 0 on success
    print(result.output)      # captured stdout, e.g. "✅ Database cleared..."
    if result.exception:
        print(result.exception)




        





