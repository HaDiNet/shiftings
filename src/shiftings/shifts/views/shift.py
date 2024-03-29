from __future__ import annotations

from datetime import date, datetime
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
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.forms.shift import SelectOrgForm, ShiftForm
from shiftings.shifts.forms.template import SelectOrgShiftTemplateGroupForm
from shiftings.shifts.models import Shift, ShiftTemplateGroup
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


class ShiftEditView(OrganizationPermissionMixin, CreateOrUpdateView):
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

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, 'org_pk')
        return self.get_object().organization

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['organization'] = self.get_organization()
            initial['start'] = self.request.GET.get('date')
        return initial

    def get_obj(self) -> Optional[Shift]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, Shift):
            return None
        return obj

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
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()


class ShiftDeleteView(OrganizationPermissionMixin, DeleteView):
    model = Shift
    object: Shift
    permission_required = 'organizations.delete_shifts'
    template_name = 'generic/delete.html'

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.start < datetime.now():
            messages.error(request, _('Unable to delete past shifts.'))
            return self.render_to_response(self.get_context_data())
        self.object.delete()

    def get_success_url(self) -> str:
        return reverse('organization', args=[self.object.organization.pk])
