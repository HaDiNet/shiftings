from abc import ABC, abstractmethod
from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse

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

    def organization_reverse(self, view_name: str) -> str:
        return reverse(view_name, args=[self.get_organization().pk])


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


class OrganizationCreateUpdateMixin(ABC):
    organization_create_pk_url_kwarg: str = 'org_pk'
    organization_initial_field: str = 'organization'
    set_organization_initial_on_create_only: bool = True

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, self.organization_create_pk_url_kwarg)
        return self.get_object().organization

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if not self.set_organization_initial_on_create_only or self.is_create():
            initial[self.organization_initial_field] = self.get_organization()
        return initial


class OrganizationObjectRedirectMixin(ABC):
    organization_success_view_name: str = 'organization_admin'

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_success_url(self) -> str:
        return reverse(self.organization_success_view_name, args=[self.get_organization().pk])
