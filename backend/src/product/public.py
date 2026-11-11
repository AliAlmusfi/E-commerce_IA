from .models import Product

class ProductDTO:
    title:str
    manufacturer:str
    description:str
    price:int
    image:str


def get_products_map(product_ids:list[int])->dict[int, ProductDTO]:
    products:list[Product] = Product.objects.filter(id__in=product_ids)
    return {p.id: ProductDTO.from_model(p) for p in products}






