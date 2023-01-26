from typing import Any, TypeVar

from django import template

register = template.Library()
T = TypeVar('T')


@register.filter
def concat(arg1: Any, arg2: Any) -> str:
    return str(arg1) + str(arg2)


@register.simple_tag()
def define(obj: T) -> T:
    return obj


@register.simple_tag(takes_context=True)
def active_param(context: dict[str, Any], param_name: str, param_value: Any) -> str:
    if context['request'].GET.get(param_name) == str(param_value):
        return 'btn-success'
    return ''
