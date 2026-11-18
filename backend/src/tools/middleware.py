from django.utils.cache import patch_cache_control, patch_vary_headers

class ETagCacheHeadersMiddleware:
    """
    Adds Cache-Control and Vary headers to any response that includes an ETag.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only apply to responses that have an ETag and are successful
        if response.has_header('ETag') and 200 <= response.status_code < 300:
            # Use Django's safe patch utilities so we don't overwrite
            # headers that might have been set elsewhere (e.g., GZipMiddleware)
            patch_cache_control(response, private=True, max_age=0, must_revalidate=True)
            patch_vary_headers(response, ['Accept', 'Authorization'])

        return response