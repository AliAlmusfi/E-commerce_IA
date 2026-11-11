import os
import sys
import uuid
import grpc
from concurrent.futures import ThreadPoolExecutor

# Path setup to find generated protos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "proto", "generated"))

import inventory_pb2 as pb
import inventory_pb2_grpc as pb_grpc

PORT = "50051"
STARTING_STOCK = 10
CONCURRENT_CALLS = 20

# We use different product IDs for each test to keep them independent
PRODUCT_ID_RESERVE = 1
PRODUCT_ID_ORDER = 2

# --- Helper RPC Functions ---

def create_product_stock(user_id, product_id, stock):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            response = stub.CreateProductStorage(
                pb.CreateProductStorageRequest(
                    user_id=user_id,
                    product_id=product_id,
                    stock=stock,
                    idempotency_key=str(uuid.uuid4())
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

# --- Concurrency Workers ---

def worker_reserve_product(_):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            stub.ReserveProduct(
                pb.ReserveProductRequest(
                    user_id=1,
                    product_id=PRODUCT_ID_RESERVE,
                    quantity=1,
                    idempotency_key=str(uuid.uuid4())
                ),
                timeout=5,
            )
            return "ok"
        except grpc.RpcError as e:
            return e.code().name

def worker_reserve_order(_):
    with grpc.insecure_channel(f"localhost:{PORT}") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            stub.ReserveOrder(
                pb.ReserveOrderRequest(
                    user_id=1,
                    products=[pb.ReserveOrderItem(
                        product_id=PRODUCT_ID_ORDER,
                        quantity=1
                    )],
                    idempotency_key=str(uuid.uuid4())
                ),
                timeout=5,
            )
            return "ok"
        except grpc.RpcError as e:
            return e.code().name

# --- Test Executions ---

def test_concurrent_reserve_product():
    print("\n=== Testing Concurrent ReserveProduct ===")
    
    # 1. Create product
    print(f"Creating product {PRODUCT_ID_RESERVE} with stock {STARTING_STOCK}...")
    res = create_product_stock(user_id=1, product_id=PRODUCT_ID_RESERVE, stock=STARTING_STOCK)
    if isinstance(res, grpc.RpcError):
        print(f"Failed to create product: {res.details()}")
        return

    # 2. Fire concurrent requests
    print(f"Firing {CONCURRENT_CALLS} concurrent requests...")
    with ThreadPoolExecutor(max_workers=CONCURRENT_CALLS) as ex:
        results = list(ex.map(worker_reserve_product, range(CONCURRENT_CALLS)))

    # 3. Analyze results
    ok = results.count("ok")
    exhausted = results.count("RESOURCE_EXHAUSTED")
    other = [r for r in results if r not in ("ok", "RESOURCE_EXHAUSTED")]

    print(f"Results: ok={ok}, exhausted={exhausted}, other={other}")
    
    # 4. Assertions
    assert ok == STARTING_STOCK, f"Oversold or Undersold: {ok} succeeded (expected {STARTING_STOCK})"
    assert exhausted == CONCURRENT_CALLS - STARTING_STOCK, f"Expected {CONCURRENT_CALLS - STARTING_STOCK} exhausted errors"
    assert not other, f"Unexpected statuses: {other}"

    # 5. Verify final stock
    final = get_product_stock(user_id=1, product_id=PRODUCT_ID_RESERVE)
    if isinstance(final, grpc.RpcError):
        print(f"Failed to get final stock: {final.details()}")
    else:
        print(f"Final stock: {final.stock}")
        assert final.stock == 0, f"Final stock is {final.stock}, expected 0"
    print("✅ ReserveProduct concurrency test passed!")

def test_concurrent_reserve_order():
    print("\n=== Testing Concurrent ReserveOrder ===")
    
    # 1. Create product
    print(f"Creating product {PRODUCT_ID_ORDER} with stock {STARTING_STOCK}...")
    res = create_product_stock(user_id=1, product_id=PRODUCT_ID_ORDER, stock=STARTING_STOCK)
    if isinstance(res, grpc.RpcError):
        print(f"Failed to create product: {res.details()}")
        return

    # 2. Fire concurrent requests
    print(f"Firing {CONCURRENT_CALLS} concurrent requests...")
    with ThreadPoolExecutor(max_workers=CONCURRENT_CALLS) as ex:
        results = list(ex.map(worker_reserve_order, range(CONCURRENT_CALLS)))

    # 3. Analyze results
    ok = results.count("ok")
    exhausted = results.count("RESOURCE_EXHAUSTED")
    other = [r for r in results if r not in ("ok", "RESOURCE_EXHAUSTED")]

    print(f"Results: ok={ok}, exhausted={exhausted}, other={other}")
    
    # 4. Assertions
    assert ok == STARTING_STOCK, f"Oversold or Undersold: {ok} succeeded (expected {STARTING_STOCK})"
    assert exhausted == CONCURRENT_CALLS - STARTING_STOCK, f"Expected {CONCURRENT_CALLS - STARTING_STOCK} exhausted errors"
    assert not other, f"Unexpected statuses: {other}"

    # 5. Verify final stock
    final = get_product_stock(user_id=1, product_id=PRODUCT_ID_ORDER)
    if isinstance(final, grpc.RpcError):
        print(f"Failed to get final stock: {final.details()}")
    else:
        print(f"Final stock: {final.stock}")
        assert final.stock == 0, f"Final stock is {final.stock}, expected 0"
    print("✅ ReserveOrder concurrency test passed!")

# --- Main ---

if __name__ == "__main__":
    try:
        # Run the independent tests
        test_concurrent_reserve_product()
        test_concurrent_reserve_order()
        print("\n🎉 All concurrency tests passed successfully!")
        
    finally:
        # Delete records (exact same logic as full_test.py)
        print("\n=== Cleaning up database ===")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            
        try:
            from app import app

            runner = app.test_cli_runner()
            result = runner.invoke(args=["clear-db", "--yes"])

            print(f"Exit code: {result.exit_code}")
            print(result.output.strip())
            if result.exception:
                print(f"Cleanup error: {result.exception}")
        except Exception as e:
            print(f"Failed to run cleanup script: {e}")