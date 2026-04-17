from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipForm
from shiftings.organizations.models import Membership
from shiftings.organizations.views.membership_base import MembershipSuccessMessageMixin, OrganizationScopedMembershipMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class MembershipViewMixin(OrganizationScopedMembershipMixin):
    model = Membership
    pk_url_kwarg = 'None'
    permission_required = 'organizations.edit_members'


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


class MembershipRemoveView(MembershipSuccessMessageMixin, MembershipViewMixin, UserPassesTestMixin, DeleteView, FormMixin):
    pk_url_kwarg = 'member_pk'

    def test_func(self) -> bool:
        return not self._get_object(Membership, self.pk_url_kwarg).type.admin \
            or self.get_organization().is_admin(self.request.user)
