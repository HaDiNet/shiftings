from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipTypeForm
from shiftings.organizations.models.membership import MembershipType
from shiftings.organizations.views.organization import OrganizationPermissionMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class MembershipTypeViewMixin(OrganizationPermissionMixin):
    model = MembershipType
    permission_required = 'organizations.edit_membership_types'
    pk_url_kwarg = 'member_pk'

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()


class MembershipTypeEditView(MembershipTypeViewMixin, CreateOrUpdateView):
    membership_name: str
    form_class = MembershipTypeForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['is_admin'] = self.get_organization().is_admin(self.request.user)
        return kwargs

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['organization'] = self.get_organization()
        return initial

    def get_success_url(self):
        return reverse('organization_admin', args=[self.get_organization().pk])


class MembershipTypeRemoveView(MembershipTypeViewMixin, UserPassesTestMixin, DeleteView, FormMixin):

    def test_func(self) -> bool:
        membership_type = self._get_object(MembershipType, self.pk_url_kwarg)
        return not (membership_type.admin or membership_type.default)

    def form_valid(self, form: Any) -> HttpResponse:
        result = super().form_valid(form)
        messages.success(self.request, _('Membership removed'))
        return result
