from django.core.cache import cache
from .db_router import set_force_primary

TIME_TO_SYNC_DB = 5 # seconds

class ReadYourWritesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Reset contextvar at the start of every request
        set_force_primary(False)

        user_id = getattr(request.user, "id", None)
        cache_key = f"recent_write_user_{user_id}"

        # If this user wrote data in the last TIME_TO_SYNC_DB seconds, force Primary reads
        if user_id and cache.get(cache_key):
            set_force_primary(True)

        response = self.get_response(request)

        # If this request was a successful write, set the TIME_TO_SYNC_DB-second sticky flag
        if (
            user_id
            and request.method in ("POST", "PUT", "PATCH", "DELETE")
            # and 200 <= response.status_code < 400
        ):
            cache.set(cache_key, True, timeout=TIME_TO_SYNC_DB)

        return response