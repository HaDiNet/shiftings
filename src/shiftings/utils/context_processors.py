from typing import Any
from datetime import date

from django.conf import settings
from django.http import HttpRequest


def debug(request: HttpRequest) -> dict[str, Any]:
    return {'debug': settings.DEBUG}


def feature(request: HttpRequest) -> dict[str, dict[str, bool]]:
    return {
        'feature': settings.FEATURES
    }


def today(request: HttpRequest) -> dict[str, dict[str, date]]:
    return {
        'today': date.today
    }
