from __future__ import annotations

from typing import Any

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization, OrganizationActivityLog


def build_changed_fields(old_values: dict[str, Any], updated_object: Any) -> dict[str, dict[str, str]]:
    changed_fields: dict[str, dict[str, str]] = {}
    for field_name, old_value in old_values.items():
        new_value = getattr(updated_object, field_name)
        if old_value == new_value:
            continue
        changed_fields[field_name] = {
            'old': '' if old_value is None else str(old_value),
            'new': '' if new_value is None else str(new_value),
        }
    return changed_fields


def log_organization_activity(*,
                              organization: Organization,
                              action: OrganizationActivityLog.Action,
                              summary: str,
                              actor: User | None = None,
                              metadata: dict[str, Any] | None = None) -> None:
    OrganizationActivityLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        summary=summary,
        metadata=metadata or {},
    )
