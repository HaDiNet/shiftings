from __future__ import annotations

from typing import Type, TYPE_CHECKING, TypeVar

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from shiftings.accounts.models import User

T = TypeVar('T')


class UserRequest(HttpRequest):
    user: User


def check_not_none(obj: T | None) -> T:
    if obj is None:
        raise AttributeError(_('Value is not supposed to be None.'))
    return obj


def ensure_type(obj: T, obj_type: Type[T]) -> T:
    if obj is None:
        raise AttributeError(f'The Object was None, should be of Type {obj_type}.')
    if not isinstance(obj, obj_type):
        raise AttributeError(f'The Object was of type {type(obj)}, should be of Type {obj_type}.')
    return obj
