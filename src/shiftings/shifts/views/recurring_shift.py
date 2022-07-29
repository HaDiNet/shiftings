from __future__ import annotations

from typing import Optional

from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.shifts.forms.recurring_shift import RecurringShiftForm
from shiftings.shifts.models import RecurringShift
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class RecurringShiftListView(BaseMixin, ListView):
    template_name = 'shifts/recurring/list.html'
    model = RecurringShift
    context_object_name = 'shifts'


class RecurringShiftDetailView(BaseMixin, DetailView):
    template_name = 'shifts/recurring/shift.html'
    model = RecurringShift
    context_object_name = 'shift'


class RecurringShiftEditView(BaseMixin, CreateOrUpdateView):
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