from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db import Model

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