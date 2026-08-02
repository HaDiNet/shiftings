from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView, FormView

from shiftings.organizations.models import Organization
from shiftings.organizations.models.activity_log import OrganizationActivityLog
from shiftings.organizations.services import build_changed_fields, log_organization_activity
from shiftings.organizations.views.organization_base import (
    OrganizationCreateUpdateMixin,
    OrganizationObjectRedirectMixin,
    OrganizationPermissionMixin,
)
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.forms.shift import SelectOrgForm, ShiftForm
from shiftings.shifts.forms.template import SelectOrgShiftTemplateGroupForm
from shiftings.shifts.models import Shift, ShiftTemplateGroup
from shiftings.shifts.views.helpers import shift_datetime_is_past
from shiftings.utils.views.base import BaseLoginMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftDetailView(UserPassesTestMixin, BaseLoginMixin, DetailView):
    template_name = 'shifts/shift.html'
    model = Shift
    context_object_name = 'shift'
    object: Shift

    def get_title(self) -> str:
        return self.get_object().detailed_display

    def test_func(self) -> bool:
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.has_perm('organizations.admin') or self.get_object().can_see_details(self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'add_self_form': AddSelfParticipantForm(self.object, initial={
                'user': self.request.user,
            }),
            'current_date': date.today(),
            'user_is_participant': self.object.is_participant(self.request.user),
            'can_see_participants': self.object.can_see_participants(self.request.user)
        })
        return context


class ShiftOrgSelectView(BaseLoginMixin, FormView):
    form_class = SelectOrgForm
    template_name = 'generic/form_card.html'
    org_id: int
    action_date: date

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form: BaseForm) -> HttpResponse:
        self.org_id = form.cleaned_data['organization'].pk
        self.action_date = form.cleaned_data['action_date']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('shift_create', args=[self.org_id]) + f'?date={self.action_date.strftime("%Y-%m-%d")}'


class ShiftEditView(OrganizationCreateUpdateMixin, OrganizationPermissionMixin, CreateOrUpdateView):
    model = Shift
    form_class = ShiftForm
    permission_required = 'organizations.edit_shifts'
    template_name = 'shifts/create_shift.html'
    title = _('Edit Shift')

    def has_permission(self) -> bool:
        if self.is_create():
            return super().has_permission()
        shift: Shift = self.get_object()
        if shift.shift_type and shift.shift_type.is_system:
            return self.request.user.has_perm('organizations.admin')
        return super().has_permission()

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['start'] = self.request.GET.get('date')
        return initial

    def get_obj(self) -> Optional[Shift]:
        if self.is_create():
            return None
        return self._get_typed_object(Shift)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_create():
            org = self.get_organization()
            context['org_template_form'] = SelectOrgShiftTemplateGroupForm(organization=org,
                                                                           initial={
                                                                               'date_field': self.request.GET.get(
                                                                                   'date',
                                                                                   date.today())
                                                                           })
            context['org_template_success'] = reverse('shift_create_from_template', args=[org.pk])
        return context

    def get_success_url(self) -> str:
        return reverse('shift', args=[self.object.pk])

    def form_valid(self, form):
        is_create = self.is_create()
        old_values = None
        if not is_create:
            shift = self.get_object()
            old_values = {
                'name': shift.name,
                'start': shift.start,
                'end': shift.end,
                'place': shift.place,
                'required_users': shift.required_users,
                'max_users': shift.max_users,
                'shift_type': shift.shift_type_id,
            }

        response = super().form_valid(form)
        if is_create:
            log_organization_activity(
                organization=self.object.organization,
                actor=self.request.user,
                action=OrganizationActivityLog.Action.SHIFT_CREATED,
                summary=_('Shift created: {name}').format(name=self.object.name),
                metadata={
                    'target_url': self.object.get_absolute_url(),
                    'target_label': self.object.detailed_display,
                    'name': self.object.name,
                    'start': str(self.object.start),
                    'end': str(self.object.end),
                },
            )
            return response

        changed_fields = build_changed_fields(old_values, self.object)
        if changed_fields:
            log_organization_activity(
                organization=self.object.organization,
                actor=self.request.user,
                action=OrganizationActivityLog.Action.SHIFT_UPDATED,
                summary=_('Shift updated: {name}').format(name=self.object.name),
                metadata={
                    'target_url': self.object.get_absolute_url(),
                    'target_label': self.object.detailed_display,
                    'changed_fields': changed_fields,
                },
            )
        return response


class CreateShiftFromTemplateGroup(OrganizationPermissionMixin, FormView):
    form_class = SelectOrgShiftTemplateGroupForm
    permission_required = 'organizations.edit_shifts'
    template_name = 'generic/form_card.html'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'org_pk')

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs

    def form_valid(self, form: BaseForm) -> HttpResponse:
        template_group: ShiftTemplateGroup = form.cleaned_data['template_group']
        shifts = template_group.get_shift_objs(form.cleaned_data['date_field'], None, None)
        with transaction.atomic():
            for shift in shifts:
                shift.save()
                for participation_permission in template_group.participation_permissions.all():
                    participation_permission.create_copy_for(shift)
        log_organization_activity(
            organization=self.get_organization(),
            actor=self.request.user,
            action=OrganizationActivityLog.Action.RECURRING_SHIFT_CREATE_SHIFTS,
            summary=_('Created shifts from template group: {group}').format(group=template_group.display),
            metadata={
                'target_url': template_group.get_absolute_url(),
                'target_label': template_group.display,
                'template_group': template_group.display,
                'created_count': len(shifts),
                'create_date': str(form.cleaned_data['date_field']),
            },
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()


class ShiftDeleteView(OrganizationObjectRedirectMixin, OrganizationPermissionMixin, DeleteView):
    model = Shift
    object: Shift
    permission_required = 'organizations.delete_shifts'
    template_name = 'generic/delete.html'
    organization_success_view_name = 'organization'

    def form_valid(self, form):
        if shift_datetime_is_past(self.object):
            messages.error(self.request, _('Unable to delete past shifts.'))
            return self.render_to_response(self.get_context_data())
        organization = self.object.organization
        shift_name = self.object.name
        response = super().form_valid(form)
        log_organization_activity(
            organization=organization,
            actor=self.request.user,
            action=OrganizationActivityLog.Action.SHIFT_REMOVED,
            summary=_('Shift removed: {name}').format(name=shift_name),
            metadata={
                'target_label': shift_name,
                'name': shift_name,
            },
        )
        return response
