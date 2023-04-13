from __future__ import annotations

from datetime import date
from typing import Any

from django.contrib import messages
from django.forms import BaseForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import BaseFormView, DeleteView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationMemberMixin, OrganizationPermissionMixin
from shiftings.shifts.forms.recurring import RecurringShiftCreateShiftsForm, RecurringShiftForm
from shiftings.shifts.models import RecurringShift
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class RecurringShiftDetailView(OrganizationMemberMixin, DetailView):
    template_name = 'shifts/recurring/shift.html'
    model = RecurringShift
    context_object_name = 'shift'

    def get_title(self) -> str:
        return self.get_object().display

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = date.today()
        context.update({
            'passed_created_shifts': self.object.created_shifts.filter(start__lt=today).order_by('-start')[:5],
            'upcoming_created_shifts': self.object.created_shifts.filter(start__gte=today).order_by('start')[:5]
        })
        return context


class RecurringShiftEditView(OrganizationPermissionMixin, CreateOrUpdateView):
    template_name = 'shifts/recurring/form.html'
    model = RecurringShift
    form_class = RecurringShiftForm
    permission_required = 'organizations.edit_recurring_shifts'

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, 'org_pk')
        return self.get_object().organization

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['organization'] = self.get_organization()
            initial['first_occurrence'] = date.today()
        return initial

    def get_success_url(self) -> str:
        return reverse('recurring_shift', args=[self.object.pk])


class RecurringShiftDeleteView(OrganizationPermissionMixin, DeleteView):
    permission_required = 'organizations.edit_shift_templates'
    model = RecurringShift

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()


class RecurringShiftCreateShiftsView(OrganizationPermissionMixin, SingleObjectMixin, BaseFormView):
    permission_required = 'organizations.edit_shifts'
    form_class = RecurringShiftCreateShiftsForm
    model = RecurringShift

    object: RecurringShift
    create_date: date

    def get(self, request, *args, **kwargs):
        messages.error(self.request, _('Forbidden Method GET'))
        return HttpResponseRedirect(self.object.get_absolute_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def form_valid(self, form: BaseForm) -> HttpResponse:
        self.create_date = form.cleaned_data['create_date']
        self.object.create_shifts(form.cleaned_data['create_date'])
        messages.success(self.request, _('Created Shifts on {}').format(form.cleaned_data['create_date']))
        return super().form_valid(form)

    def form_invalid(self, form: BaseForm) -> HttpResponse:
        messages.error(self.request, _('Error while creating shifts. Invalid Date'))
        return HttpResponseRedirect(self.object.get_absolute_url())

    def get_success_url(self):
        return reverse('overview_day', args=[self.create_date])
