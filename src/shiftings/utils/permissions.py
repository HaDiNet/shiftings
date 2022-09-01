from typing import Iterable, Optional, Union

from django.contrib.auth.models import Permission
from django.db.models import Model

from shiftings.accounts.models import User


def has_any_permission(user: User, permissions: Iterable[Union[str, Permission]], obj: Optional[Model] = None) -> bool:
    for permission in permissions:
        if user.has_perm(permission, obj):
            return True
    return False
