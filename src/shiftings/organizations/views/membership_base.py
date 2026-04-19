from abc import ABC

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin


class OrganizationScopedMembershipMixin(OrganizationPermissionMixin, ABC):
    organization_pk_url_kwarg: str = 'org_pk'
    organization_success_view_name: str = 'organization_admin'
    use_organization_absolute_success_url: bool = False

    def get_organization(self) -> Organization:
        return self._get_object(Organization, self.organization_pk_url_kwarg)

    def get_success_url(self) -> str:
        organization = self.get_organization()
        if self.use_organization_absolute_success_url:
            return organization.get_absolute_url()
        return reverse(self.organization_success_view_name, args=[organization.pk])


class MembershipSuccessMessageMixin(ABC):
    success_message = _('Membership removed')

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
