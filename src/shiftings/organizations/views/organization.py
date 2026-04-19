from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from shiftings.organizations.forms.membership import MembershipForm
from shiftings.organizations.forms.organization import OrganizationForm
from shiftings.organizations.models import MembershipType, Organization, OrganizationDummyUser
from shiftings.organizations.models.activity_log import OrganizationActivityLog
from shiftings.organizations.services import build_changed_fields, log_organization_activity
from shiftings.organizations.views.organization_base import (
    OrganizationAdminMixin,
    OrganizationMemberMixin,
    OrganizationPermissionMixin,
)
from shiftings.shifts.forms.summary import OrganizationShiftSummaryForm
from shiftings.utils.pagination import get_pagination_context
from shiftings.utils.typing import UserRequest
from shiftings.utils.views.base import BaseLoginMixin, BasePermissionMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateViewWithImageUpload
from shiftings.utils.views.search import SearchableQuerysetMixin


class OrganizationListView(SearchableQuerysetMixin, BasePermissionMixin, ListView):
    template_name = 'organizations/list.html'
    model = Organization
    permission_required = 'organization.admin'
    context_object_name = 'organizations'
    search_fields = ('name',)
    extra_context = {
        'full': True
    }

    def get_queryset(self) -> QuerySet[Organization]:
        return self.apply_search_filter(Organization.objects.all())


class OwnOrganizationListView(SearchableQuerysetMixin, BaseLoginMixin, ListView):
    template_name = 'organizations/list.html'
    model = Organization
    context_object_name = 'organizations'
    search_fields = ('name',)
    extra_context = {
        'full': False
    }

    request: UserRequest

    def get_queryset(self) -> QuerySet[Organization]:
        return self.apply_search_filter(self.request.user.organizations.all())


class OrganizationShiftsView(OrganizationMemberMixin, DetailView):
    template_name = 'organizations/organization_shifts.html'
    object: Organization
    context_object_name = 'organization'
    save_path_in_session = True

    def get_title(self) -> str:
        return _('{org} Overview').format(org=self.get_object())

    def get_organization(self) -> Organization:
        return self.get_object()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = date.today()
        context['shifts'] = get_pagination_context(
            self.request,
            self.object.shifts.filter(start__date__gte=today, end__date__gte=today),
            5,
            'shifts',
        )
        return context


class OrganizationAdminView(OrganizationPermissionMixin, DetailView):
    template_name = 'organizations/organization_admin.html'
    object: Organization
    context_object_name = 'organization'
    require_only_one = True
    save_path_in_session = True
    permission_required = (
        'organizations.see_members', 'organizations.see_statistics', 'organizations.edit_membership_types',
        'organizations.edit_members', 'organizations.edit_recurring_shifts', 'organizations.edit_shift_templates'
    )

    def get_title(self) -> str:
        return _('{org} Administration').format(org=self.get_object())

    def get_organization(self) -> Organization:
        return self.get_object()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        membership_types = []
        for membership_type in self.object.membership_types.all():
            membership_types.append({
                'object': membership_type,
                'members': self.object.members.filter(type=membership_type, user__isnull=False),
                'groups': self.object.members.filter(type=membership_type, group__isnull=False),
                'form': self.create_membership_form(membership_type)
            })
        context['membership_types'] = membership_types
        context['shifts'] = get_pagination_context(
            self.request,
            self.object.shifts.order_by('-start', '-end', 'name').all(),
            25,
            'shifts',
        )
        context['shifts_claimable'] = OrganizationDummyUser.objects.filter(organization=self.object).count() > 0
        return context

    def create_membership_form(self, membership_type: MembershipType):
        return MembershipForm(user=self.request.user, initial={'organization': self.object, 'type': membership_type})


class OrganizationEditView(BasePermissionMixin, CreateOrUpdateViewWithImageUpload):
    model = Organization
    form_class = OrganizationForm

    def has_permission(self):
        if self.is_create():
            return self.request.user.has_perm('organizations.admin')
        return self.request.user.has_perm('organizations.edit_organization', self.get_object())

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def form_valid(self, form):
        tracked_fields = ('name', 'email', 'telephone_number', 'website', 'description', 'confirm_participation_active')
        old_values = None
        if not self.is_create():
            old_values = {
                field_name: getattr(self.get_object(), field_name)
                for field_name in tracked_fields
            }

        response = super().form_valid(form)

        if old_values is not None:
            changed_fields = build_changed_fields(old_values, self.object)
            if changed_fields:
                log_organization_activity(
                    organization=self.object,
                    actor=self.request.user,
                    action=OrganizationActivityLog.Action.ORGANIZATION_UPDATED,
                    summary=_('Organization details updated'),
                    metadata={
                        'target_url': self.object.get_absolute_url(),
                        'target_label': self.object.name,
                        'changed_fields': changed_fields,
                    },
                )
        return response


class OrganizationSettingsView(OrganizationPermissionMixin, DetailView):
    template_name = 'organizations/organization_settings.html'
    object: Organization
    context_object_name = 'organization'
    permission_required = 'organizations.admin'
    save_path_in_session = True

    def get_title(self) -> str:
        return _('{org} Settings').format(org=self.get_object())

    def get_organization(self) -> Organization:
        return self.get_object()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['summary_settings_form'] = OrganizationShiftSummaryForm(instance=self.object.summary_settings)
        return context


class OrganizationActivityLogView(SearchableQuerysetMixin, OrganizationAdminMixin, DetailView):
    template_name = 'organizations/organization_activity_log.html'
    object: Organization
    context_object_name = 'organization'
    save_path_in_session = True
    search_fields = ('summary', 'action', 'actor__display')

    def get_title(self) -> str:
        return _('{org} Activity Log').format(org=self.get_object())

    def get_organization(self) -> Organization:
        return self.get_object()

    def get_activity_log_queryset(self) -> QuerySet[OrganizationActivityLog]:
        base_queryset = self.object.activity_logs.select_related('actor').all()
        search_param = self.get_search_param()
        normalized_search_param = search_param.lower() if search_param else None

        if normalized_search_param and normalized_search_param in ('system', str(_('System')).lower()):
            return base_queryset.filter(actor__isnull=True)

        action_query = Q()
        for action_value, action_label in OrganizationActivityLog.Action.choices:
            if normalized_search_param and normalized_search_param in str(action_label).lower():
                action_query |= Q(action=action_value)

        queryset = self.apply_search_filter(base_queryset)
        if action_query != Q():
            queryset = queryset | base_queryset.filter(action_query)
        return queryset.distinct()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['activity_logs'] = get_pagination_context(
            self.request,
            self.get_activity_log_queryset(),
            25,
            'activity_logs',
        )
        return context
