from django.contrib.auth import get_user_model
from .models import Users
from django.db import transaction
from django.core.exceptions import ValidationError

# User = get_user_model()


def get_users_by_ids(user_ids: list[int]) -> list[Users]:

    return Users.objects.filter(id__in=user_ids)


def create_user (username , email , password)-> Users:
    try:
        with transaction.atomic():
            user = Users.objects.create_user(
                username = username,
                email = email,
                password = password,
            )

        return user
    except KeyError as e:
        raise ValidationError(f'{str(e)}: this field is required !')
