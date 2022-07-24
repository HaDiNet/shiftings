from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from django.db.models import QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.shifts.forms.shift import ShiftForm
from shiftings.shifts.models import Shift
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftListView(BaseMixin, ListView):
    template_name = 'shifts/list.html'
    model = Shift
    context_object_name = 'shifts'


class FutureShiftListView(BaseMixin, ListView):
    template_name = 'shifts/list.html'
    model = Shift
    context_object_name = 'shifts'

    def get_queryset(self) -> QuerySet:
        return Shift.objects.filter(start__gte=datetime.now())


class ShiftDetailView(BaseMixin, DetailView):
    template_name = 'shifts/shift.html'
    model = Shift
    context_object_name = 'shift'


class ShiftEditView(BaseMixin, CreateOrUpdateView):
    model = Shift
    form_class = ShiftForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({'initial': {'start': self.request.GET.get('date')}})
        return kwargs

    def get_obj(self) -> Optional[Shift]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, Shift):
            return None
        return obj

    def get_success_url(self) -> str:
        return reverse('shift', args=[self.object.pk])
