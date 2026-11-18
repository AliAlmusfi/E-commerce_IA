from .models import Product
from tools.db.db_router import WRITE_DB
class ProductDTO:
    title:str
    manufacturer:str
    description:str
    price:int
    image:str
    
    @classmethod
    def from_model(cls, p: Product) -> "ProductDTO":
        dto = cls()
        dto.title = p.title
        dto.manufacturer = p.manufacturer
        dto.description = p.description
        dto.price = p.price
        dto.image = p.image
        return dto


def get_products_map(product_ids:list[int])->dict[int, ProductDTO]:
    products:list[Product] = Product.objects.using(WRITE_DB).filter(id__in=product_ids)
    return {p.id: ProductDTO.from_model(p) for p in products}






