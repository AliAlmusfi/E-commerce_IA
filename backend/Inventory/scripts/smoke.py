import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "proto", "generated"))

import grpc

import inventory_pb2 as pb
import inventory_pb2_grpc as pb_grpc

with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.InventoryServiceStub(ch)

    # happy path — assumes product id=1 has stock >= 5
    print(stub.GetProductById(pb.GetProductByIdRequest(id=1)))
    print(stub.ReserveProduct(pb.ReserveProductRequest(id=1, quantity=3)))
    print(stub.GetProductQuantity(pb.GetProductQuantityRequest(id=1)))

    # NOT_FOUND
    try:
        stub.GetProductById(pb.GetProductByIdRequest(id=99999))
    except grpc.RpcError as e:
        print("missing:", e.code(), e.details())
        assert e.code() == grpc.StatusCode.NOT_FOUND

    # INVALID_ARGUMENT
    try:
        stub.ReserveProduct(pb.ReserveProductRequest(id=1, quantity=0))
    except grpc.RpcError as e:
        print("zero qty:", e.code(), e.details())
        assert e.code() == grpc.StatusCode.INVALID_ARGUMENT

    # RESOURCE_EXHAUSTED
    try:
        stub.ReserveProduct(pb.ReserveProductRequest(id=1, quantity=10_000))
    except grpc.RpcError as e:
        print("oversize:", e.code(), e.details())
        assert e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED