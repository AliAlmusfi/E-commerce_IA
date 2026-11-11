from django.contrib.auth import get_user_model
from .models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from tools.error_handler.exceptions import BusinessRuleViolation


# User = get_user_model()


def get_users_by_ids(user_ids: list[int]) -> list[User]:

    return User.objects.filter(id__in=user_ids)


def create_user (username , email , password)-> User:
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username = username,
                email = email,
                password = password,
            )

        return user
    except KeyError as e:
        raise BusinessRuleViolation(f'{str(e)}: this field is required !')
