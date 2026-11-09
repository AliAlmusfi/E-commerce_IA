from . import services
from .models import Users


def get_users_map(user_ids:list)->dict[int,Users] :

    if not user_ids:
        return {}

    users = services.get_users_by_ids(user_ids=user_ids)
    return {user.id: user for user in users}
