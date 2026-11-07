import enum
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.mysql import JSON
from db import Model, Base

class Product(Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, unique=True, nullable=False)

     # one-to-one back-reference
    storage = relationship("Storage", back_populates="product", uselist=False)

    def __init__(self, product_id):
        self.product_id = product_id

    def __repr__(self):
        return f'<product: id={self.id}, product_id={self.product_id}, stock={self.storage.stock}>'

    
class Storage(Model):
    __tablename__ = 'storage'
    id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    stock = Column(Integer, unique=False, nullable=False, default=0)

    product = relationship("Product", back_populates="storage")

    def __init__(self, stock=0):
        self.stock = stock
    
    def __repr__(self):
        return f'<storage: product_id={self.id}, stock={self.stock}>'


class RPCServiceEnum(enum.Enum):
    GET_PRODUCT_BY_Id = 'get_product_by_id'
    GET_PRODUCT_QUANTITY = 'get_product_quantity'
    RESERVE_PRODUCT = 'reserve_product'
    RESERVE_ORDER = 'reserve_order'
    UPDATE_PRODUCT_QUANTITY = 'update_product_quantity'
    CREATE_PRODUCT = 'create_product'

class Request(Base):
    __tablename__ = 'requests_log'
    
    request_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), unique=True)
    user_id = Column(Integer, unique=False, nullable=False)
    
    rpc_service = Column(Enum(RPCServiceEnum), nullable=False, unique=False)
    request_payload = Column(MutableDict.as_mutable(JSON), nullable=True, unique=False)
    
    response_status = Column(Integer, nullable=False, unique=False)
    response_payload = Column(MutableDict.as_mutable(JSON), nullable=True, unique=False)
    
    duration_ms = Column(Integer, nullable=False)
    
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __init__(self, user_id, rpc_service,
                 request_payload, response_status,
                 response_payload, duration_ms):
        self.user_id = user_id
        self.rpc_service = rpc_service
        self.request_payload = request_payload
        self.response_status = response_status
        self.response_payload = response_payload
        self.duration_ms = duration_ms

    def __repr__(self):
        return f'<request({self.request_id}): user:{self.user_id}, rpc_service:{self.rpc_service}, request_payload={self.request_payload}, response_status={self.response_status}, response_payload={self.response_payload}, duration_ms={self.duration_ms}, created_at={self.created_at} >'
