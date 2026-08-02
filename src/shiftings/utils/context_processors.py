from datetime import date
from typing import Any

from django.conf import settings
from django.http import HttpRequest


def debug(request: HttpRequest) -> dict[str, Any]:
    return {'debug': settings.DEBUG}


def feature(request: HttpRequest) -> dict[str, dict[str, bool]]:
    return {
        'feature': settings.FEATURES
    }


def today(request: HttpRequest) -> dict[str, date]:
    return {
        'today': date.today()
    }


def theme(request: HttpRequest) -> dict[str, str]:
    if request.user.is_authenticated and hasattr(request.user, 'theme_preference'):
        return {
            'theme_preference': request.user.theme_preference
        }
    return {
        'theme_preference': 'auto'
    }
