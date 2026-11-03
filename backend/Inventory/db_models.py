from sqlalchemy import Column, Integer, String, Float
from db import Model


class Product(Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True, nullable=False)
    manufacturer = Column(String(60), unique=False)
    image = Column(String(255), unique=False, nullable=False, default="image.jpg")
    stock = Column(Integer, unique=False, nullable=False, default=0)
    price = Column(Float, unique=False, nullable=False)

    def __init__(self, title, stock, price, image=None, manufacturer=None):
        self.title = title
        self.stock = stock
        self.price = price
        if(image): self.image = image
        self.manufacturer = manufacturer if manufacturer else ""
    
    def __repr__(self):
        return f'<Product {self.title!r}>'