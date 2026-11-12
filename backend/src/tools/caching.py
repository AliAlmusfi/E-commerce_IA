import hashlib
from urllib.parse import urlencode

from django.core.cache import cache

from rest_framework.response import Response

def get_cached_response(cache_key)-> Response | None:
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return Response(cached_data)
    
    return None

def do_cache(cache_key, data, timeout=60 * 30)-> None:
    cache.set(
        key=cache_key,
        value=data,
        timeout=timeout
    )

def get_cache_key(module, endpoint, wildcard_pk=None, user_id=None, is_staff=None, params_hash=None, page=None)-> str:
    result = f"api:{module}:{endpoint}"
    
    if wildcard_pk is not None:
        result += f":wildcard_pk_{wildcard_pk}"
    
    if user_id is not None:
        result += f":user_{user_id}"
    
    if is_staff is not None:
        result += f":staff_{is_staff}"
    
    if params_hash is not None:
        params = [(k, v) for k, v in params_hash if k != 'page']
        if params:
            hash_val  = hashlib.md5(urlencode(sorted([(k, v) for k, v in params]), doseq=True)).hexdigest()
            result += f":params_hash_{hash_val}"
    
    if page is not None:
        result += f":page_{page}"
    
    return result



def invalidate_cache(module, sender, instance, **kwargs):
    
    cache.delete_pattern(f"api:{module}:list:*")
    cache.delete_pattern(f"api:{module}:retrieve:wildcard_pk_{instance.pk}*")
