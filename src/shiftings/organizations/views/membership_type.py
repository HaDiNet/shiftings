from typing import Any, Dict

from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipTypeForm
from shiftings.organizations.models import Organization
from shiftings.organizations.models.membership import MembershipType
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class MembershipTypeViewMixin(BaseMixin):
    model = MembershipType
    slug = 'None'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'pk')

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()


class MembershipTypeEditView(MembershipTypeViewMixin, CreateOrUpdateView):
    membership_name: str
    form_class = MembershipTypeForm
    pk_url_kwarg = 'mpk'
    slug = 'mpk'

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['organization'] = self.get_organization()
        return initial


class MembershipTypeRemoveView(MembershipTypeViewMixin, DeleteView, FormMixin):
    pk_url_kwarg = 'mpk'

    def form_valid(self, form: Any) -> HttpResponse:
        result = super().form_valid(form)
        messages.success(self.request, _('Membership removed'))
        return result