from typing import Any

from shiftings.organizations.models import Organization

user_permissions: dict[int, list[dict[str, Any]]] = {
    2: [{'model': Organization, 'name': 'admin'}]
}
