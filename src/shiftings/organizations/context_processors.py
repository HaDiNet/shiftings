from dataclasses import dataclass
from typing import Any

from django.http import HttpRequest

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization import OrganizationAdminView
from shiftings.utils.permissions import has_any_permission


@dataclass
class OrganizationPermissionHolder:
    user: User
    organization: Organization
    admin: bool = False

    def __post_init__(self) -> None:
        self.admin = self.organization is not None and self.organization.is_admin(self.user)

    def __getitem__(self, item: Any) -> bool:
        if self.admin:
            return True
        if item == 'see_admin_page':
            return has_any_permission(self.user, OrganizationAdminView.permission_required, self.organization)
        return self.user.has_perm(f'organizations.{item}', self.organization)


def organization_permissions(request: HttpRequest) -> dict[str, OrganizationPermissionHolder]:
    if not hasattr(request, 'organization'):
        return {}
    return {
        'org_perms': OrganizationPermissionHolder(request.user, getattr(request, 'organization'))
    }
