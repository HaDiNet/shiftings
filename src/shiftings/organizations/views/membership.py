from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipForm
from shiftings.organizations.models import Membership, Organization
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class MembershipViewMixin(BaseMixin):
    model = Membership
    slug = 'None'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'pk')

    def get_success_url(self):
        return reverse('organization_admin', args=[self.get_organization().pk])


class MembershipAddView(MembershipViewMixin, CreateOrUpdateView):
    membership_name: str
    form_class = MembershipForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        organization = self.get_organization()
        initial['organization'] = organization
        initial['type'] = organization.default_membership_type
        return initial


class MembershipRemoveView(MembershipViewMixin, DeleteView, FormMixin):
    pk_url_kwarg = 'mpk'

    def form_valid(self, form: Any) -> HttpResponse:
        result = super().form_valid(form)
        messages.success(self.request, _('Membership removed'))
        return result
