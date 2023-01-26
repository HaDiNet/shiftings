from typing import Any

from django.conf import settings
from django.http import HttpRequest


def debug(request: HttpRequest) -> dict[str, Any]:
    return {'debug': settings.DEBUG}


def feature(request: HttpRequest) -> dict[str, dict[str, bool]]:
    return {
        'feature': settings.FEATURES
    }
