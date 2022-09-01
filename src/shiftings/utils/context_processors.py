from typing import Any

from django.conf import settings


def debug(*args: Any) -> dict[str, Any]:
    return {'debug': settings.DEBUG}
