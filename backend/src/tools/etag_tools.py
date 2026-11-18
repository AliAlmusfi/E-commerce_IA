from django.db.models import Model

def get_etag(Model:Model, name:str, request, pk=None, **kwargs)->str:
    result:str = f'W/{name}/'
    
    if pk:
        # ETag for a single product detail
        result += f'"{pk}-{Model.objects.get(pk=pk).updated_at.timestamp()}"'
        return result
    
    # ETag for the product list (e.g., based on the latest update in the list)
    latest = Model.objects.order_by('-updated_at').first()
    result += f'"list-{latest.updated_at.timestamp() if latest else 0}"'
    return result





