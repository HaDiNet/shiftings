from typing import Any, Dict

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipTypeForm
from shiftings.organizations.models.membership import MembershipType
from shiftings.organizations.views.membership_base import (
    MembershipSuccessMessageMixin,
    OrganizationScopedMembershipMixin,
)
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class MembershipTypeViewMixin(OrganizationScopedMembershipMixin):
    model = MembershipType
    permission_required = 'organizations.edit_membership_types'
    pk_url_kwarg = 'member_pk'
    use_organization_absolute_success_url = True


class MembershipTypeEditView(MembershipTypeViewMixin, CreateOrUpdateView):
    membership_name: str
    form_class = MembershipTypeForm
    use_organization_absolute_success_url = False
    organization_success_view_name = 'organization_admin'

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['is_admin'] = self.get_organization().is_admin(self.request.user)
        return kwargs

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['organization'] = self.get_organization()
        return initial


class MembershipTypeRemoveView(
    MembershipSuccessMessageMixin,
    MembershipTypeViewMixin,
    UserPassesTestMixin,
    DeleteView,
    FormMixin,
):
    def test_func(self) -> bool:
        membership_type = self._get_object(MembershipType, self.pk_url_kwarg)
        return not (membership_type.admin or membership_type.default)
