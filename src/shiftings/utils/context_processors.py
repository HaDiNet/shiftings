from typing import Any

from django.conf import settings


def debug(*args: Any) -> dict[str, Any]:
    return {'debug': settings.DEBUG}


def feature(*args: Any) -> dict[str, dict[str, bool]]:
    return {'feature': settings.FEATURES}
