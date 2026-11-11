from . import services
from .models import User
from dataclasses import dataclass

@dataclass(frozen=True)
class UserDTO:
    id: int 
    email: str



def get_users_map(user_ids:list)->dict[int,UserDTO] :

    if not user_ids:
        return {}

    users = services.get_users_by_ids(user_ids=user_ids)
    # return {user.id: user for user in users}
    return {
        user.id : UserDTO(
            id = user.id,
            email = user.email
        )
        for user in users
    }
