from django.contrib.auth import get_user_model
from .models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from tools.error_handler.exceptions import BusinessRuleViolation
from tools.db.db_router import WRITE_DB

# User = get_user_model()


def get_users_by_ids(user_ids: list[int]) -> list[User]:

    return User.objects.using(WRITE_DB).filter(id__in=user_ids)


def create_user (username , email , password)-> User:
    try:
        with transaction.atomic():
            user = User.objects.using(WRITE_DB).create_user(
                username = username,
                email = email,
                password = password,
            )

        return user
    except KeyError as e:
        raise BusinessRuleViolation(f'{str(e)}: this field is required !')
