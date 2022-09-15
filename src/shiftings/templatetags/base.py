from typing import Any, Optional, TypeVar, Union

from django import template
from django.db.models import Model

from shiftings.accounts.models import User
from shiftings.utils.typing import UserRequest

register = template.Library()
T = TypeVar('T')


@register.filter
def concat(arg1: Any, arg2: Any) -> str:
    return str(arg1) + str(arg2)


@register.simple_tag()
def has_permission(user_or_request: Union[User, UserRequest], permission: str, obj: Optional[Model] = None):
    user = user_or_request if isinstance(user_or_request, User) else user_or_request.user
    return user.has_perm(permission, obj)


@register.simple_tag()
def define(obj: T) -> T:
    return obj
