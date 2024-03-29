from typing import Any, Optional

from django.db.models import QuerySet

from shiftings.accounts.models import User
from shiftings.mail.forms.mail import OrganizationMailForm
from shiftings.mail.views.mail import BaseMailView
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin


class OrganizationMailView(OrganizationPermissionMixin, BaseMailView):
    form_class = OrganizationMailForm
    permission_required = 'organization.send_mail'
    pk_url_kwarg = 'org_pk'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs

    def get_replacements(self) -> dict[str, str]:
        replacements = super().get_replacements()
        organization = self.get_organization()
        replacements['name'] = organization.name
        return replacements

    def get_organization(self) -> Organization:
        return self._get_object(Organization, self.pk_url_kwarg)

    def get_users(self, form: Optional[OrganizationMailForm] = None) -> QuerySet[User]:
        if form is None:
            return self.get_organization().get_users_with_membership()
        return self.get_organization().get_users_with_membership(form.cleaned_data['membership_types'])

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()
