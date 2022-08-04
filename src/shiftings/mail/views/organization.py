from typing import Any, Optional

from django.db.models import QuerySet

from shiftings.accounts.models import User
from shiftings.mail.forms.mail import OrganizationMailForm
from shiftings.mail.views.mail import BaseMailView
from shiftings.organizations.models import Organization


class OrganizationMailView(BaseMailView):
    form_class = OrganizationMailForm

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
        return self._get_object(Organization, 'pk')

    def get_users(self, form: Optional[OrganizationMailForm] = None) -> QuerySet[User]:
        if form is None:
            return self.get_organization().get_membership_users()
        return self.get_organization().get_membership_users(form.cleaned_data['membership_types'])

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()
