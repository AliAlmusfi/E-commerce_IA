from .models import Product
from tools.db.db_router import WRITE_DB
class ProductDTO:
    title:str
    manufacturer:str
    description:str
    price:int
    image:str


def get_products_map(product_ids:list[int])->dict[int, ProductDTO]:
    products:list[Product] = Product.objects.using(WRITE_DB).filter(id__in=product_ids)
    return {p.id: ProductDTO.from_model(p) for p in products}






