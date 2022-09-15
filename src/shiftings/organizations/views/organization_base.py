from abc import ABC, abstractmethod
from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin

from shiftings.organizations.models import Organization
from shiftings.utils.permissions import has_any_permission
from shiftings.utils.typing import UserRequest
from shiftings.utils.views.base import BaseLoginMixin, BasePermissionMixin


class OrganizationMixin(BaseLoginMixin, ABC):
    model = Organization

    request: UserRequest

    @abstractmethod
    def get_organization(self) -> Organization:
        pass

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['organization'] = self.get_organization()
        return context


class OrganizationMemberMixin(OrganizationMixin, UserPassesTestMixin, ABC):
    def test_func(self) -> bool:
        return self.request.user.has_perm('organizations.admin') or self.get_organization().is_member(self.request.user)


class OrganizationPermissionMixin(BasePermissionMixin, OrganizationMixin, ABC):
    require_only_one: bool = False

    def has_permission(self) -> bool:
        perms = self.get_permission_required()
        if self.require_only_one:
            return has_any_permission(self.request.user, perms, self.get_organization())
        return self.request.user.has_perms(perms, self.get_organization())


class OrganizationAdminMixin(OrganizationMixin, UserPassesTestMixin, ABC):
    def test_func(self) -> bool:
        return self.request.user.has_perm('organizations.admin') or self.get_organization().is_admin(self.request.user)
