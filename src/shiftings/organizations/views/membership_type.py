from typing import Any, Dict

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from shiftings.organizations.forms.membership import MembershipTypeForm
from shiftings.organizations.models.activity_log import OrganizationActivityLog
from shiftings.organizations.models.membership import MembershipType
from shiftings.organizations.services import log_organization_activity
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

    def form_valid(self, form):
        is_create = self.is_create()
        old_name = None
        old_admin = None
        old_default = None
        if not is_create:
            membership_type = self.get_object()
            old_name = membership_type.name
            old_admin = membership_type.admin
            old_default = membership_type.default

        response = super().form_valid(form)
        action = OrganizationActivityLog.Action.MEMBERSHIP_TYPE_CREATED if is_create \
            else OrganizationActivityLog.Action.MEMBERSHIP_TYPE_UPDATED

        metadata = {
            'target_url': reverse(
                'membership_type_edit',
                kwargs={'org_pk': self.object.organization.pk, 'member_pk': self.object.pk},
            ),
            'target_label': self.object.name,
            'name': self.object.name,
            'admin': self.object.admin,
            'default': self.object.default,
        }
        if not is_create:
            metadata['before'] = {
                'name': old_name,
                'admin': old_admin,
                'default': old_default,
            }

        log_organization_activity(
            organization=self.object.organization,
            actor=self.request.user,
            action=action,
            summary=_('Membership type updated: {name}').format(name=self.object.name)
            if not is_create else _('Membership type created: {name}').format(name=self.object.name),
            metadata=metadata,
        )
        return response


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

    def form_valid(self, form):
        organization = self.object.organization
        name = self.object.name
        response = super().form_valid(form)
        log_organization_activity(
            organization=organization,
            actor=self.request.user,
            action=OrganizationActivityLog.Action.MEMBERSHIP_TYPE_REMOVED,
            summary=_('Membership type removed: {name}').format(name=name),
            metadata={},
        )
        return response
