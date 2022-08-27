from typing import Any

from django import template
from django.db.models import Model

from shiftings.accounts.models import User

register = template.Library()


@register.filter
def concat(arg1: Any, arg2: Any) -> str:
    return str(arg1) + str(arg2)


@register.simple_tag()
def has_permission(user: User, permission: str, obj: Model):
    return user.has_perm(permission, obj)
