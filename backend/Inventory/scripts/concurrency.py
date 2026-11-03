import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "proto", "generated"))
from concurrent.futures import ThreadPoolExecutor

import grpc

import proto.generated.inventory_pb2 as pb
import proto.generated.inventory_pb2_grpc as pb_grpc

PRODUCT_ID = 1
STARTING_STOCK = 10
CONCURRENT_CALLS = 20

def one_reservation(_):
    # each worker needs its own channel — channels are not thread-safe for heavy use
    with grpc.insecure_channel("localhost:50051") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        try:
            stub.ReserveProduct(
                pb.ReserveProductRequest(id=PRODUCT_ID, quantity=1),
                timeout=5,
            )
            return "ok"
        except grpc.RpcError as e:
            return e.code().name

if __name__ == "__main__":
    # precondition: reset stock to STARTING_STOCK first (see note below)
    with ThreadPoolExecutor(max_workers=CONCURRENT_CALLS) as ex:
        results = list(ex.map(one_reservation, range(CONCURRENT_CALLS)))

    ok   = results.count("ok")
    exh  = results.count("RESOURCE_EXHAUSTED")
    other = [r for r in results if r not in ("ok", "RESOURCE_EXHAUSTED")]

    print(f"ok={ok}  exhausted={exh}  other={other}")
    assert ok == STARTING_STOCK, f"oversold or undersold: {ok} succeeded"
    assert exh == CONCURRENT_CALLS - STARTING_STOCK
    assert not other, f"unexpected statuses: {other}"

    # verify final stock is exactly 0
    with grpc.insecure_channel("localhost:50051") as ch:
        stub = pb_grpc.InventoryServiceStub(ch)
        final = stub.GetProductQuantity(pb.GetProductQuantityRequest(id=PRODUCT_ID))
        print("final stock:", final.stock)
        assert final.stock == 0