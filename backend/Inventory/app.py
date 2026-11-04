from concurrent import futures

from flask import Flask, jsonify
import grpc

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "proto", "generated"))

import proto.generated.inventory_pb2 as inventory_pb2
import proto.generated.inventory_pb2_grpc as inventory_pb2_grpc

from db import db_session, init_db
from config import Config
from products.controllers import get_product_by_id, \
        get_product_quantity, reserve_product, \
        reserve_order, add_product_quantity

from flask_migrate import Migrate
# Import your custom engine, Base, and a compatibility wrapper
from db import engine, Base

app = Flask(__name__)
app.config.from_object(Config)

# Flask-Migrate needs a wrapper that provides an engine and metadata
class DummyDB:
    def __init__(self, metadata, engine):
        self.metadata = metadata
        self.get_engine = lambda *args, **kwargs: engine

db_wrapper = DummyDB(Base.metadata, engine)
migrate = Migrate(app, db_wrapper)


# gRPC code
class InventoryServiceServicer(inventory_pb2_grpc.InventoryServiceServicer):
    def GetProductById(self, request, context):
        try:
            data:dict = get_product_by_id(request=request, context=context) #controller method that gets the product data dict
            return inventory_pb2.Product(**data)
        finally:
            db_session.remove()
    def GetProductQuantity(self, request, context):
        try:
            data:dict = get_product_quantity(request=request, context=context) #controller method that gets the product quantity data dict
            return inventory_pb2.ProductQuantity(**data)
        finally:
            db_session.remove()
    def ReserveProduct(self, request, context):
        try:
            data:dict = reserve_product(request=request, context=context) #controller method that do reservation and gets the data dict
            return inventory_pb2.ReserveProductResponse(**data)
        finally:
            db_session.remove()
    def ReserveOrder(self, request, context):
        try:
            data:dict = reserve_order(request=request, context=context)
            return inventory_pb2.ReserveOrderResponse(**data)
        finally:
            db_session.remove()
    def addProductQuantity(self, request, context):
        try:
            data:dict = add_product_quantity(request=request, context=context)
            return inventory_pb2.ReserveOrderResponse(**data)
        finally:
            db_session.remove()
    
def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryServiceServicer(), server)
    
    # Listen on a dedicated port for HTTP/2 gRPC traffic
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051...")
    return server

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove() //TODO: must use this in grpc controllers

if __name__ == "__main__":
    init_db()

    # Start the gRPC server first
    grpc_server = start_grpc_server()

    try:
        # Start Flask app on a different port (HTTP/1.1)
        # Note: use_reloader=False prevents Flask from running the main block twice,
        # which would cause address conflicts for the gRPC port.
        app.run(port=5000, debug=True, use_reloader=False)
    finally:
        # Clean up gRPC server resources on shutdown
        grpc_server.stop(0)
