from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipForm
from shiftings.organizations.models import Membership
from shiftings.organizations.models.activity_log import OrganizationActivityLog
from shiftings.organizations.services import log_organization_activity
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

    def form_valid(self, form):
        response = super().form_valid(form)
        member_name = self.object.user.display if self.object.user else self.object.group.name
        log_organization_activity(
            organization=self.object.organization,
            actor=self.request.user,
            action=OrganizationActivityLog.Action.MEMBERSHIP_ADDED,
            summary=_('Added member: {member}').format(member=member_name),
            metadata={
                'membership_type': self.object.type.name,
                'group_name': self.object.group.name if self.object.group else '',
            },
        )
        return response


class MembershipRemoveView(MembershipSuccessMessageMixin, MembershipViewMixin, UserPassesTestMixin, DeleteView, FormMixin):
    pk_url_kwarg = 'member_pk'

    def test_func(self) -> bool:
        return not self._get_object(Membership, self.pk_url_kwarg).type.admin \
            or self.get_organization().is_admin(self.request.user)

    def form_valid(self, form):
        organization = self.object.organization
        member_name = self.object.user.display if self.object.user else self.object.group.name
        membership_type = self.object.type.name
        response = super().form_valid(form)
        log_organization_activity(
            organization=organization,
            actor=self.request.user,
            action=OrganizationActivityLog.Action.MEMBERSHIP_REMOVED,
            summary=_('Removed member: {member}').format(member=member_name),
            metadata={
                'membership_type': membership_type,
                'group_name': self.object.group.name if self.object.group else '',
            },
        )
        return response
