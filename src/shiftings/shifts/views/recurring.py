from __future__ import annotations

from datetime import date
from typing import Any, Optional

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.shifts.forms.recurring import RecurringShiftForm, RecurringShiftCreateForm
from shiftings.shifts.models import RecurringShift, ShiftTemplateGroup
from shiftings.utils.views.base import BaseLoginMixin, BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class RecurringShiftListView(BaseMixin, ListView):
    template_name = 'shifts/recurring/list.html'
    model = RecurringShift
    context_object_name = 'shifts'


class RecurringShiftDetailView(BaseMixin, DetailView):
    template_name = 'shifts/recurring/shift.html'
    model = RecurringShift
    context_object_name = 'shift'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = date.today()
        context.update({
            'passed_created_shifts': self.object.created_shifts.filter(start__lt=today).order_by('-start')[:5],
            'upcoming_created_shifts': self.object.created_shifts.filter(start__gte=today).order_by('-start')[:5]
        })
        return context


class RecurringShiftEditView(BaseLoginMixin, CreateOrUpdateView):
    template_name = 'shifts/recurring/form.html'
    model = RecurringShift
    form_class = RecurringShiftForm

    def get_obj(self) -> Optional[RecurringShift]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, RecurringShift):
            return None
        return obj

    def get_success_url(self) -> str:
        return reverse('recurring_shift', args=[self.object.pk])


class RecurringShiftCreateView(RecurringShiftEditView):
    template_name = 'generic/create_or_update.html'
    form_class = RecurringShiftCreateForm

    object: RecurringShift

    def form_valid(self, form: RecurringShiftCreateForm) -> HttpResponse:
        response = super().form_valid(form)
        template = ShiftTemplateGroup.objects.create(place=form.cleaned_data['place'],
                                                     organization=self.object.organization,
                                                     start_time=form.cleaned_data['start_time'])
        self.object.template = template
        self.object.save()
        return response
