from types import MethodType
from typing import Any, Dict, Optional

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def concat(arg1: Any, arg2: Any) -> str:
    return str(arg1) + str(arg2)